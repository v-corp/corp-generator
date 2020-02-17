# Almacenar todo en la carpeta hostname
$hostname = hostname
mkdir $hostname
$Usuario = [Environment]::UserName
# Configuracion de red
Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Select-Object Description, SettingID, MACAddress, DNSDomain, DNSHostName, Index, InterfaceIndex, IPAddress | ConvertTo-Json | Out-File -Encoding UTF8 $hostname'\net.json'
# Discos instalados
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, DriveType, FreeSpace, Size, VolumeName | ConvertTo-Json | Out-File -Encoding UTF8 $hostname'\disk.json'
# Cuentas de usuario en el equipo, tanto locales como de dominio
Get-WmiObject -ComputerName $hostname -Class Win32_UserAccount | Select-Object LocalAccount,AccountType,Name, PSComputerName, Description,SID, Lockout, PasswordChangeable, PasswordExpires, PasswordRequired  | ConvertTo-Json | Out-File -Encoding UTF8 $hostname'\accounts.json'
# Estructura de directorios de l carpeta home del usuario
tree $HOME /f > $hostname/$Usuario'-tree.log'
# Información de la BIOS
Get-WmiObject Win32_Bios | ConvertTo-Json | Out-File -Encoding UTF8 $hostname/'bios.json'
[System.Environment]::OSVersion.Version | ConvertTo-JSON | Out-File -Encoding UTF8 $hostname'\version.json'
# Información del antivirus
Get-WmiObject -Namespace "root\SecurityCenter2" -Query "Select * From  AntiVirusProduct" | ConvertTo-Json | Out-File -Encoding UTF8 $hostname'\av.json'
# Programas instalados
Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | ConvertTo-Json | Out-File -Encoding UTF8 $hostname'\programs.json'
# Directorios sobre Program Files
dir C:\Program Files > $hostname/$Usuario'-PFx64.log'
dir C:\Program Files (x86) > $hostname/$Usuario'-PFx86.log'