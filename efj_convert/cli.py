#!/usr/bin/env python3

import sys
import argparse

import efj_parser
from efj_convert.logbook import build_logbook
from efj_convert.expand import expand_efj
import efj_convert.summary as summary
from efj_convert.night import add_night_data


def _args():
    parser = argparse.ArgumentParser(
        description=(
            'Process an Electronic Flight Journal file into various'
            'useful formats.'))
    parser.add_argument('format',
                        choices=['logbook', 'expand', 'night', 'summary'])
    return parser.parse_args()


def main() -> int:
    args = _args()
    try:
        if args.format == "logbook":
            print(build_logbook(sys.stdin.read()))
        elif args.format == "expand":
            output, messages = expand_efj(sys.stdin.read())
            print(output)
            print(messages, file=sys.stderr)
        elif args.format == "night":
            output, messages = add_night_data(sys.stdin.read())
            print(output)
            print(messages, file=sys.stderr)
        elif args.format == "summary":
            print(summary.build(sys.stdin.read()))
        else:
            return -1
        return 0
    except efj_parser.ValidationError as ve:
        print(str(ve), file=sys.stderr)
        return -1


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
