import unittest
from datetime import date

from web_app import _build_segments, _csv_codes, _parse_bool


class WebAppTests(unittest.TestCase):
    def test_csv_codes(self):
        self.assertEqual(_csv_codes("tpe, hnd ,"), ["TPE", "HND"])

    def test_parse_bool(self):
        self.assertTrue(_parse_bool("on"))
        self.assertFalse(_parse_bool("0"))

    def test_build_segments(self):
        form = {
            "origins_1": ["tpe,khh"],
            "destinations_1": ["nrt"],
            "depart_from_1": ["2026-01-01"],
            "depart_to_1": ["2026-01-02"],
            "via_1": ["sin"],
            "allow_exit_1": ["1"],
        }
        segments = _build_segments(form, 1)
        self.assertEqual(segments[0].origins, ["TPE", "KHH"])
        self.assertEqual(segments[0].depart_from, date(2026, 1, 1))
        self.assertTrue(segments[0].allow_exit_transit)


if __name__ == "__main__":
    unittest.main()
