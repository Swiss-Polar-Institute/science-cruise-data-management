import subprocess
import glob
import os
import datetime

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

def log(message):
    f = open(os.path.join(os.environ["HOME"], "logs", "importer.log"), "a")
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    f.write("{} {}\n".format(now, message))
    f.close()


def rsync_copy(origin, destination):
    origin = glob.glob(origin)

    return execute(["rsync",
             "-rvt"] + origin + [destination], print_command=True)


def execute(cmd, abort_if_fails=False, print_command=False):
    if print_command:
        print("** Execute: {}".format(" ".join(cmd)))

    p = subprocess.Popen(cmd)
    p.communicate()[0]
    retval = p.returncode

    if retval != 0 and abort_if_fails:
        print("Command: _{}_ failed, aborting...".format(cmd))
        exit(1)

    return retval