import json
import os
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