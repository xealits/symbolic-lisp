#!/usr/bin/python3

import argparse
import logging

from nsp_lis import lisp_eval, parse, List, lispstr


def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        input_string = input(prompt)
        if not input_string.strip(): continue

        val = lisp_eval(parse(input_string))
        if val is not None: 
            print(lispstr(val))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "run tests and start repl",
        epilog = """Example:\nrlwrap python lis_sym.py\nrlwrap python lis_sym.py --debug"""
        )

    parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    repl()

