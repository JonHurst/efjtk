import unittest

from efj_parser import ValidationError
from efjtk.modify import add_night_data


class TestNight(unittest.TestCase):

    def test_well_formatted(self):
        data = """\
2024-01-01
G-ACBD:A320
BRS/BRS 1300/1400 ld:3
BRS/BRS 1600/1700 ln
/ 2000/2100"""
        expected = """\
2024-01-01
G-ACBD:A320
BRS/BRS 1300/1400 ld:3
BRS/BRS 1600/1700 n:18 ln
/ 2000/2100 n"""
        self.assertEqual(add_night_data(data), expected)
        self.assertEqual(add_night_data(expected), expected)

    def test_bad(self):
        data = "2024-01-01\nG-ACBD:A320\nXXXX/XXXX 1300/1400"
        with self.assertRaises(ValidationError) as ve:
            add_night_data(data)
        self.assertEqual(
            str(ve.exception),
            "Line 3: [Airport(s) not in database] XXXX/XXXX 1300/1400")
