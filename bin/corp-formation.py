# Unir archivos de configuración de Vagrant en uno solo
import json
import os
import codecs
import csv


def generate_script_domain(domain, actual_domain=""):
    domain_creation = []
    if '_type' in domain:
        actual_type = domain['_type']
    for dc_key in domain:
        if dc_key == '_type':
            # Nothing
            pass
        elif '_type' in domain[dc_key]:
            key_type = domain[dc_key]['_type']
            if key_type == 'DC':
                domain_creation.extend(generate_script_domain(
                    domain[dc_key], "DC="+dc_key+ ("," if len(actual_domain) > 0 else "") + actual_domain))
            elif key_type == 'CN':
                domain_creation.append(
                    'NEW-ADOrganizationalUnit -name "' + dc_key + '" -path "' + actual_domain + '"')
                domain_creation.extend(generate_script_domain(
                    domain[dc_key], "OU="+dc_key + "," + actual_domain))
    return domain_creation


def host_info_from_directory(scanPath):
    host = {}
    with open(os.path.join(scanPath, 'disk.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        data = json.loads(decoded_data)
        host['disk'] = []
        for disk in data:
            if disk['DriveType'] == 3:
                # Is HDD/SDD disk
                disco = {}
                disco['deviceId'] = disk['DeviceID'].replace(':', '')
                disco['volumeName'] = disk['VolumeName']
                disco['size'] = disk['Size']
                disco['freeSpace'] = disk['FreeSpace']
                host['disk'].append(disco)

    with open(os.path.join(scanPath, 'bios.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        bios = json.loads(decoded_data)
        customBios = {}
        if bios['Manufacturer']:
            customBios['Manufacturer'] = bios['Manufacturer']
            customBios['Version'] = bios['Version']
            customBios['Caption'] = bios['Caption']
            customBios['Description'] = bios['Description']
            customBios['ReleaseDate'] = bios['ReleaseDate']
            customBios['Name'] = bios['Name']
            customBios['SoftwareElementID'] = bios['SoftwareElementID']
            customBios['SoftwareElementState'] = bios['SoftwareElementState']
            customBios['SystemBiosMajorVersion'] = bios['SystemBiosMajorVersion']
            customBios['SystemBiosMinorVersion'] = bios['SystemBiosMinorVersion']
            customBios['SMBIOSMajorVersion'] = bios['SMBIOSMajorVersion']
            customBios['SMBIOSMinorVersion'] = bios['SMBIOSMinorVersion']
            customBios['EmbeddedControllerMajorVersion'] = bios['EmbeddedControllerMajorVersion']
            customBios['EmbeddedControllerMinorVersion'] = bios['EmbeddedControllerMinorVersion']
            customBios['PSComputerName'] = bios['PSComputerName']
            host['ComputerName'] = bios['PSComputerName']
            print(customBios)
            host['bios'] = customBios
            # Build seabios with custom configuration

    with open(os.path.join(scanPath, 'net.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        netFile = json.loads(decoded_data)
        customIface = []
        for netIface in netFile:
            if netIface['MACAddress']:
                customIf = {}
                customIf['Description'] = netIface['Description']
                customIf['SettingID'] = netIface['SettingID']
                customIf['MACAddress'] = netIface['MACAddress']
                customIf['DNSDomain'] = netIface['DNSDomain']
                customIf['DNSHostName'] = netIface['DNSHostName']
                customIf['Index'] = netIface['Index']
                customIf['InterfaceIndex'] = netIface['InterfaceIndex']
                customIf['IPAddress'] = netIface['IPAddress']
                customIface.append(customIf)
        host['net'] = customIface

    with open(os.path.join(scanPath, 'version.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        vFile = json.loads(decoded_data)
        customIf = {}
        if vFile['Major']:
            customIf['Major'] = vFile['Major']
            customIf['Minor'] = vFile['Minor']
            customIf['Build'] = vFile['Build']
            customIf['Revision'] = vFile['Revision']
            customIf['MajorRevision'] = vFile['MajorRevision']
            customIf['MinorRevision'] = vFile['MinorRevision']
        host['so'] = customIf
    # Local accounts
    with open(os.path.join(scanPath, 'accounts.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        accountsJSON = json.loads(decoded_data)
        accountList = []
        for account in accountsJSON:
            if account['Name']:
                acc = {}
                acc['Name'] = account['Name']
                acc['LocalAccount'] = account['LocalAccount']
                acc['AccountType'] = account['AccountType']
                acc['PSComputerName'] = account['PSComputerName']
                acc['Description'] = account['Description']
                acc['SID'] = account['SID']
                acc['Lockout'] = account['Lockout']
                acc['PasswordChangeable'] = account['PasswordChangeable']
                acc['PasswordExpires'] = account['PasswordExpires']
                acc['PasswordRequired'] = account['PasswordRequired']
                accountList.append(acc)
        host['accounts'] = accountList
    # Lista de programas instalados
    with open(os.path.join(scanPath, 'programs.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        vFile = json.loads(decoded_data)
        programs = []
        if vFile['DisplayName']:
            programs['DisplayName'] = vFile['DisplayName']
            programs['DisplayVersion'] = vFile['DisplayVersion']
            programs['Publisher'] = vFile['Publisher']
            programs['InstallDate'] = vFile['InstallDate']
        host['programs'] = programs
    return host


"""
    TODO:
    Usar un CSV que tenga en cuenta los paquetes para x86 o x64, incluya un regex para el nombre del programa
    y así la funcion es facilmente extensible.
"""


def extract_chocolatey_package(displayName, x86=False):
    displayName = displayName.lower()
    if 'firefox' in displayName:
        return 'firefox'
    if 'thunderbird' in displayName:
        return 'thunderbird'
    if 'notepad++' in displayName:
        return 'notepadplusplus.install'
    if 'git' in displayName:
        return 'git.install'
    if 'putty' in displayName:
        return 'putty.install'
    if 'node' in displayName and 'js' in displayName:
        return 'nodejs.install'
    if 'openssh' in displayName:
        return 'openssh'
    if 'skype' in displayName:
        return 'skype'
    if 'ccleaner' in displayName:
        return 'ccleaner'
    if 'malwarebytes' in displayName:
        return 'malwarebytes'
    if 'filezilla' in displayName:
        return 'filezilla'
    if 'gimp' in displayName:
        return 'gimp'
    if 'atom' in displayName:
        return 'atom'
    if 'ruby' in displayName:
        return 'ruby'
    if 'winscp' in displayName:
        return 'winscp'
    if 'aws' in displayName:
        return 'awscli'
    if 'keepass' in displayName:
        return 'keepass.install'
    if 'chromium' in displayName:
        return 'chromium'
    if 'sql' in displayName and 'server' in displayName and 'management' in displayName:
        return 'sql-server-management-studio'
    if '.net' in displayName and 'Microsoft' in displayName:
        return 'dotnetfx'
    if 'visual' in displayName and 'studio' in displayName:
        if 'code' in displayName:
            return 'vscode'
        if '2015' in displayName:
            return 'vcredist2015'
        if '2017' in displayName:
            return 'visualstudio2017buildtools'
        if '2010' in displayName:
            return 'vcredist2010'
    if 'ink' in displayName and 'scape' in displayName:
        return 'inkscape'
    if 'team' in displayName and 'viewer' in displayName:
        return 'teamviewer'
    if 'sysinternals' in displayName:
        return 'sysinternals'
    if 'flash' in displayName:
        return 'flashplayerplugin'
    if 'java' in displayName:
        if 'runtime' in displayName or 'jre' in displayName:
            if ' 6.' in displayName:
                return 'jre6'
            if ' 7.' in displayName:
                return 'javaruntime-tiger'
            else:
                return 'jre8'
        if 'se' in displayName:
            if ' 11.' in displayName:
                return 'jdk11'
            else:
                return 'jdk8'
    if 'spotify' in displayName:
        return 'spotify'
    if 'dropbox' in displayName:
        return 'dropbox'
    if 'virtualbox' in displayName:
        return 'virtualbox'
    if 'opera' in displayName:
        return 'opera'
    if 'vim' in displayName:
        return 'vim'
    if 'sublime' in displayName:
        return 'sublime'
    if 'audacity' in displayName:
        return 'audacity'
    if 'maven' in displayName:
        return 'maven'
    if 'kaspersky' in displayName:
        return 'kvrt'
    if 'cpu-z' in displayName:
        return 'cpu-z.install'
    if 'microsoft' in displayName and 'teams' in displayName:
        return 'microsoft-teams'
    if 'slack' in displayName:
        return 'slack'
    if 'pgadmin' in displayName:
        return 'pgadmin3'
    if 'postman' in displayName:
        return 'postman'
    if 'openvpn' in displayName:
        return 'openvpn'
    if 'sql' in displayName and 'lite' in displayName:
        return 'sqlite'
    if 'tortoise' in displayName and 'svn' in displayName:
        return 'tortoisesvn'
    if 'greenshot' in displayName:
        return 'greenshot'
    if 'whatsapp' in displayName:
        return 'whatsapp'
    if 'soapui' in displayName:
        return 'soapui'
    if 'gitkraken' in displayName:
        return 'gitkraken'
    if 'blender' in displayName:
        return 'blender'
    if 'arduino' in displayName:
        return 'arduino'
    if 'unity' in displayName:
        return 'unity'
    if 'sketchup' in displayName:
        return 'sketchup'
    if 'github' in displayName:
        return 'github-desktop'
    if 'avg' in displayName:
        return 'avgantivirusfree'
    if 'discord' in displayName:
        return 'discord'
    if 'brave' in displayName:
        return 'brave'
    if 'clone' in displayName and 'virtual' in displayName:
        return 'virtualclonedrive'
    if 'nvidia' in displayName:
        return 'nvidia-display-driver'
    if 'foxit' in displayName:
        return 'foxitreader'
    if 'evernote' in displayName:
        return 'evernote'
    if 'avast' in displayName:
        return 'avastfreeantivirus'
    if 'qbittorrent' in displayName:
        return 'qbittorrent'
    if 'android' in displayName:
        return 'androidstudio'
    if 'eclipse' in displayName:
        return 'eclipse'
    if 'tomcat' in displayName:
        return 'tomcat'
    if 'powerbi' in displayName:
        return 'powerbi'
    if 'postgresql' in displayName:
        return 'postgresql'
    if 'mysql' in displayName:
        if 'workbench' in displayName:
            return 'mysql.workbench'
        if 'community' in displayName:
            return 'mysql'
    if 'adobe' in displayName:
        if 'acrobat' in displayName:
            return 'adobereader'
    if 'office' in displayName:
        if 'libre' in displayName:
            return 'libreoffice-fresh'
        if '365' in displayName:
            return 'office365business'
    if 'vlc' in displayName:
        return 'vlc'
    if 'google' in displayName and 'drive' in displayName:
        return 'googledrive'
    if 'winrar' in displayName:
        return 'winrar'
    if '7' in displayName and 'zip' in displayName:
        return '7zip'
    if 'telegram' in displayName:
        return 'telegram'
    if 'chrome' in displayName:
        if 'remote' in displayName:
            return 'chrome-remote-desktop-chrome'
        else:
            return 'googlechrome'
    return None


"""
    Generate a script to install all programs in the machine using chocolatey.
    Some programs must be revised because can include malware.
"""


def generate_chocolatey_install(host):
    choco_install = "# Choco install for: " + \
        host['ComputerName'] + \
        "\n# Edit packages when required options or versions\n"
    programs_installed = set()
    for program in host['programs']:
        programChoco = extract_chocolatey_package(program['DisplayName'])
        if programChoco:
            if programChoco in programs_installed:
                continue
            programs_installed.add(programChoco)
            choco_install += "try {\n" \
                + "    choco install " + programChoco + "\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"", "") + " installed.\"\n" \
                + "}\ncatch {\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"", "") + " cannot be installed.\"\n" \
                + "}\n\n"
            # Installation with versions
            """
            choco_install += "try {\n" \
                + "    choco install " + programChoco + "--version=" + program['DisplayVersion'] + "\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"","") + " installed.\"\n" \
                + "}\ncatch {\n" \
                + "    try {\n" \
                + "        choco install " + programChoco + "\n" \
                + "    }\n" \
                + "    catch {\n" \
                + "        Write-Host \"Program: " + program['DisplayName'].replace("\"","") + " cannot be installed.\"\n" \
                + "    }\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"","") + " installed.\"\n" \
                + "}\n\n"
            """
    for program in host['programs_x64']:
        programChoco = extract_chocolatey_package(program)
        if programChoco:
            if programChoco in programs_installed:
                continue
            programs_installed.add(programChoco)
            choco_install += "try {\n" \
                + "    choco install " + programChoco + "\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"", "") + " installed.\"\n" \
                + "}\ncatch {\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"", "") + " cannot be installed.\"\n" \
                + "}\n\n"
    for program in host['programs_x86']:
        programChoco = extract_chocolatey_package(program, x86=True)
        if programChoco:
            if (programChoco + "_x86") in programs_installed:
                continue
            programs_installed.add(programChoco + "_x86")
            choco_install += "try {\n" \
                + "    choco install " + programChoco + "\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"", "") + " installed.\"\n" \
                + "}\ncatch {\n" \
                + "    Write-Host \"Program: " + program['DisplayName'].replace("\"", "") + " cannot be installed.\"\n" \
                + "}\n\n"
    return choco_install


with open('domain.csv', newline='') as csvfile:
    domainAccount = csv.DictReader(csvfile)
    domainScript = ""
    domains = {}
    for row in domainAccount:
        # CN=Salvador Bendito,CN=Users,DC=MINAF,DC=ES
        dn = row['DN'].split(',')
        element = None
        anteriorDN = True
        dnOU = ""
        for dc in reversed(dn):
            claveValor = dc.split('=')
            if anteriorDN:
                if claveValor[0] is 'OU':
                    ouList.add(dc + "," + dnOU)
                    anteriorDN = False
                elif claveValor[0] is 'DC':
                    dnOU = dc + "," + dnOU
                else:
                    anteriorDN = False
            if element is not None:
                if claveValor[1] in element:
                    element2 = element[claveValor[1]]
                    element = element2
                else:
                    element2 = {'_type': claveValor[0]}
                    element[claveValor[1]] = element2
                    element = element2
            else:
                if claveValor[1] in domains:
                    element = domains[claveValor[1]]
                else:
                    element = {'_type': claveValor[0]}
                    domains[claveValor[1]] = element
    # Ya esta construido el arbol. Ahora se construye el script del dominio
    print(domains)
    print(generate_script_domain(domains))
    array = generate_script_domain(domains)
    print("\n".join(array))

host_info_from_directory