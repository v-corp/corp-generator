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

program_description = """
Vagrantice an alredy defined Windows Image.
"""
parser = argparse.ArgumentParser(description=program_description)


parser.add_argument('--name', dest='machine_name', action='store', default='windows-corp',
                    help='sets the name for this machine')
parser.add_argument('--proxmox-config', dest='proxmox_config', action='store', default='',
                    help='Secret configuration of proxmox, like Username, Password and URL .')
parser.add_argument('--proxmox-storage', dest='proxmox_storage', action='store', default='',
                    help='Select a storage for the proxmox template.')
args = parser.parse_args()

if args.proxmox_config == '':
    print("The configuration file must be defined.")
    exit()

currentDir = os.getcwd()
corpDir = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..'))

FLOPPY_DIR = os.path.join(currentDir, 'floppy')

PROXMOX_TEMPLATE_DIR = os.path.join(currentDir, 'proxmox')


px_endpoint = ''
px_user_name = ''
px_password = ''
px_project_name = 'cancamusa'
px_vm_id_range = '800..900'
px_storage = ''
try:
    if os.path.isfile(proxmox_config):
        with open(proxmox_config, 'r') as json_data:
            data = json.loads(json_data.read())
            px_endpoint = data["endpoint"]
            px_user_name = data["user_name"]
            px_password = data["password"]
            if 'project_name' in data:
                px_project_name = data["project_name"]
            if 'vm_id_range' in data:
                px_vm_id_range = data["vm_id_range"]
            if 'proxmox_storage' in data:
                px_storage = data["proxmox_storage"]
    else:
        raise Exception('File does not exists')
except e as Exception:
    print(str(e))
    print("Not a valid configuration file. Needs to be:")
        print("""
{
    "endpoint" : "https://proxmox.example.com/api2/json",
    "user_name" : "vagrant",
    "password" : "password",
    "project_name" : "cancamusa",
    "vm_id_range" : "800..900",
    "proxmox_storage" : "local-lvm"

}
""")
    exit()


if not args.proxmox_storage == '':
    px_storage = args.proxmox_storage

if args.proxmox and not os.path.isdir(PROXMOX_TEMPLATE_DIR):
    os.makedirs(PROXMOX_TEMPLATE_DIR)

if args.proxmox and not os.path.isdir(FLOPPY_DIR):
    os.makedirs(FLOPPY_DIR)

floppy_machine_dir = os.path.join(FLOPPY_DIR, args.machine_name)
if args.proxmox and not os.path.isdir(floppy_machine_dir):
    os.makedirs(floppy_machine_dir)


print("Generating floppy image")
FLOPPY_DISK_IMG = os.path.join(FLOPPY_DIR,args.machine_name + '.img')
process = subprocess.Popen(['mkfs.msdos', '-C', FLOPPY_DISK_IMG  ,'1440'], stdout=subprocess.PIPE)
output, error = process.communicate()
p_status = process.wait()
process.terminate()

process = subprocess.Popen(('mount -o loop '+ FLOPPY_DISK_IMG + ' ' + floppy_machine_dir).split(), stdout=subprocess.PIPE)
output, error = process.communicate()
p_status = process.wait()
process.terminate()

packer_file_path = os.path.join(currentDir, 'packer-' + args.machine_name + '.json')
floppy_list = []
cores = 1
memory = 4096
disk = "64000"
iso_path = ""
if os.path.isfile(packer_file_path):
    with open(packer_file_path, 'r') as json_data:
        data = json.loads(json_data.read())
        floppy_list = data["variables"]["floppy_files_list"].split(",")
        cores = data["variables"]["cpus"]
        disk = str(data["variables"]["disk_size"]) + 'M'

        # Test if quemu supports B leter
        if 'real_disk_size' in data["variables"]:
            disk = str(data["variables"]["disk_size"]) + 'B'
        iso_path = data["variables"]["iso_path"]
        
for floppy_file in floppy_list:
    if floppy_file.endswith("*"):
        os.popen('cp ' + floppy_file + ' ' + floppy_machine_dir)

    else:
        os.popen('cp ' + floppy_file + ' ' + floppy_machine_dir)
    
process = subprocess.Popen(('umount '+ floppy_machine_dir).split(), stdout=subprocess.PIPE)
output, error = process.communicate()
p_status = process.wait()
process.terminate()

print("Floppy disk created: " + FLOPPY_DISK_IMG)
qemu_template_file = os.path.join(PROXMOX_TEMPLATE_DIR, args.machine_name + '-qemu.conf')
with open(qemu_template_file, 'w') as qemu_template:
    qemu_template.write('args: -fda ' + FLOPPY_DISK_IMG + '\n')
    qemu_template.write('bootdisk: virtio0\n')
    qemu_template.write('cores: ' + str(cores) +'\n')
    qemu_template.write('sockets: ' + str(int(min(1, int(cores)/2))) +'\n')
    qemu_template.write('memory: ' + str(memory) + '\n')
    qemu_template.write('ide0: ' + px_storage + ':iso/' + str(os.path.basename(iso_path)) +',media=cdrom\n')
    qemu_template.write('name: ' + str(args.machine_name) + '\n')
    # TODO: generate random macs based on a defined set of vendors
    qemu_template.write('net0: e1000=' + str(rand_mac()) + ',bridge=vmbr0,firewall=1\n')
    qemu_template.write('numa: 0\n')
    qemu_template.write('ostype: ' + args.win_type + '\n')
    qemu_template.write('scsi1: ' + px_storage + ':base-disk-' + args.machine_name + ',size=' + str(disk) + '\n')
    qemu_template.write('scsihw: virtio-scsi-pci\n')
print('QEMU template for proxmox created: ' + qemu_template_file)



