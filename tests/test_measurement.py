import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from evaluation.server_measure import (
    percentile_95,
    save_report,
    term_criteria_met,
    validate_server_url,
)


class MeasurementHelpersTests(unittest.TestCase):
    def test_root_cause_requires_every_labelled_phrase(self):
        required = ["connection pool", "exhaustion"]

        self.assertTrue(
            term_criteria_met("Database connection pool exhaustion.", required)
        )
        self.assertFalse(
            term_criteria_met("Database connection pool is near its limit.", required)
        )

    def test_p95_uses_nearest_rank(self):
        self.assertEqual(percentile_95([1, 2, 3, 4]), 4)
        self.assertIsNone(percentile_95([]))

    def test_requires_https_for_deployed_measurement_target(self):
        self.assertEqual(
            validate_server_url("https://incidents.example.com/"),
            "https://incidents.example.com",
        )
        with self.assertRaises(ValueError):
            validate_server_url("http://incidents.example.com")
        with self.assertRaises(ValueError):
            validate_server_url("https://localhost:8000")
        with self.assertRaises(ValueError):
            validate_server_url("https://[::1]:8000")

    def test_http_requires_explicit_opt_in(self):
        self.assertEqual(
            validate_server_url("http://10.0.0.12:8000", allow_http=True),
            "http://10.0.0.12:8000",
        )

    def test_report_refuses_to_mix_non_server_measurements(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "measurements.json"
            path.write_text(json.dumps({"runs": []}), encoding="utf-8")

            with self.assertRaises(ValueError):
                save_report({"run_id": "test"}, path)


if __name__ == "__main__":
    unittest.main()
