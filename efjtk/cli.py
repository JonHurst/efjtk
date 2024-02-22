#!/usr/bin/env python3

import sys
import argparse
from typing import Optional
import os.path

import efj_parser
import efjtk.convert
import efjtk.modify
from efjtk.config import build_config, aircraft_classes


def _args():
    parser = argparse.ArgumentParser(
        description=(
            """Process an electronic Flight Journal (eFJ) file. Tools to aid in
            manual creation of eFJ files (expand, night, vfr, ins, fo) and
            tools to convert to useful formats (logbook, summary) are included.
            Also included is a tool to help create a config file, which is
            required for generation of the FCL.050 logbook."""))
    parser.add_argument('format',
                        choices=['expand', 'night', 'vfr', 'ins', 'fo',
                                 'logbook',  'summary',
                                 'config'])
    parser.add_argument('-c', '--config', default=None)
    return parser.parse_args()


def _config(filename: Optional[str]) -> str:
    if filename and os.path.exists(filename):
        with open(filename) as f:
            return f.read()
    else:
        for filename in (os.path.expanduser("~/.efjtkrc"),
                         os.path.expanduser("~/.config/efjtkrc")):
            if os.path.exists(filename):
                with open(filename) as f:
                    return f.read()
    return ""


_func_map = {
    "expand": efjtk.modify.expand_efj,
    "night": efjtk.modify.add_night_data,
    "summary": efjtk.convert.build_summary,
    "vfr": efjtk.modify.add_vfr_flag,
    "fo": efjtk.modify.add_fo_role_flag,
    "ins": efjtk.modify.add_ins_flag,
}


def main() -> int:
    args = _args()
    data = sys.stdin.read()
    try:
        if args.format == "logbook":
            ac_classes = aircraft_classes(_config(args.config))
            print(efjtk.convert.build_logbook(data, ac_classes))
        elif args.format == "config":
            sys.stdout.write(
                build_config(data, _config(args.config)))
        elif args.format in _func_map:
            print(_func_map[args.format](data))
        else:
            return -1
        return 0
    except efj_parser.ValidationError as ve:
        print(str(ve), file=sys.stderr)
        return -1
    except efjtk.convert.UnknownAircraftType as t:
        print(f"No class for type: {t}", file=sys.stderr)
        return -3


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
