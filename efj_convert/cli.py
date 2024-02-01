#!/usr/bin/env python3

import sys
import argparse

from efj_convert.logbook import build_logbook
from efj_convert.expand import expand_efj
from efj_convert.validate import validate
from efj_convert.night import add_night_data


def _args():
    parser = argparse.ArgumentParser(
        description=(
            'Process an Electronic Flight Journal file into various'
            'useful formats.'))
    parser.add_argument('format',
                        choices=['logbook', 'expand', 'validate', 'night'])
    return parser.parse_args()


def main() -> int:
    args = _args()
    if args.format == "logbook":
        print(build_logbook(sys.stdin.read()))
        return 0
    elif args.format == "expand":
        output, messages = expand_efj(sys.stdin.read())
        print(output)
        print(messages, file=sys.stderr)
    elif args.format == "night":
        output, messages = add_night_data(sys.stdin.read())
        print(output)
        print(messages, file=sys.stderr)
    elif args.format == "validate":
        print(validate(sys.stdin.read()))
    return -1


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
