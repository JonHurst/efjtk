#!/usr/bin/env python3

import sys
import argparse
from typing import Callable
import datetime as dt

import efj_parser
import efjtk.convert
import efjtk.modify
import efjtk.gec
from efjtk.version import VERSION


def _args():
    parser = argparse.ArgumentParser(
        description=(
            """Process an electronic Flight Journal (eFJ) file. Tools to aid in
            manual creation of eFJ files (expand, night, vfr, ins, fo) and
            tools to convert to useful formats (logbook, summary, cumulative)
            are included. Also included is a tool to help create a config file,
            which is required for generation of the FCL.050 logbook."""))
    parser.add_argument('format',
                        choices=['expand', 'night', 'vfr', 'ins', 'fo',
                                 'logbook',  'summary', 'cumulative',
                                 'version', 'gec'])
    parser.add_argument(
        '-f', '--from', dest='from_', metavar="FROM", default=None,
        help="Restrict output to dates including and after FROM")
    parser.add_argument(
        '-t', '--to', default=None,
        help="Restrict output to dates up to but excluding TO")
    return parser.parse_args()


_func_map: dict[str, Callable[[str, tuple[dt.date, dt.date]], str]] = {
    "expand": efjtk.modify.expand_efj,
    "night": efjtk.modify.add_night_data,
    "vfr": efjtk.modify.add_vfr_flag,
    "fo": efjtk.modify.add_fo_role_flag,
    "ins": efjtk.modify.add_ins_flag,
    "gec": efjtk.gec.report,
    "logbook": efjtk.convert.build_logbook,
    "cumulative": efjtk.convert.build_cumulative,
    "summary": efjtk.convert.build_summary,
}


def main() -> int:
    args = _args()
    if args.format == "version":
        print(VERSION)
        return 0
    try:
        date_from = args.from_ and dt.date.fromisoformat(args.from_)
        date_to = args.to and dt.date.fromisoformat(args.to)
    except ValueError as e:
        print(e, file=sys.stderr)
        return -4
    date_range = (date_from, date_to)
    data = sys.stdin.read()
    try:
        if args.format in _func_map:
            print(_func_map[args.format](data, date_range))
            return 0
        else:
            return -1
    except efj_parser.ValidationError as ve:
        print(str(ve), file=sys.stderr)
        return -1


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
