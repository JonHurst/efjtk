import re

import efj_parser as ep


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
