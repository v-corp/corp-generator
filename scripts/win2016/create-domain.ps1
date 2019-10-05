param (
    [String] $ip,
    [String] $domain = "windomain.local",
    [String] $password = "cancamusa",
    [String] $dns1 = "8.8.8.8",
    [String] $dns2 = "8.8.4.4"
)

$subnet = $ip -replace "\.\d+$", ""

if ((gwmi win32_computersystem).partofdomain -eq $false) {
    #Todavia no está en dominio
    Write-Host 'Installing RSAT tools'
    Import-Module ServerManager
    Add-WindowsFeature RSAT-AD-PowerShell,RSAT-AD-AdminCenter

    Write-Host 'Creating domain controller'

    # Eliminar política de contraseña robusta
    secedit /export /cfg C:\secpol.cfg
    (gc C:\secpol.cfg).replace("PasswordComplexity = 1", "PasswordComplexity = 0") | Out-File C:\secpol.cfg
    secedit /configure /db C:\Windows\security\local.sdb /cfg C:\secpol.cfg /areas SECURITYPOLICY
    rm -force C:\secpol.cfg -confirm:$false

    # Poner contraseña de administrador
    $computerName = $env:COMPUTERNAME
    $adminPassword = $password
    $adminUser = [ADSI] "WinNT://$computerName/Administrator,User"
    $adminUser.SetPassword($adminPassword)

    $PlainPassword = $password # "P@ssw0rd"
    $SecurePassword = $PlainPassword | ConvertTo-SecureString -AsPlainText -Force

    # Windows Server 2012 R2
    Install-WindowsFeature AD-domain-services
    Import-Module ADDSDeployment
    Install-ADDSForest `
        -SafeModeAdministratorPassword $SecurePassword `
        -CreateDnsDelegation:$false `
        -DatabasePath "C:\Windows\NTDS" `
        -DomainMode "Win2016" `
        -DomainName "windomain.local" `
        -DomainNetbiosName "WINDOMAIN" `
        -ForestMode "Win2016" `
        -InstallDns:$true `
        -LogPath "C:\Windows\NTDS" `
        -NoRebootOnCompletion:$true `
        -SysvolPath "C:\Windows\SYSVOL" `
        -Force:$true

    $newDNSServers = $dns1, $dns2
    $adapters = Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.IPAddress -And ($_.IPAddress).StartsWith($subnet) }
    if ($adapters) {
        Write-Host Setting DNS
        $adapters | ForEach-Object {$_.SetDNSServerSearchOrder($newDNSServers)}
    }
}