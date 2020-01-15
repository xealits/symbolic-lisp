import logging
import subprocess
from shutil import which


def prepare_command(comname):
    def command(*args):
        comlist  = [comname.data]
        comlist += [a.data for a in args]
        logging.debug(repr(comlist))
        return subprocess.run(comlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command

def find_command(comname):
    logging.debug(comname)
    if which(comname.data):
        return prepare_command(comname)
    else:
        return None

def get_exit(completed_process):
    return completed_process.returncode

def get_stdout(completed_process):
    return completed_process.stdout

def get_stderr(completed_process):
    return completed_process.stderr
