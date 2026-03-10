import unittest
from datetime import date

from flight_search import SearchConfig, SegmentPreference, generate_queries


class FlightSearchTests(unittest.TestCase):
    def test_generate_with_multi_airports_and_date_range(self):
        config = SearchConfig(
            segments=[
                SegmentPreference(
                    origins=["TPE", "HND"],
                    destinations=["LHR"],
                    depart_from=date(2026, 1, 1),
                    depart_to=date(2026, 1, 2),
                    via_airports=["SIN"],
                    allow_exit_transit=True,
                )
            ],
            max_queries=20,
        )

        queries = generate_queries(config)
        self.assertEqual(len(queries), 4)
        self.assertIn("mustVia=SIN", queries[0].to_skyscanner_url())

    def test_cap_to_max_four_segments(self):
        seg = SegmentPreference(
            origins=["TPE"],
            destinations=["NRT"],
            depart_from=date(2026, 2, 1),
            depart_to=date(2026, 2, 1),
        )
        with self.assertRaisesRegex(ValueError, "up to 4 segments"):
            generate_queries(SearchConfig(segments=[seg, seg, seg, seg, seg]))

    def test_max_queries_limit(self):
        config = SearchConfig(
            segments=[
                SegmentPreference(
                    origins=["TPE", "KHH"],
                    destinations=["NRT", "HND"],
                    depart_from=date(2026, 1, 1),
                    depart_to=date(2026, 1, 3),
                )
            ],
            max_queries=5,
        )
        queries = generate_queries(config)
        self.assertEqual(len(queries), 5)


if __name__ == "__main__":
    unittest.main()
