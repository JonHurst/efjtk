import efj_parser as ep
import datetime as dt
import math
import statistics

from nightflight.airport_nvecs import airfields  # type:ignore

GEC_MIN_SECTOR_OVERLAP = 15
STDDEV_ANOM = 2


def sector_overlaps(sorted_sectors: list[ep.Sector]) -> list[str]:
    if len(sorted_sectors) < 2:
        return []
    retval = []
    for s1, s2 in zip(sorted_sectors[:-1], sorted_sectors[1:]):
        s1_end = s1.start + dt.timedelta(minutes=s1.total)
        gap = (s2.start - s1_end) / dt.timedelta(minutes=1)
        if gap < GEC_MIN_SECTOR_OVERLAP:
            retval.append(f"{s2.start:%Y-%m-%d %H:%M} {int(gap)}")
    return retval


def velocity_anomaly(sectors: list[ep.Sector]) -> tuple[list[str], list[str]]:
    sectors = [X for X in sectors if X.airports.origin != X.airports.dest]
    unknown_airfields = set()
    velocities_by_type: dict[str, list[float]] = {}
    results = []
    for s in sectors:
        origin_nvec, dest_nvec = None, None
        try:
            origin_nvec = airfields[s.airports.origin]
        except KeyError:
            unknown_airfields.add(s.airports.origin)
        try:
            dest_nvec = airfields[s.airports.dest]
        except KeyError:
            unknown_airfields.add(s.airports.dest)
        if origin_nvec and dest_nvec:
            sprod = math.sumprod(origin_nvec, dest_nvec)
            angle = math.acos(min(1, sprod))
            distance = 3440 * angle
            if distance > 100:
                v = distance * 60 / s.total
                results.append((distance, v, s))
                velocities_by_type.setdefault(s.aircraft.type_, []).append(v)
    ranges_by_type = {}
    for k, vlist in velocities_by_type.items():
        mean = statistics.mean(vlist)
        stdev = statistics.stdev(vlist)
        ranges_by_type[k] = (mean - STDDEV_ANOM * stdev,
                             mean + STDDEV_ANOM * stdev)
    anomolous = []
    for d, v, s in results:
        r = ranges_by_type[s.aircraft.type_]
        if not (r[0] < v < r[1]):
            end = s.start + dt.timedelta(minutes=s.total)
            anomolous.append(
                f"{s.start:%Y-%m-%d %H%M}/{end:%H%M} "
                f"{s.airports.origin}/{s.airports.dest} {d:.0f} {v:.0f}")
    return (sorted(unknown_airfields), sorted(anomolous))


def report(efj: str, date_range: tuple[dt.date, dt.date]) -> str:
    output = []
    duties, sectors = ep.Parser().parse(efj)
    if all(date_range):
        sorted_sectors = [X for X in sorted(sectors)
                          if date_range[0] <= X.start < date_range[1]]
    else:
        sorted_sectors = sorted(sectors)
    if so := sector_overlaps(sorted_sectors):
        output.append("Overlapping\n===========")
        for o in so:
            output.append(o)
    missing, anomolous = velocity_anomaly(sorted_sectors)
    if missing:
        output.append("\nMissing\n=======")
        for m in missing:
            output.append(m)
    if anomolous:
        output.append("\nAnomolous Velocity\n==================")
        for a in anomolous:
            output.append(a)
    return "\n".join(output)
