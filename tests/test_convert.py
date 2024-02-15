import unittest

import efjtk.convert
import efjtk.config


ac_classes = efjtk.config.aircraft_classes(
    "[aircraft.classes]\n"
    "c152 = spse\n"
    "c406 = spme\n"
    "a320 = mc")


class TestLogbook(unittest.TestCase):

    def test_standard(self):
        with open("convert_test_input") as f:
            output = efjtk.convert.build_logbook(f.read(), ac_classes)
        with open("expected_convert_result.html") as f:
            expected = f.read()
        self.assertEqual(output.strip(), expected.strip())


if __name__ == "__main__":
    with open("convert_test_input") as f:
        print(efjtk.convert.build_logbook(f.read(), ac_classes))
