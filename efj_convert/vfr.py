#!/usr/bin/env python3

import re

import efj_parser as ep


def add_vfr_flag(in_: str) -> str:
    out = []
    re_sec = re.compile(r"\A(\w*/\w* \d{4}/\d{4})\s*(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ != "sector":
            out.append(line)
        else:
            mo = re_sec.match(line)
            assert mo
            out.append(f"{mo.group(1)} v {mo.group(2)}")
    ep.Parser().parse(in_, callback)
    return "\n".join(out)
