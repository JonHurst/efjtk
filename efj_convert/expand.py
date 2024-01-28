#!/usr/bin/env python3

import sys
import re
import datetime as dt

import nightflight.night as nf  # type: ignore
from nightflight.airport_nvecs import airfields as af  # type: ignore


def expand_efj(in_: str) -> tuple[str, str]:
    input_ = in_.splitlines()
    re_date = re.compile(r"\A(\d{4}-\d{2}-\d{2})\Z")
    re_nextdate = re.compile(r"\A(\++)\Z")
    re_sector = re.compile(r"(\w+)?/(\w+)?\s*(\d{4})/(\d{4})\s*([^#]*)?(#.+)?")
    date = dt.date.min
    origin, dest = "", ""
    out, messages = [], []
    for c, line in enumerate(input_):
        if mo := re_date.match(line):
            date = dt.datetime.strptime(mo.group(1), "%Y-%m-%d").date()
            out.append(line)
        elif mo := re_nextdate.match(line):
            date += dt.timedelta(len(mo.group(1)))
            out.append(f"{date:%Y-%m-%d}")
        elif mo := re_sector.match(line):
            origin, dest = (mo.group(1) or dest, mo.group(2) or origin)
            flags = mo.group(5).split()
            if "n" not in [X[0] for X in flags]:
                ts = dt.datetime.strptime(mo.group(3), '%H%M').time()  # Off blocks
                te = dt.datetime.strptime(mo.group(4), '%H%M').time()  # On blocks
                off_ = dt.datetime.combine(date, ts)
                on_ = dt.datetime.combine(date, te)
                if on_ < off_:
                    on_ += dt.timedelta(1)
                duration = (on_ - off_) / dt.timedelta(minutes=1)
                try:
                    night_dur = int(nf.night_duration(af[origin], af[dest],
                                                      off_, on_))
                    if night_dur:
                        if night_dur == duration:
                            flags.append("n")
                        else:
                            flags.append(f"n:{night_dur}")
                            if nf.night_p(af[dest], on_):
                                flags.append("ln")
                except KeyError:
                    messages.append(f"Airfield not known: line {c} : {line}")
            out.append((f"{origin}/{dest} {mo.group(3)}/{mo.group(4)} "
                   f"{' '.join(flags)} {mo.group(6) or ''}").strip())
        else:
            out.append(line)
    return "\n".join(out), "\n".join(messages)
