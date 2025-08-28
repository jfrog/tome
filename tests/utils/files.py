import os
import platform
import tempfile

TOME_TESTS_FOLDER = os.getenv('TOME_TESTS_FOLDER', None)
if TOME_TESTS_FOLDER and not os.path.exists(TOME_TESTS_FOLDER):
    os.makedirs(TOME_TESTS_FOLDER)


def get_cased_path(name):
    if platform.system() != "Windows":
        return name
    if not os.path.isabs(name):
        name = os.path.abspath(name)

    result = []
    current = name
    while True:
        parent, child = os.path.split(current)
        if parent == current:
            break

        child_cased = child
        if os.path.exists(parent):
            children = os.listdir(parent)
            for c in children:
                if c.upper() == child.upper():
                    child_cased = c
                    break
        result.append(child_cased)
        current = parent
    drive, _ = os.path.splitdrive(current)
    result.append(drive)
    return os.sep.join(reversed(result))


def temp_folder(create_dir=True):
    t = tempfile.mkdtemp(suffix='tome_tmp', dir=TOME_TESTS_FOLDER)
    # Make sure that the temp folder is correctly cased, as tempfile return lowercase for Win
    t = get_cased_path(t)
    # necessary for Mac OSX, where the temp folders in /var/ are symlinks to /private/var/
    t = os.path.realpath(t)
    path = "path with spaces"
    nt = os.path.join(t, path)
    if create_dir:
        os.makedirs(nt)
    return nt


def temp_file(suffix='', prefix='tmp'):
    folder_path = temp_folder()
    fd, name = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=folder_path)
    os.close(fd)
    return name