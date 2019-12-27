#!/usr/bin/python3

import argparse
import logging
#import readline # it blocks rlwrap
from textwrap import dedent

from sym_lis import lisp_eval_str, parse, List, lispstr


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
    while True:
        input_program = handy_input(prompt)
        if not input_program.strip(): continue

        val = lisp_eval_str(input_program)
        if val is not None: 
            print(lispstr(val))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "run tests and start repl",
        epilog = 'Example:' + dedent("""
        rlwrap python3 sym_repl.py
        rlwrap python3 sym_repl.py --debug
        rlwrap ./sym_repl.py""")
        )

    parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    repl()

