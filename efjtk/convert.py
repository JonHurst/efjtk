import configparser as cp
import importlib.resources as res
import datetime as dt

from typing import Optional, cast
import efj_parser as ep


class UnknownAircraftType(Exception):
    """Aircraft type with no matching class encountered"""

    def __init__(self, type_):
        self.missing_type = type_


DateRange = tuple[Optional[dt.date], Optional[dt.date]]


def _get_template(filename):
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
        cells = [f"{s.start:%d/%m/%Y}",
                 s.airports.origin, f"{s.start:%H:%M}",
                 s.airports.dest,
                 f"{s.start + dt.timedelta(minutes=s.total):%H:%M}",
                 s.aircraft.type_, s.aircraft.reg]
        ac_class_cells = [_duration(X) for X in _ac_class_tuple(s, ac_classes)]
        for c in range(2):  # replace the first two durations with ticks if >0
            if ac_class_cells[c]:
                ac_class_cells[c] = "✓"
        cells.extend(ac_class_cells)
        cells.append(_duration(s.total))
        cells.append(s.captain)
        cells.extend([str(s.landings.day or ""), str(s.landings.night or "")])
        night, ifr = "", ""
        if s.conditions.night:
            night = _duration(s.conditions.night)
        if s.conditions.ifr:
            ifr = _duration(s.conditions.ifr)
        cells.extend([night, ifr])
        cells.extend([_duration(X) if X else ""
                      for X in (s.roles.p1 + s.roles.p1s, s.roles.p2,
                                s.roles.put, s.roles.instructor)])
        cells.append(s.comment)
        rows.append(f"<tr><td>{'</td><td>'.join(cells)}</td></tr>")
    return _get_template("logbook-template.html").format(rows="\n".join(rows))


def _table1_rows(sectors: list[ep.Sector]):
    rpt = {}
    for s in sectors:
        type_ = s.aircraft.type_
        roles = [s.roles.p1, s.roles.p1s, s.roles.p2,
                 s.roles.put, s.roles.p0, s.roles.instructor]
        if s.aircraft.type_ not in rpt:
            rpt[type_] = roles
        else:
            rpt[type_] = [X + Y for X, Y in zip(rpt[type_], roles)]
    rows = []
    col_totals = [0] * 8
    for type_, roles in sorted(rpt.items()):
        cols = [sum(roles[:-1]), sum(roles[:2]), *roles]
        col_totals = [X + Y for X, Y in zip(col_totals, cols)]
        col_data = '</td><td>'.join(_duration(X) for X in cols)
        rows.append(f"<tr><th>{type_}</th><td>{col_data}</td></tr>")
    data = '</td><td class="total">'.join([_duration(X) for X in col_totals])
    rows.append(f"<tr class='col_total'><th>Total</th>"
                f"<td class='total'>{data}</td></tr>")
    return rows


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
    return cast(tuple[int, int, int],
                tuple(s.total if aircraft_class == X else 0
                      for X in ("spse", "spme", "mc")))


def _table2_rows(
        sectors: list[ep.Sector],
        ac_classes: cp.SectionProxy
) -> list[str]:
    rpt = {}
    for s in sectors:
        conditions = (s.total - s.conditions.ifr, s.conditions.ifr,
                      s.total - s.conditions.night, s.conditions.night)
        landings = (s.landings.day, s.landings.night)
        if s.aircraft.type_ not in rpt:
            rpt[s.aircraft.type_] = [0] * 9
        rpt[s.aircraft.type_] = [X + Y for X, Y in zip(
            rpt[s.aircraft.type_],
            _ac_class_tuple(s, ac_classes) + conditions + landings)]
    rows = []
    col_totals = [0] * 9
    for type_, cells in sorted(rpt.items()):
        col_totals = [X + Y for X, Y in zip(col_totals, cells)]
        data = (
            '</td><td>'.join(_duration(X) for X in cells[:7]) +
            '</td><td>' +
            '</td><td>'.join(str(X) for X in cells[7:])
        )
        rows.append(f"<tr><th>{type_}</th><td>{data}</td></tr>")
    data = (
        '</td><td class="total">'.join(_duration(X) for X in col_totals[:7]) +
        '</td><td>' +
        '</td><td class="total">'.join(str(X) for X in col_totals[7:])
    )
    rows.append(f"<tr class='col_total'><th>Total</th>"
                f"<td class='total'>{data}</td></tr>")
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
        table1_body="\n".join(_table1_rows(sectors)),
        table2_body="\n".join(_table2_rows(sectors, ac_classes))
    )


def build_cumulative(
        efj: str,
        ac_classes: cp.SectionProxy,
        daterange: DateRange = (None, None)) -> str:
    _, sectors = ep.Parser().parse(efj)
    spse, spme, mc, total = 0, 0, 0, 0
    day_ldg, night_ldg = 0, 0
    night, ifr = 0, 0
    pic, p2, put, ins = 0, 0, 0, 0
    rows = []
    for s in sorted(sectors):
        end = s.start + dt.timedelta(minutes=s.total)
        if daterange[1] and end.date() >= daterange[1]:
            break
        total += s.total
        classes = _ac_class_tuple(s, ac_classes)
        spse += classes[0]
        spme += classes[1]
        mc += classes[2]
        day_ldg += s.landings.day
        night_ldg += s.landings.night
        night += s.conditions.night
        ifr += s.conditions.ifr
        pic += s.roles.p1 + s.roles.p1s
        p2 += s.roles.p2
        put += s.roles.put
        ins += s.roles.instructor
        if daterange[0] and end.date() < daterange[0]:
            continue
        cells = [f"{end:%d/%m/%Y}", f"{end:%H:%M}",
                 _duration(spse), _duration(spme), _duration(mc),
                 _duration(total),
                 str(day_ldg), str(night_ldg),
                 _duration(night), _duration(ifr),
                 _duration(pic), _duration(p2), _duration(put), _duration(ins)
                 ]
        rows.append(f"<tr><td>{'</td><td>'.join(cells)}</td></tr>")
    return (_get_template("cumulative-template.html")
            .format(rows="\n".join(rows)))
