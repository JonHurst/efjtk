#!/usr/bin/env python3

import sys
import argparse

from efj_convert.logbook import build_logbook


def _args():
    parser = argparse.ArgumentParser(
        description=(
            'Process an Electronic Flight Journal file into various'
            'useful formats.'))
    parser.add_argument('format',
                        choices=['logbook'])
    return parser.parse_args()


def main() -> int:
    args = _args()
    if args.format == "logbook":
        print(build_logbook(sys.stdin.read()))
        return 0
    return -1


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
