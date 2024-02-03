#!/usr/bin/env python3

import sys
import argparse
from typing import Optional
import os.path

import efj_parser
from efj_convert.logbook import build_logbook
from efj_convert.expand import expand_efj
import efj_convert.summary as summary
from efj_convert.night import add_night_data
from efj_convert.config import build_config, aircraft_classes


def _args():
    parser = argparse.ArgumentParser(
        description=(
            'Process an Electronic Flight Journal file into various'
            'useful formats.'))
    parser.add_argument('format',
                        choices=['logbook', 'expand', 'night', 'summary',
                                 'config'])
    parser.add_argument('-c', '--config', default=None)
    return parser.parse_args()


def _config(filename: Optional[str]) -> str:
    if filename and os.path.exists(filename):
        with open(filename) as f:
            return f.read()
    else:
        for filename in (os.path.expanduser("~/.efjconvert"),
                         os.path.expanduser("~/.config/efjconvert")):
            if os.path.exists(filename):
                with open(filename) as f:
                    return f.read()
    return ""


def main() -> int:
    args = _args()
    try:
        if args.format == "logbook":
            ac_classes = aircraft_classes(_config(args.config))
            print(build_logbook(sys.stdin.read(), ac_classes))
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
        elif args.format == "config":
            sys.stdout.write(
                build_config(sys.stdin.read(),
                             _config(args.config)))
        else:
            return -1
        return 0
    except efj_parser.ValidationError as ve:
        print(str(ve), file=sys.stderr)
        return -1


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
