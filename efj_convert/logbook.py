import importlib.resources as res
import datetime as dt

from efj_parser import Parser


def _get_template():
    template = (res.files("efj_convert")
                .joinpath("logbook-template.html")
                .open().read())
    for old, new in (("{", "{{"), ("}", "}}"),
                     ("<!--{{", "{"), ("}}-->", "}")):
        template = template.replace(old, new)
    return template


SESP, MESP, MP = range(3)

ac_class = {
    "737": MP,
    "A319": MP,
    "A320": MP,
    "A321": MP,
    "C310": MESP,
    "C402": MESP,
    "C404": MESP,
    "C406": MESP,
    "C47": MP,
    "L188": MP
}


def build_logbook(in_: str) -> str:
    _, sectors = Parser().parse(in_)
    rows = []
    for c, s in enumerate(sectors):
        cells = [f"{s.start:%d/%m/%Y}",
                 s.airports.origin, f"{s.start:%H%M}",
                 s.airports.dest,
                 f"{s.start + dt.timedelta(minutes=s.total):%H%M}",
                 s.aircraft.type_, s.aircraft.reg]
        duration = f"{s.total // 60}:{s.total % 60:02}"
        aircraft_class = ac_class.get(s.aircraft.type_, SESP)
        if aircraft_class == MP:
            cells.extend(["", "", duration])
        elif aircraft_class == SESP:
            cells.extend(["✓", "", ""])
        else:
            cells.extend(["", "✓", ""])
        cells.append(duration)
        cells.append(s.captain)
        cells.extend([str(s.landings.day or ""), str(s.landings.night or "")])
        night, ifr = "", ""
        if s.conditions.night:
            night = f"{s.conditions.night // 60}:{s.conditions.night % 60:02}"
        if s.conditions.ifr:
            ifr = f"{s.conditions.ifr // 60}:{s.conditions.ifr % 60:02}"
        cells.extend([night, ifr])
        cells.extend([f"{X // 60}:{X % 60:02}" if X else ""
                      for X in (s.roles.p1 + s.roles.p1s, s.roles.p2,
                                s.roles.put, s.roles.instructor)])
        cells.append(s.comment)
        rows.append(f"<tr><td>{'</td><td>'.join(cells)}</td></tr>")
    return _get_template().format(rows="\n".join(rows))
