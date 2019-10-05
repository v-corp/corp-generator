# Unir archivos de configuración de Vagrant en uno solo
import json
import os
import codecs
scanPath = 'bin'
with open(os.path.join(scanPath, 'disk.json')) as json_file:
    decoded_data=codecs.decode(json_file.read().encode(), 'utf-8-sig')
    data = json.loads(decoded_data)
    for disk in data:
        if disk['DriveType'] == 3:
            # Is HDD/SDD disk
            deviceId = disk['DeviceID'].replace(':','')
            volumeName = disk['VolumeName']
            size = disk['Size']
            freeSpace = disk['FreeSpace']
            print(deviceId + ' ' + str(size))
with open(os.path.join(scanPath, 'bios.json')) as json_file:
    decoded_data=codecs.decode(json_file.read().encode(), 'utf-8-sig')
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
        print(customBios)
        # Build seabios with custom configuration

with open(os.path.join(scanPath, 'net.json')) as json_file:
    decoded_data=codecs.decode(json_file.read().encode(), 'utf-8-sig')
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
    print(customIface)

with open(os.path.join(scanPath, 'version.json')) as json_file:
    decoded_data=codecs.decode(json_file.read().encode(), 'utf-8-sig')
    vFile = json.loads(decoded_data)
    customIf = {}
    if vFile['Major']:
        customIf['Major'] = vFile['Major']
        customIf['Minor'] = vFile['Minor']
        customIf['Build'] = vFile['Build']
        customIf['Revision'] = vFile['Revision']
        customIf['MajorRevision'] = vFile['MajorRevision']
        customIf['MinorRevision'] = vFile['MinorRevision']
    print(customIf)
        
