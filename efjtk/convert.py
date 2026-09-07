import configparser as cp
import importlib.resources as res
import datetime as dt

from typing import Optional
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


def _aircraft_class_cells(
        sector: ep.Sector,
        ac_classes: cp.SectionProxy,
        duration: str
) -> list[str]:
    if sector.aircraft.class_:
        aircraft_class = sector.aircraft.class_
    else:
        try:
            aircraft_class = ac_classes[sector.aircraft.type_]
        except KeyError:
            raise UnknownAircraftType(sector.aircraft.type_)
    if aircraft_class == "mc":
        return ["", "", duration]
    if aircraft_class == "spse":
        return ["✓", "", ""]
    return ["", "✓", ""]  # must be "spme"


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
        duration = _duration(s.total)
        cells.extend(_aircraft_class_cells(s, ac_classes, duration))
        cells.append(duration)
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


def _build_roles(sectors):
    rpt = {}
    for s in sectors:
        type_ = s.aircraft.type_
        roles = [s.roles.p1, s.roles.p1s, s.roles.p2, s.roles.put]
        if s.aircraft.type_ not in rpt:
            rpt[type_] = roles
        else:
            rpt[type_] = [X + Y for X, Y in zip(rpt[type_], roles)]
    rows = []
    role_total = [0, 0, 0, 0]
    for type_ in sorted(rpt.keys()):
        role_total = [X + Y for X, Y in zip(role_total, rpt[type_])]
        total = sum(rpt[type_])
        data = '</td><td>'.join([_duration(X) for X in rpt[type_]])
        rows.append(f"<tr><th>{type_}</th><td>{data}</td>"
                    f"<td class='total'>{_duration(total)}</td></tr>")
    data = '</td><td class="total">'.join([_duration(X) for X in role_total])
    rows.append(f"<tr class='col_total'><th>Total</th><td class='total'>{data}"
                f"</td><td class='total'>{_duration(sum(role_total))}"
                f"</td></tr>")
    return rows


def _build_conditions(sectors):
    cond_pt = {}
    for s in sectors:
        type_ = s.aircraft.type_
        conditions = [s.total - s.conditions.ifr, s.conditions.ifr,
                      s.total - s.conditions.night, s.conditions.night]
        if s.aircraft.type_ not in cond_pt:
            cond_pt[type_] = conditions
        else:
            cond_pt[type_] = [X + Y for X, Y in
                              zip(cond_pt[type_], conditions)]
    rows = []
    cond_total = [0, 0, 0, 0]
    for type_ in sorted(cond_pt.keys()):
        cond_total = [X + Y for X, Y in zip(cond_total, cond_pt[type_])]
        data = '</td><td>'.join([_duration(X) for X in cond_pt[type_]])
        rows.append(f"<tr><th>{type_}</th><td>{data}</td></tr>")
    data = '</td><td class="total">'.join([_duration(X) for X in cond_total])
    rows.append(f"<tr class='col_total'><th>Total</th>"
                f"<td class='total'>{data}</td></tr>")
    return rows


def _build_landings(sectors):
    ldg_pt = {}
    for s in sectors:
        type_ = s.aircraft.type_
        landings = [s.landings.day, s.landings.night]
        if s.aircraft.type_ not in ldg_pt:
            ldg_pt[type_] = landings
        else:
            ldg_pt[type_] = [X + Y for X, Y in
                             zip(ldg_pt[type_], landings)]
    rows = []
    landing_total = [0, 0]
    for type_ in sorted(ldg_pt.keys()):
        landing_total = [X + Y for X, Y in zip(landing_total, ldg_pt[type_])]
        data = '</td><td>'.join([str(X) for X in ldg_pt[type_]])
        total = sum(ldg_pt[type_])
        rows.append(f"<tr><th>{type_}</th><td>{data}</td>"
                    f"<td class='total'>{total}</td></tr>")
    data = '</td><td class="total">'.join([str(X) for X in landing_total])
    rows.append(f"<tr class='col_total'><th>Total</th>"
                f"<td class='total'>{data}</td>"
                f"<td class='total'>{sum(landing_total)}</td></tr>")
    return rows


def build_summary(in_: str, daterange: DateRange = (None, None)) -> str:
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
    roles = _build_roles(sectors)
    conditions = _build_conditions(sectors)
    landings = _build_landings(sectors)
    return _get_template("summary-template.html").format(
        roles_body="\n".join(roles[:-1]),
        roles_totals=roles[-1],
        cond_body="\n".join(conditions[:-1]),
        cond_totals=conditions[-1],
        ldg_body="\n".join(landings[:-1]),
        ldg_totals=landings[-1]
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
        if s.aircraft.class_:
            aircraft_class = s.aircraft.class_
        else:
            try:
                aircraft_class = ac_classes[s.aircraft.type_]
            except KeyError:
                raise UnknownAircraftType(s.aircraft.type_)
        if aircraft_class == "spse":
            spse += s.total
        elif aircraft_class == "spme":
            spme += s.total
        else:
            mc += s.total
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
