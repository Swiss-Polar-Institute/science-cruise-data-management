import os
from django.conf import settings
from data_storage_management import utils
from data_storage_management.models import DirectoryImportLog


class Importer:
    def __init__(self, ip, shared_volume,
                 username, password,
                 source_directory, destination_directory):
        self.ip = ip
        self.shared_volume = shared_volume
        self.username = username
        self.password = password
        self.source_directory = source_directory
        self.destination_directory = destination_directory

        self.succeeded = False

    def run(self):
        self.succeeded = False
        print()
        print("****** Copying from: {} To: {}".format(self.source_directory, self.destination_directory))
        print()

        mounted = Importer.mount(self.ip, self.shared_volume, self.username, self.password)

        if mounted is None:
            print("!!!!! Can't mount //{}/{} Username: {} Password: {}".format(self.ip, self.shared_volume, self.username, self.password))
            return

        # In the next line: do not use os.path.join() (if self.source_directory is / it wouldn't work)
        source_directory_path = mounted + self.source_directory

        destination_directory_path = os.path.join(settings.BASE_STORAGE_DIRECTORY,
                                                  self.destination_directory)

        print()
        print("** From: {} To: {}".format(source_directory_path, destination_directory_path))
        print()
        retval = utils.rsync_copy(source_directory_path, destination_directory_path)

        if retval != 0:
            print("******** ATTENTION! //{}/{} Username: {} Password: {} From: {} To: {} could not be copied!".format(self.ip, self.shared_volume, self.username, self.password, source_directory_path, destination_directory_path))
        else:
            self.succeeded = True
        Importer.umount(mounted)

    def register_import(self, directory):
        directory_import = DirectoryImportLog()
        directory_import.directory = directory
        directory_import.success = self.succeeded

        directory_import.save()

    @staticmethod
    def mount(ip, shared_resource, username='guest', password=None):
        mount_point = "/mnt/importfromstaging/{}".format(shared_resource)

        if not os.path.isdir(mount_point):
            os.mkdir(mount_point)

        if password is None or password == '':
            password_options = "guest"
        else:
            password_options = "password={}".format(password)

        to_execute = ["sudo",
                 "mount",
                 "-t", "cifs",
                 "-o", "ro,username={},{}".format(username, password_options),
                 "//{}/{}".format(ip, shared_resource),
                 mount_point]

        retval = utils.execute(to_execute, print_command=True)

        if retval == 0:
            return mount_point
        else:
            return None

    @staticmethod
    def umount(mount_point):
        utils.execute(["sudo", "umount", mount_point], print_command=True)