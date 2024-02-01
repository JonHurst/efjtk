#!/usr/bin/env python3

import re
import datetime as dt

import efj_parser as ep
import nightflight.night as night  # type:ignore
from nightflight.airport_nvecs import airfields as af  # type:ignore


def add_night_data(in_: str) -> tuple[str, str]:
    out = []
    messages = []
    re_sec = re.compile(r"\A(\w*/\w* \d{4}/\d{4})(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ != "sector" or ret.conditions.night > 0:
            out.append(line)
            return
        try:
            from_ = af[ret.airports.origin]
            to = af[ret.airports.dest]
        except ValueError:
            messages.append(f"Airport not found in {ret.airports}")
            out.append(line)
            return
        end = ret.start + dt.timedelta(minutes=ret.total)
        dur = night.night_duration(from_, to, ret.start, end)
        if not dur:
            out.append(line)
            return
        ldg = " ln" if night.night_p(to, end) else ""
        if dur == ret.total:
            flags = " n"
        else:
            flags = f" n:{round(dur)}{ldg}"
        mo = re_sec.match(line)
        assert mo
        out.append(f"{mo.group(1)}{flags}{mo.group(2)}")
    ep.Parser().parse(in_, callback)
    return "\n".join(out), "\n".join(messages)
