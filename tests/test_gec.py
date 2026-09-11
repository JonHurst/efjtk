import unittest

import efj_parser as ep
import efjtk.gec as gec

class TestOverlap(unittest.TestCase):

    def test_overlapping(self):
        _, data = ep.Parser().parse("""\
2026-09-11
G-ABCD:A320
BRS/GLA 1100/1200
/ 1130/1230
""")
        self.assertEqual(
            gec.sector_overlaps(sorted(data)),
            ["2026-09-11 11:30 -30"])


class TestVelocityAnomaly(unittest.TestCase):

    def test_high(self):
        _, data = ep.Parser().parse("""\
2026-09-11
G-ABCD:A320
BRS/GLA 1100/1200
/ 1300/1400
/ 1500/1600
/ 1700/1710
/ 1900/2000
/ 2100/2200
""")
        _, a = gec.velocity_anomaly(data)
        self.assertEqual(a, ['2026-09-11 1700/1710 GLA/BRS 276 1658'])

    def test_missing_airfield(self):
        _, data = ep.Parser().parse("""\
2026-09-11
G-ABCD:A320
BRS/XXXXX 1100/1200
""")
        self.assertEqual(
            gec.velocity_anomaly(data)[0],
            ["XXXXX"])
