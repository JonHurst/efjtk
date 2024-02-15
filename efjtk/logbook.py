import importlib.resources as res
import datetime as dt
import configparser as cp

from efj_parser import Parser, Sector


class UnknownAircraftClass(Exception):
    """Aircraft type with no matching class encountered"""

    def __init__(self, type_):
        self.missing_type = type_


def _get_template():
    template = (res.files("efj_convert")
                .joinpath("logbook-template.html")
                .open().read())
    for old, new in (("{", "{{"), ("}", "}}"),
                     ("<!--{{", "{"), ("}}-->", "}")):
        template = template.replace(old, new)
    return template


def _aircraft_class_cells(
        sector: Sector,
        ac_classes: cp.SectionProxy,
        duration: str
) -> list[str]:
    if sector.aircraft.class_:
        aircraft_class = sector.aircraft.class_
    else:
        try:
            aircraft_class = ac_classes[sector.aircraft.type_]
        except KeyError:
            raise UnknownAircraftClass(sector.aircraft.type_)
    if aircraft_class == "mc":
        return ["", "", duration]
    if aircraft_class == "spse":
        return ["✓", "", ""]
    if aircraft_class == "spme":
        return ["", "✓", ""]
    raise UnknownAircraftClass(sector.aircraft.type_)


def build_logbook(in_: str, ac_classes: cp.SectionProxy) -> str:
    _, sectors = Parser().parse(in_)
    rows = []
    for c, s in enumerate(sectors):
        cells = [f"{s.start:%d/%m/%Y}",
                 s.airports.origin, f"{s.start:%H:%M}",
                 s.airports.dest,
                 f"{s.start + dt.timedelta(minutes=s.total):%H:%M}",
                 s.aircraft.type_, s.aircraft.reg]
        duration = f"{s.total // 60}:{s.total % 60:02}"
        cells.extend(_aircraft_class_cells(s, ac_classes, duration))
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
