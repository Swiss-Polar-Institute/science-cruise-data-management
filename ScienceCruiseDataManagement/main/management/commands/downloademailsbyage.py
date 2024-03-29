from django.core.management.base import BaseCommand, CommandError
import datetime
from main.models import Email, Leg
from django.conf import settings
import os
import shutil
import time
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

TEMP_DIRECTORY = os.path.join(os.getenv("HOME"), "downloademailsbyage")

class Command(BaseCommand):
    help = 'Connects to the server and download emails per priority'

    def add_arguments(self, parser):
        parser.add_argument('server_or_file',
                            type=str,
                            help="Creates the Django users from the Person table")

    def handle(self, *args, **options):
        os.makedirs(TEMP_DIRECTORY, exist_ok=True)
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
        self.temporary_directory = os.path.join(TEMP_DIRECTORY, "fetchmail-temporary")
        shutil.rmtree(self.temporary_directory, ignore_errors=True)
        os.makedirs(self.temporary_directory)
        self.current = None
        self.total = None
        self.oldest_message_date_time = None

    def set_progress(self, current, total, oldest_message_date_time):
        self.current = current
        self.total = total
        self.oldest_message_date_time = oldest_message_date_time

    def execute_fetchmail(self, file_name):
        print("")
        pidfile = os.path.join(self.temporary_directory, "pid")
        print("* Downloading messages for {} (user {} of {})".format(self.username, self.current, self.total))
        starts = datetime.datetime.utcnow()

        while True:
            oldest_message_minutes = datetime.datetime.utcnow() - self.oldest_message_date_time
            print("Oldest message datetime: {:.2f} minutes old".format((oldest_message_minutes.seconds/60)))
            cmd = "fetchmail --timeout 120 --fetchmailrc {} --pidfile {}".format(file_name, pidfile)
            exit_status = execute_log(cmd)
            print("Exit status: {}".format(exit_status))
            if exit_status == 0 or exit_status == 1 or exit_status == 13 or exit_status == 256:
                break
            else:
                print("Will try again to fetch for {}".format(self.username))
                time.sleep(2)

        ends = datetime.datetime.utcnow()
        elapsed = ends - starts
        print("To download all the messages it took: {:.2f} minutes".format(elapsed.seconds/60))


    def fetchmail(self):
        try:
            email_address = "{}@ace-expedition.net".format(self.username)
            Email.objects.get(email_address=email_address)
        except ObjectDoesNotExist:
            print("No password for user {}, not fetching emails".format(self.username))
            return

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
    print("{} Executing: {}".format(now, cmd))
    exit_status = os.system(cmd)
    return exit_status


class DownloadMailsByAge:
    def __init__(self, server_or_file):
        self.server_or_file = server_or_file
        self.messages = []
        self.usernames_to_download = []
        self.oldest_messages = {}

    def fetch_list_of_messages(self):
        if self.server_or_file == "server":
            self.messages = self.download_list_of_file_messages_from_server()
        elif self.server_or_file == "file":
            self.messages = self.read_messages_file()
        else:
            assert False

        self.messages.sort()
        self.usernames_to_download = self.prioritize_usernames()

    def download_messages(self):
        for (index, username) in enumerate(self.usernames_to_download):
            if username == "admin":
                continue
            downloader = MessageDownloader(username)
            downloader.set_progress(index+1, len(self.usernames_to_download), self.oldest_messages[username].date_time)
            downloader.fetchmail()

    def download_list_of_file_messages_from_server(self):
        output_file = datetime.datetime.utcnow().strftime("usernames-to-download-%Y-%m-%d %H:%M:%S")
        output_file_path = os.path.join(TEMP_DIRECTORY, output_file)
        while True:
            cmd = "ssh -o ConnectTimeout=120 -o ServerAliveInterval=120 root@{} ./messages_to_download.py > '{}'".format(settings.IMAP_SERVER, output_file_path)
            exit_status = execute_log(cmd)

            if exit_status == 0:
                break
            else:
                print("Trying again to fetch the list of usernames to download")

            # Allows Control+C to cancel
            time.sleep(1)

        messages = self.read_messages_file(output_file_path)
        return messages

    def read_messages_file(self, file_path):
        print("Will read from: {}".format(file_path))
        fp = open(file_path, "r")

        messages = []
        for line in fp.readlines():
            line = line.rstrip()
            message = Message(line)

            if self.username_in_email_active_legs(message.username):
                messages.append(message)
            else:
                print("Skipping {}".format(message.username))

        fp.close()
        return messages


    def username_in_email_active_legs(self, username):
        email_active_legs = Leg.current_active_leg()

        email = Email.objects.get(username=username)

        for user_in_leg in email.person.leg.all():
            # Sometimes maybe checking emails from different legs is needed,
            # so there is this commented out code
            #if user_in_leg in email_active_legs:
            #    return True
            if user_in_leg == email_active_legs:
                return True

        return False

    def print_stats(self):
        print("")
        print("Stats")
        print("=====")

        if len(self.messages) == 0:
            print("No messages, no stats")
            return

        now = datetime.datetime.utcnow()
        now_timestamp = int(now.strftime("%s"))
        total_age_seconds = 0

        messages_per_user = {}
        self.oldest_messages = {}

        for message in self.messages:
            total_age_seconds += (now_timestamp - message.timestamp)
            username = message.username

            if username not in self.oldest_messages:
                self.oldest_messages[username] = message
            else:
                if self.oldest_messages[username].timestamp > message.timestamp:
                    self.oldest_messages[username] = message

            if username not in messages_per_user:
                messages_per_user[username] = 1
            else:
                messages_per_user[username] += 1

        total_age_minutes = total_age_seconds / 60
        print("Total combined age: {:.2f} minutes".format(total_age_minutes))
        print("Number of Messages: {}".format(len(self.messages)))

        print("Average age of message: {:.2f} minutes".format(total_age_minutes/len(self.messages)))

        print("")
        print("Oldest messages per user")
        print("========================")
        for username in self.usernames_to_download:
            oldest_message_date_time = self.oldest_messages[username].date_time
            seconds_ago = (now-oldest_message_date_time).seconds
            minutes_ago = seconds_ago / 60
            print("{}\t{:.2f} minutes (number of messages: {})".format(username, minutes_ago, messages_per_user[username]))

        print("")

    def sort_messages(self):
        self.messages.sort()

    def prioritize_usernames(self):
        to_download = []

        for message in self.messages:
            if message.username not in to_download:
                to_download.append(message.username)

        return to_download