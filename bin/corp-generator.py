#!/usr/bin/env python3

# Corp Country VM

# Corp Country is made of villagers
import argparse
import subprocess
import sys
import os
import subprocess
import time
import re
import wget
import hashlib

currentDir = os.getcwd()
corpDir = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..'))

print('Current directory: ' + currentDir)
print('Cache directory: ' + corpDir)
def check_if_admin():
    checkAdmin = """
    """
    process = subprocess.Popen(
        ["powershell.exe", "(New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    p_status = process.wait()
    process.terminate()
    if 'True' in str(output):
        return True
    try:
        return 'True' in str(output.decode('iso-8859-1'))
    except:
        return 'True' in str(output)


def extract_install_file():
    start_time = time.time()
    if os.path.isfile(os.path.join(corpDir, 'cache', args.iso_md5, 'sources', 'install.wim')):
        return 'wim'
    zip7Command = "7z x " + args.iso_path + " -o" + corpDir + \
        "\\cache\\" +args.iso_md5 + " sources\\install.wim -r"
    print(zip7Command)
    process = subprocess.Popen(zip7Command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    p_status = process.wait()
    elapsed_time = time.time() - start_time
    intstallName = 'wim'
    process.terminate()
    # It has a install.esd
    if(elapsed_time < 10):
        intstallName = 'esd'
        if os.path.isfile(corpDir + "\\cache\\" +args.iso_md5 + " sources\\install.esd"):
            return 'esd'
        zip7Command = "7z x " + args.iso_path + " -o" + corpDir + \
            "\\cache\\" + args.iso_md5 + " sources\\install.esd -r"
        process = subprocess.Popen(zip7Command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        p_status = process.wait()
        process.terminate()
        print('Extracted install.esd')
    else:
        print('Extracted install.wim')
    return intstallName


def get_windows_list(content):
    pattrn = 'Index : ([0-9]+)\s+Name : (.*)'
    pattern = re.compile(pattrn, re.MULTILINE)
    try:
        return re.findall(pattern, str(content.decode('iso-8859-1')))
    except:
        return re.findall(pattern, str(content))


def get_win_type(win_image):
    if '2008' in win_image:
        return 'win2008'
    if '2016' in win_image:
        return 'win2016'
    if '2019' in win_image:
        return 'win2019'
    if 'windows 10' in win_image.lower():
        return 'win10'
    if 'windows 7' in win_image.lower():
        return 'win7'
    print('Cannot identify Windows OS version: ' + win_image)
    exit()


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def replaceArgumentsFunction(content, arguments):
    return content.replace('<<USR_NAME>>', arguments.username).replace('<<USR_PSWD>>', arguments.password).replace('<<VIRTIO>>', arguments.virtio).replace('<<WIN_IMG>>', str(arguments.win_image)).replace('<<MACHINE_NAME>>', arguments.machine_name).replace('<<ISO_PATH>>', arguments.iso_path).replace('<<IMG_SELECTOR>>', arguments.win_image_type).replace('<<ISO_CHECKSUM>>', arguments.iso_md5).replace('<<VIRTIO_PATH>>',arguments.virtio_path).replace('<<CORP_COMMAND>>', ' '.join(sys.argv).replace('\\','/'))


def copyFileAndCreateFolders(origin, destino):
    if os.path.isfile(origin):
        with open(origin, 'r') as origin_file:
            if not os.path.isdir(os.path.dirname(destino)):
                os.makedirs(os.path.dirname(destino))
            with open(destino, 'w') as destination_file:
                destination_file.write(origin_file.read())


def copyFileCreateFoldersAndReplace(origin, destino, arguments):
    if os.path.isfile(origin):
        with open(origin, 'r') as origin_file:
            if not os.path.isdir(os.path.dirname(destino)):
                os.makedirs(os.path.dirname(destino))
            with open(destino, 'w') as destination_file:
                destination_file.write(replaceArgumentsFunction(
                    origin_file.read(), arguments))

def cleanVirtioFromPDB(virtio_path):
    for root, dirs, files in os.walk(virtio_path, topdown=False):
        for name in files:
            if(name.endswith('.pdb')):
                os.remove(os.path.join(root, name))

program_description = """
Create a complete Windows based security LAB with malware sandbox ofuscation maximized using KVM.\n 
7zip and DSIM are required in order to autodetect windows image types if they are not provided.
"""
parser = argparse.ArgumentParser(description=program_description)

parser.add_argument('--iso', dest='iso_path', action='store', #default='A:\TFM\plantillas_packer\packer_cache\efb043a754a51177aaac7881fbe9234c06fe97c8.iso',
                    help='selects the iso with which generate the villager template')
parser.add_argument('--iso-md5', dest='iso_md5', action='store',
                    help='Checksum for the ISO. If not provided will be autocalculated')
parser.add_argument('--name', dest='machine_name', action='store', default='windows-corp',
                    help='sets the name for this machine')
parser.add_argument('--username', dest='username', action='store', default='vagrant',
                    help='sets the name of the user in this machine')
parser.add_argument('--password', dest='password', action='store', default='vagrant',
                    help='sets the password for the user in this machine')
parser.add_argument('--virtio', dest='virtio', action='store', default='0.1.172',
                    help='version of the virtio drivers to use. Set to NONE to skip this step.')
parser.add_argument('--win-type', dest='win_type', action='store',
                    help='version of windows: win10, win2016, win7, win2008, win2012, win2019.If it\'s not provided, then DSIM will be used to autodetect the version')
parser.add_argument('--win-image', dest='win_image', action='store', default=1,
                    help='select windows image to install. It can be selected using a number (image index inside install.wim) or the image name. Ej: 1, 2, 3, 4, \'Windows 10 Home\',\'Windows 10 Pro\',\'Windows Server 2016 SERVERSTANDARD\'')
parser.add_argument('--clean-cache', dest='clean_cache', action='store_true', default=False,
                    help='Clean the cache folder (It stores virtio versions and install.WIM files).')
args = parser.parse_args()

if args.clean_cache:
    for root, dirs, files in os.walk(os.path.join(corpDir, 'cache'), topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    exit()

# Write templates
if not args.iso_md5:
    print('Calculating MD5 of ISO image...')
    args.iso_md5 = md5(args.iso_path)
    print('MD5 = ' + args.iso_md5)

if not args.win_type:
    print('Checking Windows Image Type...')
    if not check_if_admin():
        print('ERROR: Elevated permissions are required to run DISM for extracting the Images stored in the ISO')
        exit()
    # Obtain valid types
    # Alternative: http://www.webupd8.org/2013/06/wimlib-imagex-dism-alternative-to.html
    installName = extract_install_file()
    dsimCommand = "dism.exe /get-wiminfo /wimfile:" + os.path.join(corpDir, 'cache', args.iso_md5,'sources','install.' + installName)
    print(dsimCommand)
    process = subprocess.Popen(dsimCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    p_status = process.wait()
    process.terminate()
    windowsList = get_windows_list(output)
    print('Select a Windows Image:')
    selectedImg = ''
    for img in windowsList:
        print(img[0] + ' - ' + img[1])

    selectedImg = int(input())
    print('WIN_IMAGE=' + windowsList[selectedImg - 1][1])
    args.win_image = selectedImg
    args.win_type = get_win_type( windowsList[selectedImg - 1][1])

# Select image using index or name
try:
    # https://docs.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-setup-imageinstall-osimage-installfrom-metadata-key
    image_index = int(args.win_image)
    args.win_image = image_index
    args.win_image_type = '/IMAGE/INDEX'
except ValueError:
    args.win_image_type = '/IMAGE/NAME'

# Download virtio drivers
# https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.172-1/virtio-win-0.1.172.iso
if args.virtio != 'NONE':
    pattern_virtio = re.compile(
        '(\\d\\.\\d\\.\\d{2,3})(?:-(\\d)){0,1}', re.MULTILINE)
    virtio_match = re.search(pattern_virtio, args.virtio)
    virtio_version = args.virtio
    virtio_subversion = 1
    if len(virtio_match.groups()) == 2:
        virtio_version = virtio_match.groups()[0] or '0.1.172'
        virtio_subversion = virtio_match.groups()[1] or 1
    else:
        virtio_version = virtio_match.groups()[0] or '0.1.172'
        virtio_subversion = 1
    virtio_cache_location = os.path.join(corpDir, 'cache', 'virtio', 'virtio-win-{virtio_version}-{virtio_subversion}.iso').format(
        virtio_version=virtio_version, virtio_subversion=virtio_subversion)
    if not os.path.isfile(virtio_cache_location):
        print('Downloading Virtio drivers {virtio_version}-{virtio_subversion} from:'.format(virtio_version=virtio_version, virtio_subversion=virtio_subversion))
        print('https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-{virtio_version}-{virtio_subversion}/virtio-win-{virtio_version}.iso'.format(virtio_version=virtio_version, virtio_subversion=virtio_subversion))
        if not os.path.isdir(os.path.dirname(virtio_cache_location)):
            os.makedirs(os.path.dirname(virtio_cache_location))
        wget.download('https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-{virtio_version}-{virtio_subversion}/virtio-win-{virtio_version}.iso'.format(virtio_version=virtio_version, virtio_subversion=virtio_subversion), virtio_cache_location)
        os.makedirs(os.path.dirname(os.path.join(corpDir, 'virtio',"virtio-win-" + str(virtio_version) + '-'+ str(virtio_subversion))))
        virtio7Zip = "7z x " + virtio_cache_location + " -o" + corpDir + "\\cache\\virtio\\virtio-win-" + str(virtio_version) + '-'+ str(virtio_subversion)
        args.virtio_path = os.path.join(corpDir, 'cache','virtio',"virtio-win-" + str(virtio_version) + '-'+ str(virtio_subversion)).replace('\\','/')
        process = subprocess.Popen(virtio7Zip.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        p_status = process.wait()
        process.terminate()
        cleanVirtioFromPDB(args.virtio_path)
    else:
        print('Reading drivers {virtio_version}-{virtio_subversion} from cache at {virtio_cache_location}'.format(
            virtio_version=virtio_version, virtio_subversion=virtio_subversion, virtio_cache_location=virtio_cache_location))
        args.virtio_path = os.path.join(corpDir, 'cache', 'virtio',"virtio-win-" + str(virtio_version) + '-'+ str(virtio_subversion)).replace('\\','/')
    args.virtio = virtio_cache_location.replace('\\','/')
else:
    args.virtio = '__EDIT_VIRTIO_LOCATION__'

# All paths must be changed to be printed in JSON files
args.iso_path = args.iso_path.replace('\\','/')

# --------------------------------------------- Templates ---------------------------------------------
copyFileCreateFoldersAndReplace(os.path.join(corpDir, 'templates', args.win_type, 'Autounattend.xml'), os.path.join(
    currentDir, 'answer', args.machine_name, 'Autounattend.xml'), args)
print("Created answer file: " + os.path.join('answer', args.machine_name, 'Autounattend.xml'))

copyFileCreateFoldersAndReplace(os.path.join(corpDir, 'templates', args.win_type, 'packer-file.json'),
    os.path.join(currentDir, 'packer-' + args.machine_name + '.json'), args)
print("Created packer file: " + 'packer-' + args.machine_name + '.json')

copyFileCreateFoldersAndReplace(os.path.join(corpDir, 'templates', args.win_type, 'vagrant-file.template'), os.path.join(
    currentDir, 'vagrant-files', 'vagrant-' + args.machine_name + '.template'), args)
print("Created vagrant file: " + os.path.join('vagrant-files', 'vagrant-' + args.machine_name + '.template'))

# --------------------------------------------- SCRIPTS -----------------------------------------------
scriptDir = os.path.join(currentDir, 'scripts', args.machine_name)
for root, dirs, files in os.walk(os.path.join(corpDir, 'scripts',args.win_type), topdown=False):
        for name in files:
            print('Copy script: ' + name)
            copyFileAndCreateFolders(os.path.join(root, name),os.path.join(scriptDir,name))

# --------------------------------------------- GIT IGNORE ---------------------------------------------
copyFileAndCreateFolders(os.path.join(corpDir, 'templates', 'gitignore'), os.path.join(
    currentDir, '.gitignore'))
print("Created .gitignore")

