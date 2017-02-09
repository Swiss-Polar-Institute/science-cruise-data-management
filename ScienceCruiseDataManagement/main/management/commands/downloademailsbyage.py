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
            exit_status = os.system(cmd)
            if exit_status == 0:
                break
            else:
                print("Will try again to fetch for {}".format(self.username))
                time.sleep(2)

    def fetchmail(self):
        file_name = os.path.join(self.temporary_directory, "fetchmailrc-downloader")
        fetchmailrc = open(file_name, "w")
        fetchmailrc.write(self.fetchmailrc())
        fetchmailrc.close()

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


class DownloadMailsByAge:
    def __init__(self, server_or_file):
        if server_or_file == "server":
            self.messages = self.download_list_of_file_messages_from_server()
        elif server_or_file == "file":
            self.messages = self.load_list_of_file_messages_from_file()
        else:
            assert False

        self.sort_messages()
        self.to_download = self.prioritize_usernames()
        print("List to download:")

        for email in self.to_download:
            print(email)

    def download_list_of_file_messages_from_server(self):
        output_file = datetime.datetime.utcnow().strftime("usernames-to-download-%Y-%m-%d %H:%M:%S")
        while True:
            cmd = "ssh root@ace-expedition.net ./messages_to_download.py > '{}'".format(output_file)
            print("Executing: {}".format(cmd))
            exit_status = os.system(cmd)

            if exit_status == 0:
                break
            else:
                print("Trying again to fetch the list of usernames to download")

        self.load_list_of_file_messages_from_file(output_file)

    def load_list_of_file_messages_from_file(self, file_path):
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
        age = 0

        oldest_messages = {}

        for message in self.messages:
            age += (now - message.timestamp)

            if message.username not in oldest_messages:
                oldest_messages[message.username] = message
            else:
                if oldest_messages[message.username].timestamp > message.timestamp:
                    oldest_messages[message.username] = message

        print("Stats")
        print("=====")
        print("age: {} seconds".format(age))
        print("age: {:.2f} hours".format(age / 3600))
        print("age: {:.2f} days".format(age / 3600 / 24))
        print("")

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

    def download_messages(self):
        for username in self.to_download:
            downloader = MessageDownloader(username)
            downloader.fetchmail()