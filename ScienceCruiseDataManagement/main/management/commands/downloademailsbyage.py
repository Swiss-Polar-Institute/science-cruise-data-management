from django.core.management.base import BaseCommand, CommandError
import datetime
from main.models import Email
from django.conf import settings
import os
import shutil
import time


class Command(BaseCommand):
    help = 'Connects to the server and download emails per priority'

    def add_arguments(self, parser):
        parser.add_argument('server_or_file',
                            type=str,
                            help="Creates the Django users from the Person table")

    def handle(self, *args, **options):
        download_mails_by_age = DownloadMailsByAge(options['server_or_file'])
        download_mails_by_age.fetch_list_of_messages()
        download_mails_by_age.print_stats()
        download_mails_by_age.download_messages()


class Message:
    def __init__(self, mail_file_path):
        self.username = None
        self.timestamp = None
        self.date_time = None

        self.username = Message.username(mail_file_path)
        self.timestamp = Message.timestamp(mail_file_path)
        self.date_time = Message.timestamp_to_date_time(self.timestamp)

    @staticmethod
    def username(filepath):
        return filepath.split("/")[2]

    @staticmethod
    def timestamp_to_date_time(timestamp):
        date_time = datetime.datetime.fromtimestamp(timestamp)
        return date_time

    @staticmethod
    def timestamp(mail_file_path):
        basename = os.path.basename(mail_file_path)
        timestamp = basename.split(".")
        timestamp = int(timestamp[0])
        return timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp


class MessageDownloader:
    def __init__(self, username):
        self.username = username
        self.temporary_directory = "fetchmail-temporary"
        shutil.rmtree(self.temporary_directory, ignore_errors=True)
        os.makedirs(self.temporary_directory)

    def execute_fetchmail(self, file_name):
        pidfile = os.path.join(self.temporary_directory, "pid")
        while True:
            cmd = "fetchmail --fetchmailrc {} --pidfile {}".format(file_name, pidfile)
            exit_status = execute_log(cmd)
            print("Exit status: {}".format(exit_status))
            if exit_status == 0 or exit_status == 1 or exit_status == 13:
                break
            else:
                print("Will try again to fetch for {}".format(self.username))
                time.sleep(2)

    def fetchmail(self):
        file_name = os.path.join(self.temporary_directory, "fetchmailrc-downloader")
        fetchmailrc = open(file_name, "w")
        fetchmailrc.write(self.fetchmailrc())
        fetchmailrc.close()

        # Ensures permissions needed by fetchmail
        os.chmod(file_name, 0o700)

        self.execute_fetchmail(file_name)

    def fetchmailrc(self):
        email_address = "{}@ace-expedition.net".format(self.username)

        config = {}
        config['username'] = self.username
        config['imap_server'] = settings.IMAP_SERVER
        config['limit'] = settings.MAXIMUM_EMAIL_SIZE
        config['password'] = Email.objects.get(email_address=email_address).server_password

        config_txt = """defaults
fetchall
flush
pass8bits
limit {limit}

poll {imap_server}
    proto imap
    user {username}
    pass "{password}"
    ssl
    sslfingerprint "DA:3A:8A:41:09:33:DF:0D:83:85:61:AE:CF:E4:B6:DA"
    to {username}
""".format(**config)

        return config_txt


def execute_log(cmd):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print("{} will execute: {}".format(now, cmd))
    exit_status = os.system(cmd)
    return exit_status


class DownloadMailsByAge:
    def __init__(self, server_or_file):
        self.server_or_file = server_or_file
        self.messages = None
        self.usernames_to_download = None

    def fetch_list_of_messages(self):
        if self.server_or_file == "server":
            self.messages = self.download_list_of_file_messages_from_server()
        elif self.server_or_file == "file":
            self.messages = self.read_messages_file()
        else:
            assert False

        self.messages.sort()
        self.usernames_to_download = self.prioritize_usernames()

        print("")
        print("List to download ({}):".format(len(self.usernames_to_download)))
        print("================")
        for email in self.usernames_to_download:
            print(email)

    def download_messages(self):
        for username in self.usernames_to_download:
            downloader = MessageDownloader(username)
            downloader.fetchmail()

    def download_list_of_file_messages_from_server(self):
        output_file = datetime.datetime.utcnow().strftime("usernames-to-download-%Y-%m-%d %H:%M:%S")
        while True:
            cmd = "ssh -o ConnectTimeout=120 -o ServerAliveInterval=120 -v root@{} ./messages_to_download.py > '{}'".format(settings.IMAP_SERVER, output_file)
            exit_status = execute_log(cmd)

            if exit_status == 0:
                break
            else:
                print("Trying again to fetch the list of usernames to download")

        messages = self.read_messages_file(output_file)
        return messages

    def read_messages_file(self, file_path):
        print("Will read from: {}".format(file_path))
        fp = open(file_path, "r")

        messages = []
        for line in fp.readlines():
            line = line.rstrip()
            message = Message(line)
            messages.append(message)

        fp.close()
        return messages

    def print_stats(self):
        now = int(datetime.datetime.utcnow().strftime("%s"))
        age_seconds = 0

        oldest_messages = {}

        for message in self.messages:
            age_seconds += (now - message.timestamp)

            if message.username not in oldest_messages:
                oldest_messages[message.username] = message
            else:
                if oldest_messages[message.username].timestamp > message.timestamp:
                    oldest_messages[message.username] = message

        age_hours = age_seconds / 3600
        print("")
        print("Stats")
        print("=====")
        print("Age: {:.2f} hours".format(age_hours))
        print("Messages: {}".len(self.messages))

        print("Average age of message: {:.2f}".format(age_hours/self.messages))

        print("Oldest messages per user")
        print("========================")
        print("UTC now: {}".format(datetime.datetime.utcnow()))
        for username in oldest_messages.keys():
            print("{} {}".format(oldest_messages[username].date_time, username))

    def sort_messages(self):
        self.messages.sort()

    def prioritize_usernames(self):
        to_download = []

        for message in self.messages:
            if message.username not in to_download:
                to_download.append(message.username)

        return to_download