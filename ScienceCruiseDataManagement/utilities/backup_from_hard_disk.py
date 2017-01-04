#!/usr/bin/python3

import json
import time
import os
import configparser
import argparse
import glob
import requests
import pprint
import datetime
import subprocess
import glob
import configparser
from termcolor import colored

def read_config(key):
    cp = configparser.ConfigParser()
    cp.read(os.path.join(os.getenv("HOME"), ".config", "science_cruise_data_copy.conf"))

    value = cp.get("General", key)

    return value


def collect_uuids():
    uuids = []

    for link_source in glob.glob("/dev/disk/by-uuid/*"):
        link_destination = os.readlink(link_source)

        uuids.append((os.path.basename(link_source), os.path.basename(link_destination)))

    return uuids


def longest_device_name(devices):
    longest = devices[0]

    for device in devices:
        if len(device[1]) > len(longest[1]):
            longest=device

    return longest


def print_colored(color, message):
    print(colored(message, color, attrs=['bold']))


def detect_hard_disk():
    print_colored('blue', "Please unplug the hard disk and press ENTER")
    input()

    uuids_before = collect_uuids()
    print_colored('blue', "Please plug in the hard disk and wait -no need to press enter")

    step = 0
    second_counter = 4
    while True:
        uuids_after = collect_uuids()
        new_uuids = list(set(uuids_after) - set(uuids_before))

        if step==0 and len(new_uuids) != 0:
            step=1
            starts_at=datetime.datetime.now()
            print_colored('white', "Waiting for partitions...")

        elif step==1 and second_counter < 0:
            break
        elif step == 1:
            print_colored('white', "Waiting... {} seconds".format(second_counter))
            second_counter -= 1

        time.sleep(1)

    uuids_after = collect_uuids()
    new_uuids=list(set(uuids_after)-set(uuids_before))

    device = longest_device_name(new_uuids)

    return device


def execute(cmd, abort_if_fails=False):
    print_colored('white', "Will execute: {}".format(cmd))

    p=subprocess.Popen(cmd)
    p.communicate()[0]
    retcode=p.returncode

    if retcode != 0 and abort_if_fails:
        print_colored('red', "Command: _{}_ failed, aborting...".format(cmd))
        exit(1)

    return retcode

def add_directory_update(directory_id):
    data = {}
    data['id'] = directory_id

    r=requests.post(read_config("base_url") + "/api/data_storage/add_directory_update.json", json.dumps(data))

    json_data = r.json()

    assert json_data['status'] == 'ok'


def process_hard_disk(hard_disk):
    uuid = hard_disk[0]
    partition = hard_disk[1]

    to_exec = ["sudo", "umount", partition]
    execute(to_exec)

    hard_disk_mount_point = read_config("hard_disk_mount_point")
    to_exec = ["sudo", "umount", hard_disk_mount_point]
    execute(to_exec)

    to_exec = ["sudo", "mount", "-o", "ro", "/dev/disk/by-uuid/{}".format(uuid),hard_disk_mount_point]
    execute(to_exec, True)

    hard_disk_information = requests.get(read_config("base_url") + "/api/data_storage/hard_disk.json", {'hard_disk_uuid':uuid}).json()

    if 'error' in hard_disk_information:
        print_colored('red', "Error: hard disk not found")
        pprint.pprint(hard_disk_information)
        print_colored('red', "Aborting...")
        exit(1)

    print_colored('blue', "Will process these directories:")
    print_colored('blue', "====================")
    pprint.pprint(hard_disk_information)
    print_colored('blue', "====================")

    print_colored('green', "Proceed? (Y/n)")
    answer = input()

    if not (answer == '' or answer == 'Y' or answer == 'y'):
        print_colored('red', "Exiting...")
        exit(1)

    for directory in hard_disk_information['directories']:
        source = directory['source']

        if source.startswith("/"):
            source = source[1:]

        destination = directory['destination']
        directory_id = directory['id']

        wall_clock = datetime.datetime.now().timestamp()

        to_exec = ["rsync", "-rt",
            os.path.join(read_config("hard_disk_mount_point"),source) + "/",
            os.path.join(read_config("destination_base_directory"),destination)]

        print_colored('blue', "Will execute: {}".format(to_exec))
        retval = execute(to_exec)

        if retval == 0:
            print()
            add_directory_update(directory_id)
            print_colored('blue', "It took: {} seconds".format(int(datetime.datetime.now().timestamp() - wall_clock)))
        else:
            print()
            print_colored('red', "Error: failed uploading directory")
            exit(1)

def add_directory(hard_disk_uuid, relative_path):
    data = {}
    data['hard_disk_uuid'] = hard_disk_uuid
    data['relative_path'] = relative_path

    print_colored('blue', "Do you want to add for the hard disk '{}' the directory '{}'? (Y/n)".format(hard_disk_uuid, relative_path))
    answer = input()

    if answer == '' or answer == 'y' or answer == 'Y':
        r = requests.put(read_config("base_url") + "/api/data_storage/hard_disk.json", data=json.dumps(data))

        if r.json()['status'] != 'ok':
            print_colored('red', "Failed uploading {} {} ".format(hard_disk_uuid, relative_path))

            print_colored('white', "\nReceived from server\n: ".r.json())

            print_colored('red', "Now exiting...")

            exit(1)


def create_hard_disk(hard_disk_uuid, hard_disk_mount_point, base_directory):
    if base_directory == "/":
        base_directory = ""

    for directory in glob.glob(os.path.join(hard_disk_mount_point, base_directory, "*")):
        if os.path.isdir(directory):
            relative_path = directory[len(hard_disk_mount_point)+1:]
            add_directory(hard_disk_uuid, relative_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handles how to copy things to the backups")
    parser.add_argument("--detect-new-hard-disk", action='store_true', help="Provides the UUID of the new hard disk")
    parser.add_argument("--process-hard-disk", action='store_true', help="Requests the directories to be processed from a registered hard disk")
    parser.add_argument("--add-hard-disk", type=str)
    parser.add_argument("--base-directory", type=str)
    parser.add_argument("--hard-disk-mount-point", type=str)

    args = parser.parse_args()

    if args.detect_new_hard_disk:
        uuid=detect_hard_disk()
        print_colored('green', "Found device: {}".format(uuid[0]))
    elif args.process_hard_disk:
        hard_disk=detect_hard_disk()
        process_hard_disk(hard_disk)
    elif args.add_hard_disk and args.hard_disk_mount_point and args.base_directory:
        create_hard_disk(args.add_hard_disk,
                         os.path.abspath(args.hard_disk_mount_point), # Import for some os.path.join()
                         os.path.abspath(args.base_directory))
