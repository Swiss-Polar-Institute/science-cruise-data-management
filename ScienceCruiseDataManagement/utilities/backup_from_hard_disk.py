#!/usr/bin/python3

import time
import os
import configparser
import argparse
import glob
import requests
import pprint
import datetime
import subprocess

HARD_DISK_MOUNT_POINT="/mnt/data_science"
DESTINATION_BASE_DIRECTORY="/tmp/ace_data"


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


def detect_hard_disk():
    print("Please unplug the hard disk and press ENTER")
    input()

    uuids_before = collect_uuids()
    print("Please plug the hard disk and wait")

    step=0
    while True:
        uuids_after = collect_uuids()
        new_uuids = list(set(uuids_after) - set(uuids_before))

        if step==0 and len(new_uuids) != 0:
            step=1
            starts_at=datetime.datetime.now()

        elif step==1 and (datetime.datetime.now()-starts_at).seconds >= 5:
            break

    uuids_after = collect_uuids()
    new_uuids=list(set(uuids_after)-set(uuids_before))

    device = longest_device_name(new_uuids)

    return device


def execute(cmd, abort_if_fails=False):
    print("Will execute: {}".format(cmd))

    p=subprocess.Popen(cmd)
    p.communicate()[0]
    retcode=p.returncode

    if retcode != 0 and abort_if_fails:
        print("Command: _{}_ failed, aborting...".format(cmd))
        exit(1)


def process_hard_disk(uuid):
    to_exec = ["sudo","umount","/mnt/data_science"]
    execute(to_exec)

    to_exec = ["sudo","mount","/dev/disk/by-uuid/{}".format(uuid),HARD_DISK_MOUNT_POINT]
    execute(to_exec, True)

    hard_disk_information = requests.get("http://localhost:8000/api/data_storage/hard_disk.json", {'hard_disk_uuid':uuid}).json()
    pprint.pprint(hard_disk_information)
    print("Proceed? (Ctrl+C for NO)")
    input()

    for directory in hard_disk_information['directories']:
        source=directory['source']
        destination=directory['destination']

        to_exec=["rsync","-arv",
            os.path.join(HARD_DISK_MOUNT_POINT,source) + "/",
            os.path.join(DESTINATION_BASE_DIRECTORY,destination)]

        print("To exec:",to_exec)
        input()
        execute(to_exec)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handles how to copy things to the backups")
    parser.add_argument("--detect-new-hard-disk", help="Provides the UUID of the new hard disk", action='store_true')
    parser.add_argument("--process-hard-disk", help="Requests the directories to be processed from a registered hard disk", action='store_true')
    parser.add_arguments("--add-hard-disk", action="store_str")
    parser.add_arguments("--base-directory", action="store_str")

    args = parser.parse_args()

    if args.detect_new_hard_disk:
        uuid=detect_hard_disk()
        print(uuid)
    elif args.process_hard_disk:
        hard_disk=detect_hard_disk()
        process_hard_disk(hard_disk[0])
    elif args.add_hard_disk and args.base_directory:
        print("Should create hard disk")
