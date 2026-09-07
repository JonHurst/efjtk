import unittest
import datetime as dt

import efjtk.convert
import efjtk.config


ac_classes = efjtk.config.aircraft_classes(
    "[aircraft.classes]\n"
    "c152 = spse\n"
    "c406 = spme\n"
    "a320 = mc")


class TestLogbook(unittest.TestCase):

    def setUp(self):
        with open("convert_test_input") as f:
            self.test_input = f.read()

    def test_standard(self):
        output = efjtk.convert.build_logbook(
                self.test_input, ac_classes, (None, None))
        with open("expected_logbook.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_from(self):
        output = efjtk.convert.build_logbook(
            self.test_input, ac_classes,
            (dt.date(2024, 1, 3), None))
        with open("expected_logbook_from.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_to(self):
        output = efjtk.convert.build_logbook(
            self.test_input,  ac_classes,
            (None, dt.date(2024, 1, 3)))
        with open("expected_logbook_to.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_fromto(self):
        output = efjtk.convert.build_logbook(
            self.test_input,  ac_classes,
            (dt.date(2024, 1, 2), dt.date(2024, 1, 3)))
        with open("expected_logbook_fromto.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())


class TestCumulative(unittest.TestCase):

    def setUp(self):
        with open("convert_test_input") as f:
            self.test_input = f.read()

    def test_standard(self):
        output = efjtk.convert.build_cumulative(self.test_input, ac_classes)
        with open("expected_cum_convert_result.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_from(self):
        output = efjtk.convert.build_cumulative(
            self.test_input, ac_classes,
            (dt.date(2024, 1, 3), None))
        with open("expected_cum_convert_result_from.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_to(self):
        output = efjtk.convert.build_cumulative(
            self.test_input, ac_classes,
            (None, dt.date(2024, 1, 3)))
        with open("expected_cum_convert_result_to.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_fromto(self):
        output = efjtk.convert.build_cumulative(
            self.test_input, ac_classes,
            (dt.date(2024, 1, 2), dt.date(2024, 1, 3)))
        with open("expected_cum_convert_result_fromto.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())


class TestSummary(unittest.TestCase):

    def setUp(self):
        with open("convert_test_input") as f:
            self.test_input = f.read()

    def test_standard(self):
        output = efjtk.convert.build_summary(self.test_input)
        with open("expected_summary.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_from(self):
        output = efjtk.convert.build_summary(
            self.test_input,
            (dt.date(2024, 1, 3), None))
        with open("expected_summary_from.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_to(self):
        output = efjtk.convert.build_summary(
            self.test_input,
            (None, dt.date(2024, 1, 3)))
        with open("expected_summary_to.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_fromto(self):
        output = efjtk.convert.build_summary(
            self.test_input,
            (dt.date(2024, 1, 2), dt.date(2024, 1, 3)))
        with open("expected_summary_fromto.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())
