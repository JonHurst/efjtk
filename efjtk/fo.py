#!/usr/bin/env python3

import re

import efj_parser as ep


def add_fo_role_flag(in_: str) -> str:
    out = []
    re_sec = re.compile(r"\A(\w*/\w* \d{4}/\d{4})\s*(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ != "sector" or ret.roles.p1 != ret.total:
            out.append(line)
        else:
            mo = re_sec.match(line)
            assert mo
            if ret.landings.day or ret.landings.night:
                out.append(f"{mo.group(1)} p1s {mo.group(2)}")
            else:
                out.append(f"{mo.group(1)} p2 {mo.group(2)}")
    ep.Parser().parse(in_, callback)
    return "\n".join(out)
