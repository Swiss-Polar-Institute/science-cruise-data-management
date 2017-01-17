import subprocess
import glob
import os
import datetime


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