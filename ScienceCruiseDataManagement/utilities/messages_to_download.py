#!/usr/bin/python3

import argparse
import glob
import os

# This should be in the remote server in /root/messages_to_download.py

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
