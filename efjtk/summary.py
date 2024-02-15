import importlib.resources as res

import efj_parser as ep


def _duration(minutes):
    if minutes:
        return f"{minutes // 60}:{minutes % 60:02}"
    return ""


def _get_template():
    template = (res.files("efjtk")
                .joinpath("summary-template.html")
                .open().read())
    for old, new in (("{", "{{"), ("}", "}}"),
                     ("<!--{{", "{"), ("}}-->", "}")):
        template = template.replace(old, new)
    return template


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


def build(in_: str) -> str:
    """Build an HTML file with a summary table.

    :param in_: An EFJ format text file as a string
    :return: An HTML file as a string
    """
    _, sectors = ep.Parser().parse(in_)
    roles = _build_roles(sectors)
    conditions = _build_conditions(sectors)
    landings = _build_landings(sectors)
    return _get_template().format(
        roles_body="\n".join(roles[:-1]),
        roles_totals=roles[-1],
        cond_body="\n".join(conditions[:-1]),
        cond_totals=conditions[-1],
        ldg_body="\n".join(landings[:-1]),
        ldg_totals=landings[-1]
    )
