#!/usr/bin/env python3

import sys
import argparse

from efj_convert.logbook import build_logbook
from efj_convert.expand import expand_efj


def _args():
    parser = argparse.ArgumentParser(
        description=(
            'Process an Electronic Flight Journal file into various'
            'useful formats.'))
    parser.add_argument('format',
                        choices=['logbook', 'expand'])
    return parser.parse_args()


def main() -> int:
    args = _args()
    if args.format == "logbook":
        print(build_logbook(sys.stdin.read()))
        return 0
    if args.format == "expand":
        output, messages = expand_efj(sys.stdin.read())
        print(output)
        print(messages, file=sys.stderr)
    return -1


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
