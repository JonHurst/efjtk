#!/usr/bin/env python3

import re

import efj_parser as ep


def expand_efj(in_: str) -> tuple[str, str]:
    out = []
    re_sec = re.compile(r"\A\w*/\w*\s*(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ == "short_date":
            out.append(f"{ret:%Y-%m-%d}")
        elif type_ == "sector":
            if mo := re_sec.match(line):
                out.append(
                    f"{ret.airports.origin}/{ret.airports.dest} {mo.group(1)}")
            else:
                out.append(line)
        else:
            out.append(line)
    ep.Parser().parse(in_, callback)
    return "\n".join(out), ""
