#!/usr/bin/env python3

import re
import datetime as dt

import efj_parser as ep
import nightflight.night as night  # type:ignore
from nightflight.airport_nvecs import airfields as af  # type:ignore


def add_night_data(in_: str) -> str:
    """Add night data to eFJ format text file in string form.

    :param in_: An eFJ format text file in string form.
    :return: The input string modified to include night hours. Any previously
        marked night flying is left unmodified.
    """
    out = []
    re_sec = re.compile(r"\A(\w*/\w* \d{4}/\d{4})(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ != "sector" or ret.conditions.night > 0:
            out.append(line)
            return
        try:
            from_ = af[ret.airports.origin]
            to = af[ret.airports.dest]
        except KeyError:
            raise ep.ValidationError(
                line_num, "Airport(s) not in database", line)
        end = ret.start + dt.timedelta(minutes=ret.total)
        dur = night.night_duration(from_, to, ret.start, end)
        if not dur:
            out.append(line)
            return
        ldg = ""
        if not ret.landings.night and night.night_p(to, end):
            ldg = " ln"
        if dur == ret.total:
            flags = " n"
        else:
            flags = f" n:{round(dur)}{ldg}"
        mo = re_sec.match(line)
        assert mo
        out.append(f"{mo.group(1)}{flags}{mo.group(2)}")
    ep.Parser().parse(in_, callback)
    return "\n".join(out)


def expand_efj(in_: str) -> str:
    """Expand short dates (e.g. ++) and omitted airports, leaving all other
    lines intact.

    :param in_: An eFJ text file as a string
    :return: An eFJ text file as a string with short dates and omitted airports
        expanded to full form.
    """
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
    return "\n".join(out)


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


def add_ins_flag(in_: str) -> str:
    out = []
    re_sec = re.compile(r"\A(\w*/\w* \d{4}/\d{4})\s*(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ != "sector" or ret.roles.instructor:
            out.append(line)
        else:
            mo = re_sec.match(line)
            assert mo
            out.append(f"{mo.group(1)} ins {mo.group(2)}")
    ep.Parser().parse(in_, callback)
    return "\n".join(out)


def add_vfr_flag(in_: str) -> str:
    out = []
    re_sec = re.compile(r"\A(\w*/\w* \d{4}/\d{4})\s*(.*)\Z")

    def callback(line, line_num, type_, ret):
        if type_ != "sector" or ret.conditions.ifr < ret.total:
            out.append(line)
        else:
            mo = re_sec.match(line)
            assert mo
            out.append(f"{mo.group(1)} v {mo.group(2)}")
    ep.Parser().parse(in_, callback)
    return "\n".join(out)
