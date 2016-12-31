from django.core.management.base import BaseCommand, CommandError

from data_storage_management import cifs_utils
from data_storage_management.models import Directory
from django.conf import settings


class Command(BaseCommand):
    help = 'Copies data from staging areas into the ace_data'

    def add_arguments(self, parser):
        parser.add_argument('import', type=str)

    def handle(self, *args, **options):
        db_staging_directories = Directory.objects.all().filter(staging_directory__isnull=False)

        for staging_directory in db_staging_directories:
            importer = cifs_utils.Importer(settings.NAS_IP,
                                         settings.NAS_STAGING_VOLUME,
                                         "guest",
                                         None,
                                         staging_directory.source_directory,
                                         staging_directory.destination_directory)

            importer.run()

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
