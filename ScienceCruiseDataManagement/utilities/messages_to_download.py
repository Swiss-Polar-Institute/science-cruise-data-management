#!/usr/bin/python3

import argparse
import glob
import os

# This should be in the remote server in /root/messages_to_download.py

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

def unread_messages_files():
    messages_files = []

    for home_directory in glob.glob("/home/*"):
        new_message_directory = os.path.join(home_directory, "Maildir/new")

        new_mail_files = glob.glob(os.path.join(new_message_directory, "*"))

        for new_mail_file in new_mail_files:
            messages_files.append(new_mail_file)

    return messages_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    for message in unread_messages_files():
        print(message)
