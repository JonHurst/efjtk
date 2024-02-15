#!/usr/bin/env python3

import sys
import argparse
from typing import Optional
import os.path

import efj_parser
from efjtk.logbook import build_logbook
# from efjtk.expand import expand_efj
import efjtk.summary as summary
# from efjtk.night import add_night_data
from efjtk.config import build_config, aircraft_classes
# from efjtk.vfr import add_vfr_flag
# from efjtk.fo import add_fo_role_flag
# from efjtk.ins import add_ins_flag
import efjtk.modify


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
        for filename in (os.path.expanduser("~/.efjrc"),
                         os.path.expanduser("~/.config/efjrc")):
            if os.path.exists(filename):
                with open(filename) as f:
                    return f.read()
    return ""


_func_map = {
    "expand": efjtk.modify.expand_efj,
    "night": efjtk.modify.add_night_data,
    "summary": summary.build,
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
            print(build_logbook(data, ac_classes))
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


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
