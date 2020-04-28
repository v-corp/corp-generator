"""
 Creates a clone of a real machine to use in a virtualized network of the corporation.
 The generated machine is a stuntmachine (stuntman) of the real machine.
 This script needs info extracted using "extract-info.ps1"
"""
import json
import os
import codecs
import csv

from choco_script import *


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
            host['bios'] = customBios
            # Build seabios with custom configuration

    with open(os.path.join(scanPath, 'net.json')) as json_file:
        decoded_data = codecs.decode(json_file.read().encode(), 'utf-8-sig')
        netFile = json.loads(decoded_data)
        customIface = []
        for netIface in netFile:
            if 'MACAddress' in netIface and 'IPAddress' in netIface and not netIface['IPAddress'] == None:
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
