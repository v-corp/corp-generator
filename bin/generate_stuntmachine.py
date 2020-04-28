#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import time
import re
import wget
import hashlib
from sys import platform
import json
import random
from ..lib import info_cleaner, bios_cloner, mac_vendors



program_description = """
Use the information extracted from a real machine, to recreate it in a virtualized environment.
"""
parser = argparse.ArgumentParser(description=program_description)

parser.add_argument('--name', dest='machine_name', action='store', default='windows-corp',
                    help='Selects the name of the configuration previously created with corp-generator')
parser.add_argument('--extracted-info', dest='extracted_info', action='store', default='',
                    help='Extracted information path of the real machine.')
parser.add_argument('--bios', dest='bios', action='store_true', default=False,
                    help='Build a custom SeaBIOS.')


args = parser.parse_args()


currentDir = os.getcwd()
corpDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

if args.extracted_info == '':
    print("The path to the extracted information must be provided.")
    exit()

host_info = info_cleaner.host_info_from_directory(args.extracted_info)

if args.bios:
    bios_list_dir = os.path.join(currentDir,"bios")
    bios_dir = os.path.join(bios_list_dir, args.machine_name)
    
    if not os.path.isdir(bios_list_dir):
        os.makedirs(bios_list_dir)
    if not os.path.isdir(bios_dir):
        os.makedirs(bios_dir)
    
    process = subprocess.Popen(['git','clone','https://git.seabios.org/seabios.git'], stdout=subprocess.PIPE, cwd=bios_dir)
    output, error = process.communicate()
    p_status = process.wait()
    process.terminate()
    binary_bios = bios_cloner.compile_cloned_bios(bios_dir, host_info["bios"])
    print("Compiled Seabios: " + binary_bios)




data = {}

with open(os.path.join(currentDir, 'packer-' + args.machine_name + ".json"),'r') as packer_file:
    data = json.loads(json_data.read())

    # Replace disk
    disk_list = host_info["disk"]
    for dsk in disk_list:
        if dsk["DeviceID"].startswith("C"):
            data["variables"]["real_disk_size"] = dsk["size"]
            data["variables"]["disk_size"] = int(int(dsk["size"])/1000000)
    
    # Set MAC ADDRESS
    net_list = host_info["net"]
    for net in net_list:
        desc = net["Description"].lower()
        if not ('virtual adapter' in desc or 'hyper-v' in desc or 'loopback' in desc or 'vmware' in desc or 'virtualbox' in desc or 'kernel debug' in desc):
            data["variables"]["mac_address"] = net["MACAddress"]
            break

    # Set accounts?


with open(os.path.join(currentDir, 'packer-' + args.machine_name + ".json"),'w') as packer_file:
    packer_file.write(json.dumps(data,ident=1))

