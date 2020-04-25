#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import time
import re
import csv 
import json
import random
import string

currentDir = os.getcwd()
program_description = """
Uses a CSV to clone all the users of a real domain. It can use the real password of each user or a random one.
"""
parser = argparse.ArgumentParser(description=program_description)

parser.add_argument('in_file',metavar='FILE_IN', default="domain.csv",
                    help='Input file')
parser.add_argument('--pswd', dest='password', action='store', default="",
                    help='Uses the same password. Default: Random()')
parser.add_argument('--adm-pswd', dest='admin_password', action='store', default="",
                    help='Custom password for the admin user.')
parser.add_argument('--adm', dest='admin', action='store', default="Administrator",
                    help='Name for the admin user. Default: Administrator')
parser.add_argument('--out', dest='out_file', action='store', default="",
                    help='Script file name. Default: print to standard output')

args = parser.parse_args()




def randString(length=8):
    your_letters='abcdefghijklmnopqrstuvwxyz0123456789_%'
    return ''.join((random.choice(your_letters) for i in range(length)))

def name_and_type(obj):
    splited_obj = obj.split("=")
    return {
        "Type" : splited_obj[0],
        "Name" : splited_obj[1]
    }

def extract_info(obj_path = ""):
    splited_path = obj_path.split(",")
    name = splited_path[0].split("=")[1]
    return {
        "Name" : name,
        "Path" : ",".join(splited_path[1:])
    }

def create_ad_group(usr_group):
    info_group = extract_info(usr_group)
    return 'New-ADGroup -Name "' + info_group["Name"] + '" -SamAccountName "' + info_group["Name"] + '" -GroupCategory Security -GroupScope Global -DisplayName "' + info_group["Name"] + '" -Path "' + info_group["Path"] + '" -Description ""'

def generate_script_domain(domain_file, actual_domain=""):
    scripted_ou = []
    scripted_groups = []
    scripted_users = []

    created_user_groups = []
    created_ous = []
    domain_name = domain_file["domain"]

    for usr_group in domain_file["ou_groups"]:
        info_group = extract_info(usr_group)
        if info_group["Path"] == domain_name:
            scripted_ou.append('New-ADOrganizationalUnit -name "' + info_group["Name"] + '"')
        else:
            scripted_ou.append('New-ADOrganizationalUnit -name "' + info_group["Name"] + '" -path "' + info_group["Path"] + '"')
        created_ous.append(usr_group)
    
    for usr_group in domain_file["user_groups"]:
        if not usr_group in created_user_groups:
            info_group = create_ad_group(usr_group)
            scripted_groups.append(info_group)
            created_user_groups.append(usr_group)

    for usr_group in domain_file["user_list"]:
        name = usr_group["Name"]
        displayName = usr_group["Name"] if usr_group["DisplayName"] == "" else usr_group["DisplayName"]
        scripted_users.append('New-ADUser -Name "' + name + '" -GivenName "' + usr_group["GivenName"] +'" -Surname "' + usr_group["Surname"] +'" -SamAccountName "' + usr_group["SamAccountName"] + '" -Enabled $True -ChangePasswordAtLogon $True -DisplayName "' + displayName + '" -Department "" -Path "' + usr_group["Path"] + '" -Description "' + usr_group["Description"] + '" -AccountPassword (convertto-securestring "' + usr_group["Password"] +'" -AsPlainText -Force)')
        for new_group in usr_group["MemberOf"]:
            if (",DC=" in new_group or ",CN=" in new_group):
                scripted_users.append('Add-ADGroupMember -Identity "' + new_group + '" -Member "' + usr_group["DN"] + '"')
                if not new_group in created_user_groups:
                    info_group = create_ad_group(new_group)
                    scripted_groups.append(info_group)
                    created_user_groups.append(new_group)
        scripted_users.append("")


    return "#OrganizationalUnits:\n" + "\n".join(scripted_ou) + "\n\n#Groups:\n" + "\n".join(scripted_groups) + "\n\n#Users:\n" + "\n".join(scripted_users)


def join_dn_array(dn_array):
    ret = ""
    for i in range(len(dn_array) - 1):
        ret = "," +dn_array[i][0] + "=" + dn_array[i][1] + ret
    #ret = dn_array[len(dn_array) - 1][0] + "=" + dn_array[len(dn_array) - 1][1]
    ret = ret[1:]
    return ret


def proces_csv_file(csv_file):
    with open(csv_file, newline='') as csvfile:
        domainAccount = csv.DictReader(csvfile)
        domain_DC = []
        domain = ""
        ou_groups = []
        ou_list = []
        user_list = []
        user_groups = []
        for row in domainAccount:
            # CN=Salvador Bendito,CN=Users,DC=MINAF,DC=ES
            dn_split = row['DN'].split(',')
            element = None
            anteriorDN = True
            dnOU = ""
            dn_processed_list = []
            for dc in reversed(dn_split):
                claveValor = dc.split('=')
                if claveValor[0] == "DC" and claveValor[1] not in domain_DC:
                    domain_DC.append(claveValor[1])
                dn_processed_list.append([claveValor[0], claveValor[1]])
            if row["objectClass"] == "user":
                grp = join_dn_array(dn_processed_list)
                user_groups.append(grp)
                user_list.append({
                    "Name" : row["cn"],
                    "DN" : row["DN"],
                    "Path" : grp,
                    "SamAccountName" : row["sAMAccountName"],
                    "DisplayName" : row["displayName"],
                    "Description" : row["description"],
                    "UserPrincipalName" : row["userPrincipalName"],
                    "GivenName" : row["givenName"],
                    "Surname" : row["sn"],
                    "MemberOf" : row["memberOf"].split(";"),
                    "os" : row["operatingSystem"],
                    "os_version" : row["operatingSystemVersion"],
                    "Password" : args.admin_password if (args.admin == row["cn"] and not args.admin_password == "") else (randString(10) if args.password == "" else args.password)
                })
            if row["objectClass"] == "computer":
                grp = join_dn_array(dn_processed_list)
                ou_groups.append(grp)
                ou_list.append({
                    "Name" : row["cn"],
                    "Path" : grp,
                    "SamAccountName" : row["sAMAccountName"],
                    "DisplayName" : row["displayName"],
                    "Description" : row["description"]

                })
        return {
            "domain" : "DC=" + ",DC=".join(reversed(domain_DC)),
            "domain_uri" : ".".join(reversed(domain_DC)),
            "user_list" : user_list,
            "user_groups" : list(set(reversed(sorted(user_groups, key=len)))),
            "ou_list" : ou_list,
            "ou_groups" : list(set(reversed(sorted(ou_groups, key=len))))
        }

    # Ya esta construido el arbol. Ahora se construye el script del dominio
    #print(domains)
    #print(generate_script_domain(domains))
    #array = generate_script_domain(domains)
    #print("\n".join(array))
#print(json.dumps(proces_csv_file("domain.csv")))

domain_info = proces_csv_file(args.in_file)
domain_uri = domain_info["domain_uri"]

powershell_script = """param (
    [String] $ip,
    [String] $password = "cancamusa",
    [String] $dns1 = "8.8.8.8",
    [String] $dns2 = "8.8.4.4",
    [String] $domainNetBios = "corp"
)
if ((gwmi win32_computersystem).partofdomain -eq $true) {
    Exit
}

""" + '$domain = "'+ domain_uri.lower().strip() + '"' + """
#Todavia no está en dominio
Write-Host 'Installing RSAT tools'
Import-Module ServerManager
Add-WindowsFeature RSAT-AD-PowerShell,RSAT-AD-AdminCenter

# Eliminar política de contraseña robusta
secedit /export /cfg C:\\secpol.cfg
(gc C:\\secpol.cfg).replace("PasswordComplexity = 1", "PasswordComplexity = 0") | Out-File C:\\secpol.cfg
secedit /configure /db C:\\Windows\\security\\local.sdb /cfg C:\\secpol.cfg /areas SECURITYPOLICY
rm -force C:\\secpol.cfg -confirm:$false

$PlainPassword = $password
$SecurePassword = $PlainPassword | ConvertTo-SecureString -AsPlainText -Force


# Instalar Forest y convertir la maquina en un DC
Install-WindowsFeature AD-domain-services
Import-Module ADDSDeployment
Install-ADDSForest -SafeModeAdministratorPassword $SecurePassword `
    -CreateDnsDelegation:$false `
    -DatabasePath "C:\\Windows\\NTDS" `
    -DomainMode "7" `
    -DomainName $domain `
    -DomainNetbiosName $domainNetBios `
    -ForestMode "7" `
    -InstallDns:$true `
    -LogPath "C:\\Windows\\NTDS" `
    -NoRebootOnCompletion:$true `
    -SysvolPath "C:\\Windows\\SYSVOL" `
    -Force:$true

$newDNSServers = $dns1, $dns2
$adapters = Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.DefaultIPGateway -ne $null -and $_.DefaultIPGateway[0].StartsWith($subnet) }
if ($adapters) {
    Write-Host Setting DNS
    $adapters | ForEach-Object {$_.SetDNSServerSearchOrder($newDNSServers)}
}"""

powershell_script = powershell_script + generate_script_domain(domain_info)

if args.out_file == "":
    print(powershell_script)
else:
    with open(args.out_file, "w") as file_script:
        file_script.write(powershell_script)