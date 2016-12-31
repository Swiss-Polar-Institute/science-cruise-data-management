import os
from django.conf import settings
from data_storage_management import utils


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

    def run(self):
        mounted = Importer._mount(self.ip, self.shared_volume, self.username, self.password)

        source_directory_path = os.path.join(mounted, self.source_directory)
        destination_directory_path = os.path.join(settings.BASE_STORAGE_DIRECTORY,
                                                  self.destination_directory)

        print("From: {} To: {}".format(source_directory_path, destination_directory_path))
        utils.rsync_copy(source_directory_path, destination_directory_path)
        Importer._umount(mounted)

    @staticmethod
    def _mount(ip, shared_resource, username='guest', password=None):
        mount_point = "/mnt/importfromstaging/{}".format(shared_resource)

        if not os.path.isdir(mount_point):
            os.mkdir(mount_point)

        if password is None:
            password_options = "guest"
        else:
            password_options = "password={}".format(password)

        utils.exe(["sudo",
                 "mount",
                 "-t", "cifs",
                 "-o", "ro,username={},{}".format(username, password_options),
                 "//{}/{}".format(ip, shared_resource),
                 mount_point])

        return mount_point

    @staticmethod
    def _umount(mount_point):
        utils.execute(["sudo", "umount", mount_point])