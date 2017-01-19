from django.core.management.base import BaseCommand, CommandError
from main.models import Person, Email
from main.utils import remove_accents
import subprocess


class Command(BaseCommand):
    help = 'Creates email addresses and passwords and adds them to the email table'

    def add_arguments(self, parser):
        parser.add_argument('command', type=str, help="Command can be generatepasswords or generatefetchmailrc")

    def handle(self, *args, **options):
        if options['command'] == "generateemails":
            self.generate_emails()
        elif options['command'] == "generatefetchmailrc":
            self.generate_fetchmailrc()
        elif options['command'] == "generateusers":
            self.generate_users()
        elif options['command'] == "printpasswords":
            self.print_passwords()

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
        email = "{}.{}@ace-expedition.net".format(firstname.lower(), surname.lower())

        return email

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
