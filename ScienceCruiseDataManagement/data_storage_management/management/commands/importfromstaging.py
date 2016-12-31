from django.core.management.base import BaseCommand, CommandError

from data_storage_management import cifs_utils
from data_storage_management.models import Directory, NASResource
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Copies data from staging areas into the ace_data'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)

    def handle(self, *args, **options):
        if options['action'] == 'import':
            db_nas_directories = Directory.objects.all().filter(nas_resource__isnull=False)

            print("Will import the NAS directories. To be processed: {}".format(len(db_nas_directories)))
            for nas_directory in db_nas_directories:
                importer = cifs_utils.Importer(settings.NAS_IP,
                                               nas_directory.nas_resource.shared_resource,
                                               "guest",
                                               None,
                                               nas_directory.source_directory,
                                               nas_directory.destination_directory)

            importer.run()

        elif options['action'] == 'check':
            nas_shares = NASResource.objects.all()

            directories_in_nas = []
            for nas_share in nas_shares:
                mounted = cifs_utils.Importer.mount(settings.NAS_IP, nas_share.shared_resource)
                files_and_dirs = os.listdir(mounted)

                for file_or_dir in files_and_dirs:
                    if os.path.isdir(os.path.join(mounted, file_or_dir)):
                        report_if_directory_no_exist(file_or_dir, nas_share.shared_resource)

                cifs_utils.Importer.umount(mounted)


def report_if_directory_no_exist(directory, shared_resource):
    query_set = Directory.objects.all().filter(nas_resource__isnull=False, source_directory=directory)
    exists_in_db = query_set.exists()

    if not exists_in_db:
        print("Directory {} from shared resource {} is not in the database".format(directory, shared_resource))

# class Importer:
#     def __init__(self):
#         pass
#
#     def run(self):
#         nas_files_and_dirs = glob.glob(settings.NAS_STAGING_MOUNT_POINT + "/*")
#
#         nas_directories = Importer._filter_only_dirs(nas_files_and_dirs)
#
#         all_db_staging_directories = Directory.objects.all().filter(staging_directory__isnull=False)
#
#         for staging_directory in all_db_staging_directories:
#             mounted = cifs_utils.mount(staging_directory.staging_directory.shared_resource)
#
#             source_directory_path = os.path.join(mounted, staging_directory.source_path)
#             destination_directory_path =
#
#             print("From: {} To: {}".format(source_directory_path, settings.BASE_STORAGE_DIRECTORY))
#             cifs_utils.copy(source_directory_path, os.path.join(settings.BASE_STORAGE_DIRECTORY, staging_directory.destination))
#
#             cifs_utils.umount(mounted)
#
#         Importer._print_directories("Directories in NAS not in the DB (NOT copied, should be added in the DB):", nas_directories)
#
#     @staticmethod
#     def _mount(shared_resource):
#         mount_point = "/mnt/importfromstaging/{}".format(shared_resource)
#
#         if not os.path.isdir(mount_point):
#             os.mkdir(mount_point)
#
#         execute(["sudo",
#                  "mount",
#                  "-t","cifs",
#                  "-o","ro,username=guest,guest",
#                  "//{}/{}".format(settings.NAS_IP, shared_resource),
#                  mount_point])
#
#         return mount_point
#
#     @staticmethod
#     def _copy(origin, destination):
#         execute(["rsync",
#                 "-rvt",
#                 origin,
#                 destination])
#
#     @staticmethod
#     def _umount(mount_point):
#         execute(["sudo", "umount", mount_point])
#
#     @staticmethod
#     def _filter_only_dirs(list_of_paths):
#         dirs = []
#
#         for path in list_of_paths:
#             if os.path.isdir(path):
#                 dirs.append(path)
#
#         return dirs
#
#     @staticmethod
#     def _print_directories(message, directories):
#         directories.sort()
#         print(message)
#         for directory in directories:
#             print("  {}".format(directory))
#
#
# def execute(cmd, abort_if_fails=False):
#     p = subprocess.Popen(cmd)
#     p.communicate()[0]
#     retcode = p.returncode
#
#     if retcode != 0 and abort_if_fails:
#         print("Command: _{}_ failed, aborting...".format(cmd))
#         exit(1)
