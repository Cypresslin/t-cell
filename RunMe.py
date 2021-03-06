#!/usr/bin/env python
"""T-Cell, the component issue lookup tool.

A small tool for checking known buggy components on your system.
Copyright (c) 2014 - 2015  Po-Hsu Lin <po-hsu.lin@canonical.com>
"""

import os
import re
import glob
import json
import platform
import subprocess
from itertools import chain

XDISPLAY = "DISPLAY=" + os.getenv("DISPLAY", ':0')


def sysinfo():
    """Return the distro and kernel version to see which database to use."""
    data = platform.release().split('.')
    return platform.dist()[2], '.'.join(data[:2])


def xinput_detect():
    """Detect PS/2 Mouse."""
    data = subprocess.check_output(XDISPLAY + " xinput list --name-only", shell=True)
    if "PS/2 Generic Mouse" in data:
        print('================================================')
        print('"PS/2 Generic Mouse" found in xinput')
        print('Please check scrolling ability of your touchpad.')
        print('================================================')
    if "SynPS/2 Synaptics TouchPad" in data:
        capability = subprocess.check_output(
            XDISPLAY + " xinput list-props 'SynPS/2 Synaptics TouchPad' | grep Capa",
            shell=True)
        capability = re.sub('\t.*:\t', '', capability)
        capability = re.split(',', capability)
        if capability[4]:  # 1 - device support 3-finger detection
            printer("Synaptics Touchpad", "1384042", "Input")


def parser_input():
    """Return devices found in /proc/bus/input/devices."""
    data = subprocess.check_output("cat /proc/bus/input/devices | sed -n 's/I: //p'", shell=True)
    data = re.sub('Vendor=', 'input-', data)
    data = re.sub(' Product=', ':', data)
#   No Subsystem in input, but added here to retain consistency with PCIdev
    result = re.finditer('\w+ (?P<COMP>input-\w+:\w+) Version=(?P<REV>\w{4})'
                         '(.+(?P<SUB>Subsystem-\w+:\w+))?', data)
    return result


def parser_usb():
    """Return devices found in usb-devices command."""
    data = subprocess.check_output("usb-devices", shell=False)
    data = re.sub('Vendor=', 'usb-', data)
    data = re.sub(' ProdID=', ':', data)
#   No Subsystem in USB, but added here to retain consistency with PCIdev
    result = re.finditer('(?P<COMP>usb-\w+:\w+) \w+=(?P<REV>.+)'
                         '(.+(?P<SUB>Subsystem-\w+:\w+))?', data)
    return result


def parser_pci():
    """Return devices found in "lspci -nv" command."""
    data = subprocess.check_output("lspci -nv", shell=True)
    data = re.sub('\s+Subsystem: ', ' Subsystem-', data)
    data = re.sub(':\s', ' pci-', data)
#   REV is not necessary, not every device has it
    result = re.finditer('\S+ (?P<COMP>pci-\w+:\w+)(.\(rev (?P<REV>\w+)\))?'
                         '(.+(?P<SUB>Subsystem-\w+:\w+))?', data)
    return result


def parser_pnp():
    """Return devices found in /sys/devices/pnp0/.

    REV, SUB will be added for data stucture consistency
    """
    data = subprocess.check_output("cat /sys/devices/pnp0/*/id", shell=True)
    data = re.sub("$\n", "", data)
    data = re.sub("^", "pnp-", data, flags=re.MULTILINE)
    result = re.finditer('(?P<COMP>pnp-.+)(?P<REV>rev)?(?P<SUB>sub)?', data)
    return result


def printer(dev, bug, cat):
    """Print out the information."""
    print("Known issue for %s: http://pad.lv/%s (%s)" % (dev, bug, cat))


def main():
    """Check buggy components by its device ID."""
    found = False
    distro, ver = sysinfo()
    fn = distro + "-" + ver + "-bug.json"
    fn_common = "common-bug.json"
    print('Your distro: %s' % distro)
    print('Your kernel version: %s.X ' % ver)
    if not os.path.isfile(fn):
        print("Sorry we don't have a database for %s-%s" % (distro, ver))
        filenames = glob.glob('*-%s-bug.json' % (ver))
        if 0 == len(filenames):
            print("And we don't have any database for kernel %s" % (ver))
            filenames = glob.glob('%s-*-bug.json' % (distro))
            if 0 == len(filenames):
                print("And we don't have any database for %s" % (distro))
                print("Program terminates now :(")
                return
#       Return the last (newest) database with the same kernel / distro
        fn = filenames[-1]
        print('We will use %s as an alternative' % (fn))
        print("* It might cause some false alarms")
    if os.path.isdir('/proc/acpi/button/lid'):
        print('Checking touchpad/mouse')
        xinput_detect()
    print('Scanning components...')
    INPdev = parser_input()
    USBdev = parser_usb()
    PCIdev = parser_pci()
    PNPdev = parser_pnp()
    ALLdev = chain(INPdev, USBdev, PCIdev, PNPdev)
    SUBtmp = []
    print('Loading database...')
    with open(fn, 'r') as database:
        dict_db = json.load(database)
    print('Running component check...')
    for dev in ALLdev:
        # Special case: Parse the Subsystem for Audio
        if dev.group('SUB') in dict_db['Audio']:
            # In lspci & lsusb, only the Subsystem will be duplicated, we will
            # collect them into a temporary list then de-duplicate it later.
            found = True
            SUBtmp.append(dev.group('SUB'))
        for cat in dict_db:
            if dev.group('COMP') in dict_db[cat]:
                found = True
                for bugs in dict_db[cat][dev.group('COMP')]:
                    printer(dev.group('COMP'), bugs, cat)
    SUBtmp = sorted(set(SUBtmp))
#   Currently we have only Audio bugs recorded in subsystem
    for dev in SUBtmp:
        for bugs in dict_db['Audio'][dev]:
            printer(dev, bugs, 'Audio')
    print('Checking common issues...')
    with open(fn_common, 'r') as database:
        dict_db = json.load(database)
    for cat in dict_db:
        # Skip the Bluetooth category if there is no BT
        if 'Bluetooth' == cat:
            if not subprocess.check_output("hciconfig"):
                continue
        if distro in dict_db[cat]:
            found = True
            for bugs in dict_db[cat][distro]:
                printer(distro, bugs, cat)
    if not found:
        print('No other known issue found on your system')

if __name__ == "__main__":
    main()
