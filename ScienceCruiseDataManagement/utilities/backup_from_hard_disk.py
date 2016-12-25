#!/usr/bin/python3

# to be changed so it's not a command
from django.core.management.base import BaseCommand, CommandError
import time
import os
import configparser


class Command(BaseCommand):
    help = 'Copies the hard disk into the storage area. Registers the hard disk if needed'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def handle(self, *args, **options):
        copy_connected_hard_disk = CopyConnectedHardDisk()
        directory = options['directory']

        call_command('importcountries', os.path.join(directory, "countries.csv"))
        call_command('importorganisations', os.path.join(directory, "organisations.csv"))


def read_config():
    config = configparser.ConfigParser()
    file_to_read = os.path.join(os.getenv("HOME"), ".config", "science_cruise_data_copy.conf")
    config.read(file_to_read)
    return config

def detect_hard_disk():
    config = read_config()
    base_directory = config['General']['from']
    for section in config.sections():
        if section == "General":
            continue

        from_directory = os.path.join(base_directory, config['section']['from'])

        if os.path.isdir(from_directory):
            return from_directory

    print("Hard disk not found")
    exit(1)

def detect_to():
    config = read_config()

    destination_directory = config['General']['to']

    destination_directory_test = os.path.join(destination_directory, "ACSM")

    if os.path.exists(destination_directory_test):
        return destination_directory

    print("Destination not found")
    exit(1)

def copy(from_directory, to_directory):
    print("Should copy from {} to {}".format(from_directory, to_directory))
    return

def main():
    from_directory = detect_hard_disk()
    to_directory = detect_to()

    copy(from_directory, to_directory)

if __name__ == "__main__":
    main()