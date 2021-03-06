import os
import re
from random import randrange
import argparse

def replace_files(file_list=[], replacer_list=[]):
    for file_name in file_list:
        data = ""
        with open(file_name, 'r') as file_data:
            data = file_data.read()
            for replacer in replacer_list:
                data = data.replace(replacer[0], replacer[1])
        with open(file_name, 'w') as file_data:
            file_data.write(data)

def process_release_date(released):
        #Format: 20120305000000.000000+000
        regex= r"^(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})"
        matches= re.search(regex, released)
        return matches.group('day') + "/" + matches.group('month') + "/" + matches.group('year')

# git clone https://git.seabios.org/seabios.git
# qemu -bios out/bios.bin
# https://gist.github.com/doomedraven/41af84c8cf93ba63cea933a80e898fb6

"""
Use information extracted from a Windows machine to compile a seabios that shows the same
information as te original one.
Information extracted using: Get-WmiObject Win32_Bios | ConvertTo-Json
"""
def compile_cloned_bios(seabios_path, bios):
    SEABIOS_PATH = seabios_path
    SRC_CONFIG_H = os.path.join(SEABIOS_PATH, "src", "config.h")
    SRC_FW_SSDT_MISC_DSL = os.path.join(SEABIOS_PATH, "src", "fw", "ssdt-misc.dsl")
    VGASRC_KCONFIG = os.path.join(SEABIOS_PATH, "vgasrc", "Kconfig")
    SRC_HW_BLOCKCMD_C = os.path.join(SEABIOS_PATH, "src", "hw", "blockcmd.c")
    SRC_FW_PARAVIRT_C = os.path.join(SEABIOS_PATH, "src", "fw", "paravirt.c")
    SRC_HW_BLOCKCMD_C = os.path.join(SEABIOS_PATH, "src", "hw", "blockcmd.c")
    SRC_FW_ACPI_DSDT_DSL = os.path.join(SEABIOS_PATH, "src", "fw", "acpi-dsdt.dsl")
    SRC_FW_Q35_ACPI_DSDT_DSL = os.path.join(
        SEABIOS_PATH, "src", "fw", "q35-acpi-dsdt.dsl")
    SRC_FW_SSDT_PCIHP_DSL = os.path.join(
        SEABIOS_PATH, "src", "fw", "ssdt-pcihp.dsl")
    SRC_FW_SSDT_PROC_DSL = os.path.join(SEABIOS_PATH, "src", "fw", "ssdt-proc.dsl")
    SRC_FW_PCIINIT_c = os.path.join(SEABIOS_PATH, "src", "fw", "pciinit.c")
    SRC_FW_BIOSTABLES_c = os.path.join(SEABIOS_PATH, "src", "fw", "biostables.c")
    SRC_FW_CSMC_C = os.path.join(SEABIOS_PATH, "src", "fw", "csmc.c")

    NEW_BIOS_NAME_UPPER = bios['Version'].split(" ")[0]
    NEW_BIOS_NAME = NEW_BIOS_NAME_UPPER[0] + (NEW_BIOS_NAME_UPPER[1:]).lower()

    data = ""
    with open(SRC_FW_PCIINIT_c, 'r') as file_data:
        data = file_data.read()
    data = re.sub(r'"Intel IGD BDSM enabled at[^"]+"', '"' + bios["Name"] + '"', data)
    with open(SRC_FW_PCIINIT_c, 'w') as file_data:
        file_data.write(data)

    replace_files([SRC_FW_BIOSTABLES_c], [
        ['#define BIOS_NAME "SeaBIOS"', '#define BIOS_NAME "' + bios["Manufacturer"] +'"'],
        ['#define BIOS_DATE "04/01/2014"', '#define BIOS_DATE "' + process_release_date(bios["ReleaseDate"]) +'"']
    ])

    replace_files([SRC_CONFIG_H], [
        ["Bochs", NEW_BIOS_NAME],
        ["BOCHSCPU", NEW_BIOS_NAME_UPPER],
        ["BOCHS ", NEW_BIOS_NAME_UPPER + " "],
        ["BXPC", NEW_BIOS_NAME_UPPER],
        ['"BXPC"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])

    replace_files([SRC_FW_SSDT_MISC_DSL], [
        ["QEMU0001", NEW_BIOS_NAME_UPPER]
    ])

    replace_files([VGASRC_KCONFIG], [
        ["QEMU/Bochs", NEW_BIOS_NAME],
        ["qemu ", NEW_BIOS_NAME + " "]
    ])

    replace_files([SRC_HW_BLOCKCMD_C, SRC_FW_PARAVIRT_C], [
        ['"QEMU', '"' + NEW_BIOS_NAME_UPPER]
    ])

    replace_files([SRC_HW_BLOCKCMD_C], [
        ['"QEMU"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])

    replace_files([SRC_FW_ACPI_DSDT_DSL, SRC_FW_Q35_ACPI_DSDT_DSL], [
        ['"BXPC"', '"' + NEW_BIOS_NAME_UPPER + '"'],
        ['"BXDSDT"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])

    replace_files([SRC_FW_SSDT_PCIHP_DSL], [
        ['"BXPC"', '"' + NEW_BIOS_NAME_UPPER + '"'],
        ['"BXDSDT"', '"' + NEW_BIOS_NAME_UPPER + '"'],
        ['"BXSSDTPCIHP"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])

    replace_files([SRC_FW_SSDT_PROC_DSL], [
        ['"BXPC"', '"' + NEW_BIOS_NAME_UPPER + '"'],
        ['"BXDSDT"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])

    replace_files([SRC_FW_SSDT_MISC_DSL], [
        ['"BXPC"', '"' + NEW_BIOS_NAME_UPPER + '"'],
        ['"BXSSDTSU"', '"' + NEW_BIOS_NAME_UPPER + '"'],
        ['"BXSSDTSUSP"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])
    replace_files([SRC_FW_Q35_ACPI_DSDT_DSL, SRC_FW_ACPI_DSDT_DSL, SRC_FW_SSDT_MISC_DSL, SRC_FW_SSDT_PROC_DSL, SRC_FW_SSDT_PCIHP_DSL], [
        ['"BXPC"', '"' + NEW_BIOS_NAME_UPPER + '"']
    ])

    replace_files([SRC_FW_CSMC_C], [
        ['.OemIdStringPointer = (u32)"SeaBIOS",', '.OemIdStringPointer = (u32)"' + bios["Manufacturer"] + '",']
    ])
    replace_files([SRC_OUTPUT_C], [
        ['"SeaBIOS (version', '" ' + bios["Manufacturer"] + ' (version']
    ])

    # do make
    process = subprocess.Popen(['make'], stdout=subprocess.PIPE, cwd=SEABIOS_PATH)
    output, error = process.communicate()
    p_status = process.wait()
    process.terminate()

    # bios compiled file
    return os.path.join(seabios_path,"out","bios.bin")
