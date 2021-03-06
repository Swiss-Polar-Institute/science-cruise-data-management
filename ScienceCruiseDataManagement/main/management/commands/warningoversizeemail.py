from django.core.management.base import BaseCommand, CommandError
import socket
import imaplib
import sys
import email
from django.conf import settings
from main.models import Email, EmailOversizeNotified, Leg
import pprint
from django.core.mail import send_mail

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

class Command(BaseCommand):
    help = 'Sends an email to users with messages bigger than the settings MAXIMUM_EMAIL_SIZE'

    def add_arguments(self, parser):
        parser.add_argument('action', help="[notify|dry-run]", type=str)
        parser.add_argument('user', help="Specify a username to check if for a specific user. Leave it blank or 'all' for all users", type=str)

    def handle(self, *args, **options):
        if options['action'] == "dry-run":
            dry_run = True
        elif options['action'] == "notify":
            dry_run = False
        else:
            print("Unknown action, should be dry-run or notify")
            exit(1)

        if 'user' in options:
            user = options['user']
        else:
            user = 'all'

        notify = Notify(dry_run)

        if user == "all":
            notify.check_all_users()
        else:
            notify.check_user(options['user'])


class Notify:
    def __init__(self, dry_run):
        self._dry_run = dry_run
        self._imap = None

    def _get_message_headers(self, message_uuid, size):
        resp, data = self._imap.uid('FETCH', message_uuid, '(RFC822.HEADER)')

        msg = email.message_from_bytes(data[0][1])

        information = {}
        information['From'] = str(email.header.make_header(email.header.decode_header(msg['From'])))
        information['Date'] = msg['Date']

        if 'Subject' not in msg:
            information['Subject'] = ""
        else:
            information['Subject'] = str(email.header.make_header(email.header.decode_header(msg['Subject'])))

        information['Size'] = "{} KB".format(int(size / 1024))
        information['_size_in_bytes'] = size
        information['_imap_uuid'] = message_uuid
        information['Uuid'] = message_uuid

        return information

    def _notified_for_email(self, headers, email_address):
        email_object = Email.objects.get(email_address=email_address)

        # encodes as ascii to avoid problems with an old Mysql
        subject = headers['Subject'].encode('ascii', 'ignore')
        from_email = headers['From'].encode('ascii', 'ignore')

        email_oversized_notified = EmailOversizeNotified.objects.filter(date_string=headers['Date'],
                                                                        size=headers['_size_in_bytes'],
                                                                        #subject=subject,
                                                                        to_email=email_object,
                                                                        #from_email=from_email,
                                                                        imap_uuid=headers['_imap_uuid'])

        return len(email_oversized_notified) > 0

    def _save_headers_as_notified(self, headers_list, email_address):
        for headers in headers_list:
            already_notified = self._notified_for_email(headers, email_address)

            if already_notified:
                print("Already notified message. Not saving headers in the database")
                continue

            email_oversize = EmailOversizeNotified()
            email = Email.objects.get(email_address=email_address)

            # encodes as ascii to avoid problems with an old Mysql
            subject = headers['Subject'].encode('ascii', 'ignore')
            from_email = headers['From'].encode('ascii', 'ignore')

            email_oversize.to_email = email
            email_oversize.date_string = headers['Date']
            email_oversize.size = headers['_size_in_bytes']
            email_oversize.from_email = from_email
            email_oversize.subject = subject
            email_oversize.imap_uuid = headers['_imap_uuid']

            email_oversize.save()

    def _notify_user(self, headers_list, email_to_notify):
        pprint.pprint(headers_list)

        information = ""
        for headers in headers_list:
            headers['_To_Email'] = email_to_notify
            headers['_To_User'] = email_to_notify.split("@")[0]
            already_notified = self._notified_for_email(headers, email_to_notify)

            if already_notified:
                print("Already notified. Skipping sending notification")
                continue

            information += """From: {From}
To: {_To_Email}
Date: {Date}
Size: {Size}
Subject: {Subject}
UUID: {_To_User} {Uuid}

""".format(**headers)


        if len(information) == 0:
            # There are no messages to be notified
            return

        message_body = """Hello,

There are some oversized emails in your mailbox (see the bottom of this email for details).

You will not receive the oversized email and the attachment will not be downloaded.
We recommend you contact the sender and ask for a smaller version (<300 KB).

If it's really crucial to download the attachment, forward the details below for the
relevant email, to data@ace-expedition.net and we will try to download it. When it has
downloaded, you will receive an email telling you where you can find it.

{}

Data team
""".format(information)

        if self._dry_run == False:
            send_mail(
                 'Oversized email',
                 message_body,
                 'Data team <data@ace-expedition.net>',
                 [email_to_notify],
                 fail_silently=False,
            )

    def _process_mailbox(self, imap, email_to_notify):
        rv, sizes = imap.uid('FETCH', '1:*', '(RFC822.SIZE)')
        if rv != 'OK':
            print("No messages can't be retrieved!")
            return

        if sizes == [None]:
            print("No messages in the mailbox")
            return

        headers_for_oversized_messages = []
        for message_information_size in sizes:
            message_information_size = message_information_size.decode()
            message_information_size = message_information_size.replace("(", "")
            message_information_size = message_information_size.replace(")", "")

            (index_number, parenthesis_uid, message_uuid, rfc822_size, size) = message_information_size.split()
            message_uuid = message_uuid
            size = int(size)

            if size > settings.MAXIMUM_EMAIL_SIZE:
            # if size > 3000:
                headers = self._get_message_headers(message_uuid, size)
                headers_for_oversized_messages.append(headers)

        self._notify_user(headers_for_oversized_messages, email_to_notify)
        self._save_headers_as_notified(headers_for_oversized_messages, email_to_notify)

    def _get_imap_password(self, email_address):
        password = Email.objects.get(email_address=email_address).server_password

        return password

    def check_user(self, email_address):
        username = email_address.split("@")[0]
        password = self._get_imap_password(email_address)

        socket.setdefaulttimeout(30)
        self._imap = imaplib.IMAP4(settings.IMAP_SERVER)

        try:
            print("Login")
            rv, data = self._imap.login(username, password)
        except imaplib.IMAP4.error:
            print("Login failed for:", username)
            return

        print("Select INBOX")
        # the readonly=True is to avoid that the FETCH command
        # to check the sizes marks the messages as read
        rv, data = self._imap.select("INBOX", readonly=True)

        if rv == 'OK':
            print("Processing mailbox...")
            self._process_mailbox(self._imap, email_address)
            self._imap.close()
        else:
            print("ERROR: Unable to open mailbox", rv)
        self._imap.logout()

    def check_all_users(self):
        active_leg = Leg.current_active_leg()

        emails_active_leg = Email.objects.filter(person__leg=active_leg).order_by("email_address")

        for (index, email_account) in enumerate(emails_active_leg):
            while True:
                try:
                    print("Checking: {} {}/{}".format(email_account.email_address, index+1, len(emails_active_leg)))
                    self.check_user(email_account.email_address)
                    break
                except ConnectionResetError:
                    print("Connection Reset Error for user: {}. Trying again".format(email_account))
                except socket.timeout:
                    print("Connection timeout Error for user: {}. Trying again".format(email_account))
                except OSError:
                    print("Probably 'Network is unreachable' error for user {}. Trying again".format(email_account))

