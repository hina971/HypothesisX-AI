import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.hypothesis_agent import analyze_pattern, generate_hypothesis, validate_pattern


class TestHypothesisAgent(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "correlation",
            "variable_x": "Humidity_percent",
            "variable_y": "Temperature_C",
            "relationship": "negative",
            "correlation": -0.661,
            "sample_size": 1000,
        }

    def test_correlation_hypothesis(self):
        result = analyze_pattern(self.pattern)
        self.assertIn("Humidity_percent", result["hypothesis"]["statement"])
        self.assertEqual(result["hypothesis"]["pattern_type"], "correlation")
        self.assertGreaterEqual(len(result["alternative_explanations"]), 5)
        self.assertEqual(result["generation_confidence"], "medium")

    def test_missing_required_field(self):
        with self.assertRaisesRegex(ValueError, "variable_y"):
            generate_hypothesis({"pattern_type": "correlation", "variable_x": "A"})

    def test_invalid_pattern_type(self):
        with self.assertRaisesRegex(ValueError, "Unsupported pattern_type"):
            validate_pattern({"pattern_type": "unknown"})

    def test_json_serializable(self):
        import json
        result = analyze_pattern(self.pattern)
        json.dumps(result)


if __name__ == "__main__":
    unittest.main()
