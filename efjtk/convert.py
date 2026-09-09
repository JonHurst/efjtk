import configparser as cp
import importlib.resources as res
import datetime as dt

from typing import Optional
from html import escape

import efj_parser as ep


class UnknownAircraftType(Exception):
    """Aircraft type with no matching class encountered"""

    def __init__(self, type_):
        self.missing_type = type_


DateRange = tuple[Optional[dt.date], Optional[dt.date]]


def _get_template(filename):
    """Get and prepare a template from the package's resources

    :param filename: The name of the file as recorded in the 'efjtk' key's list
        under package_data in setup.py

    :returns: The template ready for str.format to use

    The template should use <!--{ and }--> to delimit the kwarg that str.format
    will replace. Use of { and } elsewhere in the template is suitably escaped.
    """
    template_file = res.files("efjtk").joinpath(filename)
    with template_file.open() as f:
        template = f.read()
    for old, new in (("{", "{{"), ("}", "}}"),
                     ("<!--{{", "{"), ("}}-->", "}")):
        template = template.replace(old, new)
    return template


def _duration(minutes):
    if minutes:
        return f"{minutes // 60}:{minutes % 60:02}"
    return ""


def _ac_class_tuple(
        s: ep.Sector,
        ac_classes: cp.SectionProxy
) -> tuple[int, int, int]:
    """Get minutes alloted to aircraft classes.

    :param s: The sector to process

    :param ac_classes: Effectively a case-insensitive dict mapping aircraft
        type to aircraft class (spse, spme or mc)

    :returns: A tuple of the form (SPSE, SPME, MC) where each cell is the
        minutes (as an integer) to allot to the associated class.

    :raises UnknownAircraftType: Raised if the class associated with a type is
        not available from the Sector object, nor from the ac_classes mapping.
    """
    if s.aircraft.class_:  # will be "" if no class assigned by parser
        aircraft_class = s.aircraft.class_
    else:
        try:
            aircraft_class = ac_classes[s.aircraft.type_]
        except KeyError:
            raise UnknownAircraftType(s.aircraft.type_)
    spse, spme, mc = (s.total if aircraft_class == X else 0
                      for X in ("spse", "spme", "mc"))
    return (spse, spme, mc)


def _row(cells: tuple[str, ...], class_: str = "") -> str:
    """Build an HTML table row from a tuple of strings

    :param cells: The strings representing the table cells

    :param class_: A string to assign to the row's class attribute

    :returns: A string containing a properly escaped HTML table row
    """
    c = class_ and f" class='{escape(class_)}'"
    inner = "".join(f"<td>{escape(X, False)}</td>" for X in cells)
    return f"<tr{c}>{inner}</tr>"


def build_logbook(
        in_: str,
        ac_classes: cp.SectionProxy,
        daterange: DateRange = (None, None)
) -> str:
    _, sectors = ep.Parser().parse(in_)
    rows = []
    for s in sorted(sectors):
        if daterange[0] and s.start.date() < daterange[0]:
            continue
        if daterange[1] and s.start.date() >= daterange[1]:
            break
        ac_class_t = _ac_class_tuple(s, ac_classes)
        cells = (
            f"{s.start:%d/%m/%Y}",  # Date
            s.airports.origin,  # Departure Place
            f"{s.start:%H:%M}",  # Departure Time
            s.airports.dest,  # Arrival Place
            f"{s.start + dt.timedelta(minutes=s.total):%H:%M}",  # Arrival Time
            s.aircraft.type_,  # Aircraft Type
            s.aircraft.reg,  # Aircraft Reg
            "✓" if ac_class_t[0] else "",  # SE tick
            "✓" if ac_class_t[1] else "",  # ME tick
            _duration(ac_class_t[2]),  # MC duration
            _duration(s.total),  # Total duration
            s.captain,  # PIC
            str(s.landings.day or ""),  # Day landings
            str(s.landings.night or ""),  # Night landings
            _duration(s.conditions.night),  # Night duration
            _duration(s.conditions.ifr),  # IFR duration
            _duration(s.roles.p1 + s.roles.p1s),  # PIC duration
            _duration(s.roles.p2),  # Co-Pilot duration
            _duration(s.roles.put),  # Dual duration
            _duration(s.roles.instructor),  # Instruction duration
            s.comment  # Comment
        )
        rows.append(_row(cells))
    return _get_template("logbook-template.html").format(rows="\n".join(rows))


def summary_table1(sectors: list[ep.Sector]) -> list[str]:
    roles_for_type: dict[str, list[int]] = {}
    for s in sectors:
        if s.aircraft.type_ not in roles_for_type:
            roles_for_type[s.aircraft.type_] = [0] * 6
        sector_roles = (s.roles.p1, s.roles.p1s, s.roles.p2,
                        s.roles.put, s.roles.p0, s.roles.instructor)
        for c in range(6):
            roles_for_type[s.aircraft.type_][c] += sector_roles[c]
    rows = []
    col_totals = [0] * 8
    for type_, roles in sorted(roles_for_type.items()):
        cells = (
            sum(roles[:-1]),  # Total (excludes instruction)
            sum(roles[:2]),  # PIC (P1 + P1S)
            *roles  # P1, P1S, P2, PUT, P0, INS
        )
        for c in range(8):
            col_totals[c] += cells[c]
        rows.append(_row(tuple([type_] + [_duration(X) for X in cells])))
    rows.append(_row(tuple(["Total"] + [_duration(X) for X in col_totals])))
    return rows


def summary_table2(
        sectors: list[ep.Sector],
        ac_classes: cp.SectionProxy
) -> list[str]:
    cells_for_type = {}
    for s in sectors:
        if s.aircraft.type_ not in cells_for_type:
            cells_for_type[s.aircraft.type_] = [0] * 9
        sector_cells = (
            *_ac_class_tuple(s, ac_classes),  # SPSE, SPME, MC
            s.total - s.conditions.ifr,  # VFR
            s.conditions.ifr,  # IFR
            s.total - s.conditions.night,  # Day
            s.conditions.night,  # Night
            s.landings.day,  # Day landings
            s.landings.night  # Night landings
        )
        for c in range(9):
            cells_for_type[s.aircraft.type_][c] += sector_cells[c]
    rows = []
    col_totals = [0] * 9
    for type_, cells in sorted(cells_for_type.items()):
        for c in range(9):
            col_totals[c] += cells[c]
        rows.append(_row(tuple(
            [type_] +
            [_duration(X) for X in cells[:7]] +
            [str(X) for X in cells[7:]])))
    rows.append(_row(tuple(
            ["Total"] +
            [_duration(X) for X in col_totals[:7]] +
            [str(X) for X in col_totals[7:]])))
    return rows


def build_summary(
        in_: str,
        ac_classes: cp.SectionProxy,
        daterange: DateRange = (None, None)
) -> str:
    """Build an HTML file with a summary table.

    :param in_: An EFJ format text file as a string

    :param daterange: A tuple of the form (FROM, TO) where FROM and TO are
        datetime dates. Sectors commencing on a date on or after FROM but
        before TO will be summarised (i.e range is half closed). FROM and/or TO
        may be None in which case the associated restriction is not applied.

    :return: An HTML file as a string

    """
    _, parsed_sectors = ep.Parser().parse(in_)
    sectors = []
    for s in parsed_sectors:
        if ((not daterange[0] or s.start.date() >= daterange[0]) and
                (not daterange[1] or s.start.date() < daterange[1])):
            sectors.append(s)
    return _get_template("summary-template.html").format(
        table1_body="\n".join(summary_table1(sectors)),
        table2_body="\n".join(summary_table2(sectors, ac_classes))
    )


def build_cumulative(
        efj: str,
        ac_classes: cp.SectionProxy,
        daterange: DateRange = (None, None)) -> str:
    _, sectors = ep.Parser().parse(efj)
    cumulative_totals = [0] * 12
    rows = []
    for s in sorted(sectors):
        end = s.start + dt.timedelta(minutes=s.total)
        if daterange[1] and end.date() >= daterange[1]:
            break
        sector_cells = (
            *_ac_class_tuple(s, ac_classes),  # SPSE, SPME, MC minutes
            s.total,  # Total minutes
            s.landings.day,  # Day landings
            s.landings.night,  # Night landings
            s.conditions.night,  # Night minutes
            s.conditions.ifr,  # IFR minutes
            s.roles.p1 + s.roles.p1s,  # PIC minutes
            s.roles.p2,  # Co-Pilot minutes
            s.roles.put,  # Dual minutes
            s.roles.instructor  # Instructor minutes
        )
        for c in range(12):
            cumulative_totals[c] += sector_cells[c]
        if daterange[0] and end.date() < daterange[0]:
            continue
        rows.append(_row((
            f"{end:%d/%m/%Y}",
            f"{end:%H:%M}",
            *(_duration(X) for X in cumulative_totals[:4]),
            *(str(X) for X in cumulative_totals[4:6]),
            *(_duration(X) for X in cumulative_totals[6:]))
        ))
    return (_get_template("cumulative-template.html")
            .format(rows="\n".join(rows)))
