# Cancamusa

ISO: https://software-download.microsoft.com/download/pr/Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.ISO
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
