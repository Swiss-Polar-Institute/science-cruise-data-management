import subprocess


def rsync_copy(origin, destination):
    execute(["rsync",
             "-rvt",
             origin,
             destination])


def execute(cmd, abort_if_fails=False):
    p=subprocess.Popen(cmd)
    p.communicate()[0]
    retcode=p.returncode

    if retcode != 0 and abort_if_fails:
        print("Command: _{}_ failed, aborting...".format(cmd))
        exit(1)


"""
def _filter_only_dirs(list_of_paths):
    dirs = []

    for path in list_of_paths:
        if os.path.isdir(path):
            dirs.append(path)

    return dirs

def _print_directories(message, directories):
    directories.sort()
    print(message)
    for directory in directories:
        print("  {}".format(directory))
"""