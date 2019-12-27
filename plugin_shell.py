import logging
import subprocess, shutil

def prepare_command(comname):
    def command(*args):
        comlist = [comname] + list(args)
        logging.debug(repr(comlist))
        return subprocess.run(comlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command

def find_command(comname):
    logging.debug(comname)
    if shutil.which(comname):
        return prepare_command(comname)
    else:
        return None

def get_exit(completed_process):
    return completed_process.returncode

def get_stdout(completed_process):
    return completed_process.stdout

def get_stderr(completed_process):
    return completed_process.stderr
