from django.core.management.base import BaseCommand, CommandError
from main.models import Person, Email
from main.utils import remove_accents
from main.models import Leg
import subprocess
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates email addresses and passwords and adds them to the email table'

    def add_arguments(self, parser):
        parser.add_argument('command', type=str, help="Command can be generatepasswords or generatefetchmailrc")

    def handle(self, *args, **options):
        if options['command'] == "generateemails":
            self.generate_emails()
        elif options['command'] == "generatefetchmailrc":
            self.generate_fetchmailrc()
        elif options['command'] == "generateusersserver":
            self.generate_users_server()
        elif options['command'] == "printpasswords":
            self.print_passwords()
        elif options['command'] == "generatewebmailusers":
            self.generate_webmail_users()
        elif options['command'] == "invalidateusersotherlegs":
            self.invalidate_users_from_other_legs()

    def print_passwords(self):
        for email in Email.objects.all().order_by("email_address"):
            print("***** Welcome to ACE mail! *****")
            print()
            print("Email address: {}   Password: {}".format(email.email_address, email.webmail_password))
            print()
            print("A FEW TIPS:")
            print("- Set up your out of office to this address but please DO NOT set up any email forwarding. Ask contacts not to send you attachments and to check their junk folders for replies. Emails are limited to a size of 100 KB.")
            print("- Please note that this email address and all messages will not be usable or accessible when you leave the ship, so please save anything you may need whilst still on board.")
            print()
            print("- Access your email here: http://ace-mail.lan (you will need to connect to the ship's network with an ethernet cable)")
            print()
            print("**Keep an eye on the whiteboard in the office to find out when the email system is up and running.**")
            print()
            print("----------------------------------------------------------------------------------------------------")
            print()

    def generate_email(self, person):
        firstname = remove_accents(person.name_first.replace(" ", "")).decode("ascii")
        surname = remove_accents(person.name_last.replace(" ", "")).decode("ascii")

        # email = str(firstname) + '.' + str(surname) + '@ace-expedition.net'
        email = "{}@ace-expedition.net".format(self.username(person))

        return email

    def username(self, person):
        firstname = remove_accents(person.name_first.replace(" ", "")).decode("ascii")
        surname = remove_accents(person.name_last.replace(" ", "")).decode("ascii")

        return "{}.{}".format(firstname.lower(), surname.lower())

    def generate_password(self, length):
        with subprocess.Popen(["pwgen", str(length)], stdout=subprocess.PIPE) as proc:
            password = proc.stdout.read().decode("ascii").strip()

        return password

    def generate_emails(self):
        query_set = Person.objects.all()

        for person in query_set:
            email_address = self.generate_email(person)
            webmail_password = self.generate_password(6)
            server_password = self.generate_password(20)

            email = Email()
            email.person = person
            email.email_address = email_address
            email.webmail_password = webmail_password
            email.server_password = server_password

            email.save()

    def generate_users_server(self):
        for email in Email.objects.all().order_by("email_address"):
            print("useradd --create-home {}".format(self.username(email.person)))
            print("echo {}:{} | chpasswd".format(self.username(email.person), email.server_password))

    def generate_webmail_users(self):
        for email in Email.objects.all().order_by("email_address"):
            print("useradd --shell /bin/false --create-home {}".format(self.username(email.person)))
            print("echo {}:{} | chpasswd".format(self.username(email.person), email.webmail_password))
            print("echo {} | saslpasswd2 -u ace-expedition.net {}".format(email.webmail_password, self.username(email.person)))
            print("##############")

    def generate_fetchmailrc(self):
        print("defaults")
        print("fetchall")
        print("flush")
        print("pass8bits")
        print("limit {}".format(settings.MAXIMUM_EMAIL_SIZE))
        print()

        active_leg = Leg.current_active_leg()

        for email in Email.objects.filter(person__leg=active_leg).order_by("email_address"):
            # person = email.person
            #
            # print(person.leg)
            print("poll 46.226.111.64")
            print("  proto imap")
            print("  user {}".format(self.username(email.person)))
            print("  pass \"{}\"".format(email.server_password))
            print("  ssl")
            print("  sslfingerprint \"DA:3A:8A:41:09:33:DF:0D:83:85:61:AE:CF:E4:B6:DA\"")
            print("  to {}".format(self.username(email.person)))
            print("")

    def invalidate_users_from_other_legs(self):
        active_leg = Leg.current_active_leg()
        print("# the active leg is: ", active_leg)
        for email in Email.objects.order_by("email_address"):
            legs = email.person.leg.all()
            if active_leg in legs:
                print("# the user {} is in the active leg".format(email.email_address))
            else:
                print("echo {}:{}DISABLED | chpasswd".format(self.username(email.person), email.webmail_password))
