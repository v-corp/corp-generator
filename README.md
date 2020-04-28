# Cancamusa

```
apt-get install wimtools
```

## Generate Windows Images and Vagrant Boxes
ISO: https://software-download.microsoft.com/download/pr/Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.ISO
ISO: http://download.microsoft.com/download/7/6/9/769D6905-3BC7-4CF0-B3BD-785EC88767AF/14393.0.161119-1705.RS1_REFRESH_SERVER_EVAL_X64FRE_ES-ES.ISO
ISO: https://software-download.microsoft.com/download/pr/18363.418.191007-0143.19h2_release_svc_refresh_CLIENTENTERPRISEEVAL_OEMRET_x64FRE_es-es.iso

```
usage: corp-generator.py [-h] [--iso ISO_PATH] [--iso-md5 ISO_MD5]
                         [--name MACHINE_NAME] [--username USERNAME]
                         [--password PASSWORD] [--virtio VIRTIO]
                         [--win-type WIN_TYPE] [--win-image WIN_IMAGE]
                         [--clean-cache] [--no-pswd] [--kvm]
                         [--version VERSION]

Create a complete Windows based security LAB with malware sandbox ofuscation
maximized using KVM. 7zip and DSIM are required in order to autodetect windows
image types if they are not provided.

optional arguments:
  -h, --help            show this help message and exit
  --iso ISO_PATH        selects the iso with which generate the villager
                        template
  --iso-md5 ISO_MD5     Checksum for the ISO. If not provided will be
                        autocalculated
  --name MACHINE_NAME   sets the name for this machine
  --username USERNAME   sets the name of the user in this machine
  --password PASSWORD   sets the password for the user in this machine
  --virtio VIRTIO       version of the virtio drivers to use. Set to NONE to
                        skip this step.
  --win-type WIN_TYPE   version of windows: win10, win2016, win7, win2008,
                        win2012, win2019.If it's not provided, then DSIM will
                        be used to autodetect the version
  --win-image WIN_IMAGE
                        select windows image to install. It can be selected
                        using a number (image index inside install.wim) or the
                        image name. Ej: 1, 2, 3, 4, 'Windows 10 Home','Windows
                        10 Pro','Windows Server 2016 SERVERSTANDARD'
  --clean-cache         Clean the cache folder (It stores virtio versions and
                        install.WIM files).
  --no-pswd             Allow the usage of simple passwords.
  --kvm                 Allow running QEMU using KVM.
  --version VERSION     Version control of the generated templates.
```

Generate the packer and vagrant templates (example machine name windows-123):
`python3 bin/corp-generator.py --iso win7_ent_x64.iso --name windows-123 --username vagrant --password vagrant --no-pswd --kvm`

After generating the templates you need to build the image with packer.
`packer build packer-windows-123.json`

Note: The vagrant commands must be executed where the box is residing.
Add the generated box to the vagrant list
`vagrant box add windows-123 ./windows-123-1.box`
And then run it with:
`vagrant up windows-123 --provider libvirt`

Then connect to the box with RDP:
`vagrant rdp`
or using programms like Remmina.


### How it works

```
$ sudo python3 bin/corp-generator.py --iso ~/Descargas/14393.0.161119-1705.RS1_REFRESH_SERVER_EVAL_X64FRE_ES-ES.ISO --name test-cancamusa --username paco --win-image 1
Current directory: /home/paco/test/corp-generator
Cache directory: /home/paco/test/corp-generator
Calculating MD5 of ISO image...
MD5 = 920a6148d79075d261c10c5cb906d39c
Checking Windows Image Type...
mount: /mnt/920a6148d79075d261c10c5cb906d39c: ATENCIÓN: el dispositivo está protegido contra escritura; se monta como sólo lectura.
Select a Windows Image:
1 - Windows Server 2016 SERVERSTANDARDCORE
2 - Windows Server 2016 SERVERSTANDARD
3 - Windows Server 2016 SERVERDATACENTERCORE
4 - Windows Server 2016 SERVERDATACENTER
2
WIN_IMAGE=Windows Server 2016 SERVERSTANDARD
Downloading Virtio drivers 0.1.172-1 from:
https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.172-1/virtio-win-0.1.172.iso
100% [..................................................] 371818496 / 371818496
Created answer file: answer/test-cancamusa/Autounattend.xml
Created packer file: packer-test-cancamusa.json
Created vagrant file: vagrant-files/vagrant-test-cancamusa.template
Copy script: firewall-disable.bat
Copy script: enable-winrm.ps1
Copy script: install-bginfo.ps1
Copy script: create-domain.ps1
Copy script: vagrant-ssh.bat
Copy script: unlimited-password-expiration.bat
Copy script: firewall-open-smb.bat
Copy script: execution-policy-unrestricted.bat
Copy script: zz-start-sshd.cmd
Copy script: install-cygwin-sshd.bat
Copy script: vagrant.bat
Copy script: install-iis.ps1
Copy script: fixnetwork.ps1
Copy script: copy-scripts.bat
Copy script: vagrant.pub
Copy script: firewall-open-ping.bat
Copy script: install-cygwin-sshd.sh
Copy script: disable-hibernate.bat
Copy script: disable-firewall.bat
Copy script: disablewinupdate.bat
Copy script: firewall-open-rdp.bat
Copy script: provision.ps1
Copy script: fill-ad.ps1
Copy script: disable-winrm.ps1
Copy script: install-chocolatey.ps1
Copy script: install-git.ps1
Copy script: join-domain.ps1
Copy script: enable-rdp.bat
Copy script: winrm-allow-basic.bat
Copy script: setup-net.ps1
Copy script: bginfo.bgi
Copy script: install-adfs2.ps1
Copy script: install-winrm.cmd
Copy script: install-rol.ps1
Copy script: uac-disable.bat
Created .gitignore
```


## Install and fill a domain

`python3 generate_domain.py domain.csv --out init_domain.ps1`

```powershell
param (
    [String] $ip,
    [String] $password = "cancamusa",
    [String] $dns1 = "8.8.8.8",
    [String] $dns2 = "8.8.4.4",
    [String] $domainNetBios = "corp"
)
if ((gwmi win32_computersystem).partofdomain -eq $true) {
    Exit
}

$domain = "mydomain.com"
#Todavia no está en dominio
Write-Host 'Installing RSAT tools'
Import-Module ServerManager
Add-WindowsFeature RSAT-AD-PowerShell,RSAT-AD-AdminCenter

# Eliminar política de contraseña robusta
secedit /export /cfg C:\secpol.cfg
(gc C:\secpol.cfg).replace("PasswordComplexity = 1", "PasswordComplexity = 0") | Out-File C:\secpol.cfg
secedit /configure /db C:\Windows\security\local.sdb /cfg C:\secpol.cfg /areas SECURITYPOLICY
rm -force C:\secpol.cfg -confirm:$false

$PlainPassword = $password
$SecurePassword = $PlainPassword | ConvertTo-SecureString -AsPlainText -Force


# Instalar Forest y convertir la maquina en un DC
Install-WindowsFeature AD-domain-services
Import-Module ADDSDeployment
Install-ADDSForest -SafeModeAdministratorPassword $SecurePassword `
    -CreateDnsDelegation:$false `
    -DatabasePath "C:\Windows\NTDS" `
    -DomainMode "7" `
    -DomainName $domain `
    -DomainNetbiosName $domainNetBios `
    -ForestMode "7" `
    -InstallDns:$true `
    -LogPath "C:\Windows\NTDS" `
    -NoRebootOnCompletion:$true `
    -SysvolPath "C:\Windows\SYSVOL" `
    -Force:$true

$newDNSServers = $dns1, $dns2
$adapters = Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.DefaultIPGateway -ne $null -and $_.DefaultIPGateway[0].StartsWith($subnet) }
if ($adapters) {
    Write-Host Setting DNS
    $adapters | ForEach-Object {$_.SetDNSServerSearchOrder($newDNSServers)}
}#OrganizationalUnits:
New-ADOrganizationalUnit -name "Computers"
New-ADOrganizationalUnit -name "Domain Controllers"
#...
#...

#Groups:
New-ADGroup -Name "Users" -SamAccountName "Users" -GroupCategory Security -GroupScope Global -DisplayName "Users" -Path "DC=MYDOMAIN,DC=COM" -Description ""
#...
#...

#Users:
New-ADUser -Name "Administrador" -GivenName "" -Surname "" -SamAccountName "Administrador" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "Administrador" -Department "" -Path "CN=Users,DC=MYDOMAIN,DC=COM" -Description "ADMIN" -AccountPassword (convertto-securestring "_nb3%z7vct" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=Propietarios del creador de directivas de grupo,CN=Users,DC=MYDOMAIN,DC=COM" -Member "CN=Administrador,CN=Users,DC=MYDOMAIN,DC=COM"
#...
#...

```



### Problems with vagrant and proxmox

Use DEB packet from: [https://www.vagrantup.com/downloads.html](https://www.vagrantup.com/downloads.html)

apt install ./vagrant_2.2.7_x86_64.deb

```
vagrant plugin install vagrant-libvirt
Installing the 'vagrant-libvirt' plugin. This can take a few minutes...
Fetching: formatador-0.2.5.gem (100%)
Fetching: excon-0.73.0.gem (100%)
Fetching: fog-core-1.43.0.gem (100%)
Fetching: mini_portile2-2.4.0.gem (100%)
Fetching: nokogiri-1.10.9.gem (100%)
Building native extensions.  This could take a while...
Fetching: fog-json-1.2.0.gem (100%)
Fetching: fog-xml-0.1.3.gem (100%)
Fetching: ruby-libvirt-0.7.1.gem (100%)
Building native extensions.  This could take a while...
Fetching: fog-libvirt-0.7.0.gem (100%)
Fetching: vagrant-libvirt-0.0.45.gem (100%)
Installed the plugin 'vagrant-libvirt (0.0.45)'!
```
vagrant up --provider libvirt



### BIOS clonning

Using the "--bios" option we can now build a custom SeaBIOS that emulates a real one with data from WMI:

```json
}
    ...
    "Manufacturer":  "American Megatrends Inc.",
    "Name":  "5.6.5",
    "OtherTargetOS":  null,
    "PrimaryBIOS":  true,
    "ReleaseDate":  "20150901000000.000000+000",
    "SerialNumber":  "To be filled by O.E.M.",
    "SMBIOSBIOSVersion":  "5.6.5",
    "SMBIOSMajorVersion":  2,
    "SMBIOSMinorVersion":  8,
    "SMBIOSPresent":  true,
    "SoftwareElementID":  "5.6.5",
    "SoftwareElementState":  3,
    "Status":  "OK",
    "SystemBiosMajorVersion":  5,
    "SystemBiosMinorVersion":  6,
    "TargetOperatingSystem":  0,
    "Version":  "ALASKA - 1072009"
}
```