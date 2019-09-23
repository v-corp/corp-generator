# Almacenar todo en la carpeta hostname
$hostname = hostname
mkdir $hostname
$Usuario = [Environment]::UserName
# Configuracion de red
Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Select-Object Description, SettingID, MACAddress, DNSDomain, DNSHostName, Index, InterfaceIndex, IPAddress | ConvertTo-Json > $hostname'\net.json'
# Discos instalados
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, DriveType, FreeSpace, Size, VolumeName | ConvertTo-Json > $hostname'\disk.json'
# Cuentas de usuario en el equipo, tanto locales como de dominio
Get-WmiObject -ComputerName $hostname -Class Win32_UserAccount -Filter | Select-Object LocalAccount,AccountType,Name, PSComputerName, Description,SID, Lockout, PasswordChangeable, PasswordExpires, PasswordRequired  | ConvertTo-Json > $hostname'\accounts.json'
# Estructura de directorios de l carpeta home del usuario
tree $HOME /f > $hostname/$Usuario'-tree.log'
# Información de la BIOS
Get-WmiObject Win32_Bios | ConvertTo-Json > > $hostname/'bios.json'