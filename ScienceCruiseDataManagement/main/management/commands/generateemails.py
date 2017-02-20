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
        parser.add_argument('--leg', type=int, help="Specifies the leg for the commands that accepts it, e.g. printemails")

    def handle(self, *args, **options):
        if options['command'] == "generateemails":
            self.generate_emails(options['leg'])
        elif options['command'] == "generatefetchmailrc":
            self.generate_fetchmailrc()
        elif options['command'] == "generateusersserver":
            self.generate_users_server()
        elif options['command'] == "printpasswords":
            self.print_passwords(options['leg'])
        elif options['command'] == "generatewebmailusers":
            self.generate_webmail_users()
        elif options['command'] == "invalidateusersotherlegs":
            self.invalidate_users_from_other_legs()
        elif options['command'] == "printemails":
            self.print_emails(options['leg'])

    def print_emails(self, leg):
        wanted_leg = Leg.objects.get(number=leg)
        print("name, email")
        for person in Person.objects.order_by("name_first"):
            legs = person.leg.all()
            if wanted_leg in legs:
                print("{} {},{}".format(person.name_first, person.name_last, self.generate_email(person)))


    def print_passwords(self, leg):
        added = 0
        skipped = 0
        leg2 = Leg.objects.filter(number=2)

        for email in Email.objects.filter(person__leg__number=leg).order_by("email_address"):
            if leg2[0] in email.person.leg.all():
                skipped += 1
                continue

            print("***** Welcome to ACE mail! *****")
            print()
            print("Email address: {}".format(email.email_address))
            print("Username: {}".format(self.username(email.person)))
            print("Password: {}".format(email.webmail_password))
            print()
            print("A FEW TIPS:")
            print("- Set up your out reply and mention this this address but please DO NOT set up any email forwarding. Ask contacts not to send you attachments and to check their junk folders for replies.")
            print("- Emails are limited to a size of 200 KB. If a bigger email is sent you will receive a notification. If you need to send a bigger email come and speak with the data team.")
            print("- Please note that this email address and all messages will not be usable or accessible when you leave the ship, so please save anything you may need whilst still on board.")
            print()
            print("- To access your email: connect to the expedition network (cable in the cabins and labs, or WiFi on the coffee room next to the mess) and go to http://ace-mail.lan (or http://192.168.20.40 for Macs)")
            print()
            print("----------------------------------------------------------------------------------------------------")
            print()
            added += 1

        print("Added: {}".format(added))
        print("Skipped (leg3 and leg2): {}".format(skipped))

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

    def generate_emails(self, leg):
        query_set = Person.objects.all().filter(leg__number=leg)

        created = 0
        skipped = 0
        for person in query_set:
            email_address = self.generate_email(person)
            webmail_password = self.generate_password(6)
            server_password = self.generate_password(20)

            email_existed = Email.objects.filter(email_address=email_address)

            if not email_existed:
                email = Email()
                email.person = person
                email.email_address = email_address
                email.webmail_password = webmail_password
                email.server_password = server_password

                email.save()

                print("created:", person)

                created += 1
            else:
                skipped += 1

        print("Created:", created)
        print("Skipped:", skipped)

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
