#!/usr/bin/python3

import argparse
import logging
#import readline # it blocks rlwrap
from textwrap import dedent
from os.path import isfile
import sys

from sym_lis3 import GlobalEnv, parse, List, lispstr


def handy_input(prompt='> '):
    'An `input` with 2 newline characters ending.'

    all_input_strings = ''

    # prompt the user for input
    given_input = input(prompt)
    all_input_strings += given_input

    # and handle the two newline ending
    while given_input:
        # if previous input is not empty
        # then prompt again
        given_input = input('')
        all_input_strings += '\n' + given_input

    logging.debug('input script:\n%s' % all_input_strings)
    return all_input_strings

def repl(prompt='sym_repl> '):
    "A prompt-read-eval-print loop."
    g = GlobalEnv()
    while True:
        input_program = handy_input(prompt)
        if not input_program.strip(): continue

        try:
            val = g.eval_str(input_program)
            if val is not None: 
                print(lispstr(val))
        except Exception as e:
            print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "run tests and start repl",
        epilog = 'Example:' + dedent("""
        rlwrap python3 sym_repl.py
        rlwrap python3 sym_repl.py --debug
        rlwrap ./sym_repl.py""")
        )

    parser.add_argument("--script", type=str, help="execute a script file")
    parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.script:
        assert isfile(args.script)

        g = GlobalEnv()
        with open(args.script) as f:
            script = f.read()
            if not script.strip():
                logging.warning("the script file is empty: %s" % args.script)

            val = g.eval_str(script)
            # print final value of the script
            if val is not None:
                print(lispstr(val), file=sys.stderr)

    else:
        repl()

