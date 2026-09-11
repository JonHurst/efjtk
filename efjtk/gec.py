import efj_parser as ep
import datetime as dt
import math

from nightflight.airport_nvecs import airfields  # type:ignore

GEC_MIN_SECTOR_OVERLAP = 15
VELOCITY_LIMIT_LOW = 50
VELOCITY_LIMIT_HIGH = 500


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
    unknown_airfields = set()
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
                results.append((distance, distance * 60 / s.total, s))
    anomolous = []
    for d, v, s in results:
        if not (VELOCITY_LIMIT_LOW < v < VELOCITY_LIMIT_HIGH):
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
