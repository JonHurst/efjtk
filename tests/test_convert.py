import unittest
import datetime as dt

import efjtk.convert


class TestLogbook(unittest.TestCase):

    def setUp(self):
        with open("convert_test_input") as f:
            self.test_input = f.read()

    def test_standard(self):
        output = efjtk.convert.build_logbook(
                self.test_input, (None, None))
        with open("expected_logbook.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_from(self):
        output = efjtk.convert.build_logbook(
            self.test_input,
            (dt.date(2024, 1, 3), None))
        with open("expected_logbook_from.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_to(self):
        output = efjtk.convert.build_logbook(
            self.test_input,
            (None, dt.date(2024, 1, 3)))
        with open("expected_logbook_to.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_fromto(self):
        output = efjtk.convert.build_logbook(
            self.test_input,
            (dt.date(2024, 1, 2), dt.date(2024, 1, 3)))
        with open("expected_logbook_fromto.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())


class TestCumulative(unittest.TestCase):

    def setUp(self):
        with open("convert_test_input") as f:
            self.test_input = f.read()

    def test_standard(self):
        output = efjtk.convert.build_cumulative(self.test_input)
        with open("expected_cumulative.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_from(self):
        output = efjtk.convert.build_cumulative(
            self.test_input,
            (dt.date(2024, 1, 3), None))
        with open("expected_cumulative_from.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_to(self):
        output = efjtk.convert.build_cumulative(
            self.test_input,
            (None, dt.date(2024, 1, 3)))
        with open("expected_cumulative_to.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_ranged_fromto(self):
        output = efjtk.convert.build_cumulative(
            self.test_input,
            (dt.date(2024, 1, 2), dt.date(2024, 1, 3)))
        with open("expected_cumulative_fromto.html") as f:
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


class TestDateAccumulator(unittest.TestCase):

    def test_basic(self):
        # test requires system timezone to be Europe/London
        test = efjtk.convert.DateAccumulator(
            (dt.datetime(2026, 10, 9, 12),
             dt.datetime(2026, 10, 11, 23),
             dt.datetime(2026, 10, 12, 14)),
            (60, 120, 45))
        self.assertEqual(test.get(dt.date(2026, 10 , 8)), 0)
        self.assertEqual(test.get(dt.date(2026, 10 , 9)), 60)
        self.assertEqual(test.get(dt.date(2026, 10 , 10)), 60)
        self.assertEqual(test.get(dt.date(2026, 10 , 11)), 60)
        self.assertEqual(test.get(dt.date(2026, 10 , 12)), 225)
        self.assertEqual(test.get(dt.date(2026, 10 , 13)), 225)
        self.assertEqual(
            test.get_range(),
            (dt.date(2026, 10, 9), dt.date(2026, 10, 14)))

    def test_hour_change(self):
        # test requires system timezone to be Europe/London
        test = efjtk.convert.DateAccumulator(
            (dt.datetime(2026, 10, 23, 22, 30),
             dt.datetime(2026, 10, 25, 0)),
            (120, 180))
        self.assertEqual(test.get(dt.date(2026, 3 , 22)), 0)
        self.assertEqual(test.get(dt.date(2026, 10 , 22)), 0)
        self.assertEqual(test.get(dt.date(2026, 10 , 23)), 30)
        self.assertEqual(test.get(dt.date(2026, 10 , 24)), 120)
        self.assertEqual(test.get(dt.date(2026, 10 , 25)), 300)
        self.assertEqual(test.get(dt.date(2026, 10 , 30)), 300)


class TestFTL(unittest.TestCase):

    def setUp(self):
        with open("ftl-test.efj") as f:
            self.test_input = f.read()

    def test_standard(self):
        output = efjtk.convert.build_ftl(
                self.test_input, (None, dt.date(2027, 2, 1)))
        with open("expected_ftl-test-result.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_empty(self):
        output = efjtk.convert.build_ftl("", (None, None))
        with open("expected_ftl-empty.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_only_duty(self):
        output = efjtk.convert.build_ftl(
            "2026-10-19\n1000/1100",
            (None, None))
        with open("expected_ftl-only-duty.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())

    def test_only_sector(self):
        output = efjtk.convert.build_ftl(
            "2026-10-19\nG-ABCD:A320\nBRS/BFS 1000/1100",
            (None, None))
        with open("expected_ftl-only-sector.html") as f:
            expected = f.read()
            self.assertEqual(output.strip(), expected.strip())
