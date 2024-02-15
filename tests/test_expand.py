import unittest

from efj_parser import ValidationError
import efjtk.modify


class TestExpand(unittest.TestCase):

    def test_well_formatted(self):
        data = """\
2024-01-29
G-ABCD:A320
BRS/KEF 1600/1900
/ 2000/2300

+
/CDG 1300/1400
/ 1500/1600
++
PMI/ 1200/0100"""
        expected = """\
2024-01-29
G-ABCD:A320
BRS/KEF 1600/1900
KEF/BRS 2000/2300

2024-01-30
BRS/CDG 1300/1400
CDG/BRS 1500/1600
2024-02-01
PMI/CDG 1200/0100"""
        self.assertEqual(efjtk.modify.expand_efj(data), expected)

    def test_bad(self):
        with self.subTest("No preceding date"):
            with self.assertRaises(ValidationError) as ve:
                efjtk.modify.expand_efj("++")
            self.assertEqual(
                str(ve.exception),
                "Line 1: [Short date without preceding Date entry] ++")
        with self.subTest("No aircraft"):
            with self.assertRaises(ValidationError) as ve:
                efjtk.modify.expand_efj(
                    "2024-01-29\nBRS/KEF 1600/1900\n/ 2000/2300")
            self.assertEqual(
                str(ve.exception),
                "Line 2: [Sector with no preceding Aircraft entry] "
                "BRS/KEF 1600/1900")
        with self.subTest("No previous airports"):
            with self.assertRaises(ValidationError) as ve:
                efjtk.modify.expand_efj("2024-01-29\nG-ABCD:A320\n/ 1600/1900")
            self.assertEqual(
                str(ve.exception),
                "Line 3: [Blank From without previous To] / 1600/1900")
            with self.assertRaises(ValidationError) as ve:
                efjtk.modify.expand_efj(
                    "2024-01-29\nG-ABCD:A320\nBRS/ 1600/1900")
            self.assertEqual(
                str(ve.exception),
                "Line 3: [Blank To without previous From] BRS/ 1600/1900")
