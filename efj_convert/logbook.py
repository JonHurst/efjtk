#!/usr/bin/env python3

import datetime as dt

from efj_parser import Parser


template_page = """\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
   <meta charset='UTF-8'/>
    <title>FCL.050 Logbook</title>
<style>
:root {{
    --thin-border: 0.0625rem solid black;
    --thick-border: 0.125rem solid black;
    --stripe: #E0FFE0;
    background-color: white;
    color: black;
    font-family: arial, sans-serif;
}}

.j-lb-table {{
    margin: auto;
    border-collapse: fixed;
    border-spacing: 0;
    text-align: center;
    position: relative;
    table-layout: fixed;
    width: 100rem;
    border-bottom: var(--thick-border);
}}

.j-lb-table thead {{
    background-color: white;
    font-weight: bold;
    position: sticky;
    top: 0;
}}

.j-lb-table tr:first-child th {{
    border-top: var(--thick-border);
    border-right: var(--thick-border);
}}

.j-lb-table tr:first-child th:nth-child(5) {{
    border-right: var(--thin-border);
}}

.j-lb-table tr:first-child th:first-child {{
    border-left: var(--thick-border);
}}

.j-lb-table tr:first-child th:nth-child(1),
.j-lb-table tr:first-child th:nth-child(6),
.j-lb-table tr:first-child th:nth-child(7),
.j-lb-table tr:first-child th:nth-child(8),
.j-lb-table tr:first-child th:nth-child(12) {{
    border-bottom: var(--thick-border);
}}

.j-lb-table tr:last-child th:nth-child(2),
.j-lb-table tr:last-child th:nth-child(4),
.j-lb-table tr:last-child th:nth-child(6),
.j-lb-table tr:last-child th:nth-child(10),
.j-lb-table tr:last-child th:nth-child(12),
.j-lb-table tr:last-child th:nth-child(16) {{
    border-right: var(--thick-border);
}}

.j-lb-table tr:first-child td {{
    border-top: none;
}}

.j-lb-table tr:last-child td,
.j-lb-table tr:last-child th {{
    border-bottom: var(--thick-border);
}}

.j-lb-table td:first-child {{
    border-left: var(--thick-border);
}}

.j-lb-table td:last-child {{
    border-right: var(--thick-border);
}}

.j-lb-table tbody tr:nth-child(even) {{
    background-color: var(--stripe);
}}

.j-lb-table td:nth-child(1),
.j-lb-table td:nth-child(3),
.j-lb-table td:nth-child(5),
.j-lb-table td:nth-child(7),
.j-lb-table td:nth-child(10),
.j-lb-table td:nth-child(11),
.j-lb-table td:nth-child(12),
.j-lb-table td:nth-child(14),
.j-lb-table td:nth-child(16),
.j-lb-table td:nth-child(20) {{
    border-right: var(--thick-border);
}}

.j-lb-table td,
.j-lb-table th {{
    border-top: var(--thin-border);
    border-right: var(--thin-border);
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0.2rem;
}}

.j-lb-table td:last-child,
.j-lb-table td:nth-child(12) {{
    text-align: left;
}}


.j-col-date {{
    width: 7rem;
}}
.j-col-place {{
    width: 5rem;
}}
.j-col-time {{
    width: 3.75rem;
}}
.j-col-duration {{
    width: 3.5rem;
}}
.j-col-type {{
    width: 6rem;
}}
.j-col-reg {{
    width: 6rem;
}}
.j-col-narrow {{
    width: 2.25rem;
}}
.j-col-pic {{
    width: 8rem;
}}

@page {{
    size: A4 landscape;
    -prince-shrink-to-fit: auto;
    margin: 1cm;
}}

@page:left {{
    margin-bottom: 2cm;
}}

@page:right {{
    margin-top: 2cm;
}}

</style>
  </head>
  <body>
    <table class='j-lb-table'>
<colgroup>
<col class="j-col-date"/>
<col class="j-col-place"/>
<col class="j-col-time"/>
<col class="j-col-place"/>
<col class="j-col-time"/>
<col class="j-col-type"/>
<col class="j-col-reg"/>
<col class="j-col-narrow"/>
<col class="j-col-narrow"/>
<col class="j-col-duration"/>
<col class="j-col-duration"/>
<col class="j-col-pic"/>
<col class="j-col-narrow"/>
<col class="j-col-narrow"/>
<col class="j-col-duration"/>
<col class="j-col-duration"/>
<col class="j-col-duration"/>
<col class="j-col-duration"/>
<col class="j-col-duration"/>
<col class="j-col-duration"/>
</colgroup>
      <thead>
        <tr><th rowspan="2">Date</th>
            <th colspan="2">Departure</th><th colspan="2">Arrival</th>
            <th colspan="2">Aircraft</th>
            <th colspan="2">Single Pilot</th><th rowspan="2">Multi Pilot</th>
            <th rowspan="2">Total</th>
            <th rowspan = "2">PIC</th>
            <th colspan="2">Ldgs</th>
            <th colspan="2">Conditions</th>
            <th colspan="4">Pilot Function</th>
            <th rowspan="2">Remarks and Endorsements</th></tr>
        <tr><th>Place</th><th>Time</th><th>Place</th><th>Time</th>
            <th>Type</th><th>Reg</th>
            <th>SE</th><th>ME</th>
            <th>D</th><th>N</th>
            <th>Night</th><th>IFR</th>
            <th>PIC</th><th>Co-Pilot</th><th>Dual</th><th>Inst</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </body>
</html>
"""

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
    return template_page.format(rows="\n".join(rows))
