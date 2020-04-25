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

$domain = "minaf.es"
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
New-ADOrganizationalUnit -name "AISLADOS" -path "CN=Computers,DC=MINAF,DC=ES"
New-ADOrganizationalUnit -name "Domain Controllers"

#Groups:
New-ADGroup -Name "Users" -SamAccountName "Users" -GroupCategory Security -GroupScope Global -DisplayName "Users" -Path "DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "Propietarios del creador de directivas de grupo" -SamAccountName "Propietarios del creador de directivas de grupo" -GroupCategory Security -GroupScope Global -DisplayName "Propietarios del creador de directivas de grupo" -Path "CN=Users,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "Admins. del dominio" -SamAccountName "Admins. del dominio" -GroupCategory Security -GroupScope Global -DisplayName "Admins. del dominio" -Path "CN=Users,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "Administradores de empresas" -SamAccountName "Administradores de empresas" -GroupCategory Security -GroupScope Global -DisplayName "Administradores de empresas" -Path "CN=Users,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "Administradores de esquema" -SamAccountName "Administradores de esquema" -GroupCategory Security -GroupScope Global -DisplayName "Administradores de esquema" -Path "CN=Users,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "Administradores" -SamAccountName "Administradores" -GroupCategory Security -GroupScope Global -DisplayName "Administradores" -Path "CN=Builtin,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "Invitados" -SamAccountName "Invitados" -GroupCategory Security -GroupScope Global -DisplayName "Invitados" -Path "CN=Builtin,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "System Managed Accounts Group" -SamAccountName "System Managed Accounts Group" -GroupCategory Security -GroupScope Global -DisplayName "System Managed Accounts Group" -Path "CN=Builtin,DC=MINAF,DC=ES" -Description ""
New-ADGroup -Name "PlanSecretoFelicidad" -SamAccountName "PlanSecretoFelicidad" -GroupCategory Security -GroupScope Global -DisplayName "PlanSecretoFelicidad" -Path "CN=Users,DC=MINAF,DC=ES" -Description ""

#Users:
New-ADUser -Name "Administrador" -GivenName "" -Surname "" -SamAccountName "Administrador" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "Administrador" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "X'4375656e746120696e746567726164612070617261206c612061646d696e69737472616369c3b36e2064656c2065717569706f206f20646f6d696e696f'" -AccountPassword (convertto-securestring "_nb3%z7vct" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=Propietarios del creador de directivas de grupo,CN=Users,DC=MINAF,DC=ES" -Member "CN=Administrador,CN=Users,DC=MINAF,DC=ES"
Add-ADGroupMember -Identity "CN=Admins. del dominio,CN=Users,DC=MINAF,DC=ES" -Member "CN=Administrador,CN=Users,DC=MINAF,DC=ES"
Add-ADGroupMember -Identity "CN=Administradores de empresas,CN=Users,DC=MINAF,DC=ES" -Member "CN=Administrador,CN=Users,DC=MINAF,DC=ES"
Add-ADGroupMember -Identity "CN=Administradores de esquema,CN=Users,DC=MINAF,DC=ES" -Member "CN=Administrador,CN=Users,DC=MINAF,DC=ES"
Add-ADGroupMember -Identity "CN=Administradores,CN=Builtin,DC=MINAF,DC=ES" -Member "CN=Administrador,CN=Users,DC=MINAF,DC=ES"

New-ADUser -Name "Invitado" -GivenName "" -Surname "" -SamAccountName "Invitado" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "Invitado" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "Cuenta integrada para el acceso como invitado al equipo o dominio" -AccountPassword (convertto-securestring "uhpn5q99xn" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=Invitados,CN=Builtin,DC=MINAF,DC=ES" -Member "CN=Invitado,CN=Users,DC=MINAF,DC=ES"

New-ADUser -Name "DefaultAccount" -GivenName "" -Surname "" -SamAccountName "DefaultAccount" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "DefaultAccount" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "Cuenta de usuario administrada por el sistema." -AccountPassword (convertto-securestring "7v2rgp6hct" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=System Managed Accounts Group,CN=Builtin,DC=MINAF,DC=ES" -Member "CN=DefaultAccount,CN=Users,DC=MINAF,DC=ES"

New-ADUser -Name "krbtgt" -GivenName "" -Surname "" -SamAccountName "krbtgt" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "krbtgt" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "X'4375656e746120646520736572766963696f2064652063656e74726f2064652064697374726962756369c3b36e20646520636c61766573'" -AccountPassword (convertto-securestring "i85q56uhch" -AsPlainText -Force)

New-ADUser -Name "SuperAdmin" -GivenName "SuperAdmin" -Surname "" -SamAccountName "dom.adm" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "SuperAdmin" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "" -AccountPassword (convertto-securestring "0dqyfouybd" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=Admins. del dominio,CN=Users,DC=MINAF,DC=ES" -Member "CN=SuperAdmin,CN=Users,DC=MINAF,DC=ES"

New-ADUser -Name "Pepe Contento" -GivenName "Pepe" -Surname "Contento" -SamAccountName "pepe.contento" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "Pepe Contento" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "" -AccountPassword (convertto-securestring "6b2km%xjeo" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=PlanSecretoFelicidad,CN=Users,DC=MINAF,DC=ES" -Member "CN=Pepe Contento,CN=Users,DC=MINAF,DC=ES"

New-ADUser -Name "Maria Feliz" -GivenName "Maria" -Surname "Feliz" -SamAccountName "maria.feliz" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "Maria Feliz" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "" -AccountPassword (convertto-securestring "9v48e4ufjm" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=PlanSecretoFelicidad,CN=Users,DC=MINAF,DC=ES" -Member "CN=Maria Feliz,CN=Users,DC=MINAF,DC=ES"

New-ADUser -Name "Salvador Bendito" -GivenName "Salvador" -Surname "Bendito" -SamAccountName "salvador.bendito" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "Salvador Bendito" -Department "" -Path "CN=Users,DC=MINAF,DC=ES" -Description "" -AccountPassword (convertto-securestring "ai_lhgd_mv" -AsPlainText -Force)
Add-ADGroupMember -Identity "CN=Admins. del dominio,CN=Users,DC=MINAF,DC=ES" -Member "CN=Salvador Bendito,CN=Users,DC=MINAF,DC=ES"
