import json
import tempfile
import unittest
from pathlib import Path

from app.config import DEFAULT_PATH, DEFAULT_SETTINGS, load_settings
from app.decision_logic import DecisionLogic
from app.traffic_controller import TrafficController


class ConfigTests(unittest.TestCase):
    def test_default_file_matches_defaults(self):
        self.assertEqual(load_settings(), DEFAULT_SETTINGS)

    def test_one_file_changes_parameters_and_current_behavior(self):
        values = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))
        values.update({
            "waiting_count_threshold": 2,
            "waiting_seconds_threshold": 10,
            "min_green_seconds": 4,
            "extension_step_seconds": 2,
            "max_extension_seconds": 4,
            "barrier_wait_seconds": 1,
            "barrier_descent_seconds": 3,
            "entry_confirmation_frames": 4,
            "exit_confirmation_seconds": 3,
            "waiting_presence_seconds": 1,
            "voice_repeat_seconds": 7,
        })
        values["roi"]["crosswalk"] = [340, 130, 560, 470]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps(values), encoding="utf-8")
            settings = load_settings(path)

        self.assertEqual(settings, values)
        controller = TrafficController(settings)
        decision = DecisionLogic(controller)
        controller.advance(3)
        self.assertIsNone(decision.evaluate(waiting_count=2))
        controller.advance()
        self.assertTrue(decision.evaluate(waiting_count=2))
        self.assertEqual(controller.phase, "B")

        controller = TrafficController(settings)
        decision = DecisionLogic(controller)
        controller.advance(4)
        self.assertTrue(decision.evaluate(longest_wait_seconds=10))
        self.assertEqual(controller.phase, "B")

        controller = TrafficController(settings)
        controller.advance(47)
        self.assertTrue(controller.request_extend())
        self.assertTrue(controller.request_extend())
        self.assertFalse(controller.request_extend())
        self.assertEqual(controller.status["remaining_seconds"], 6)

    def test_invalid_values_use_defaults_with_warning(self):
        values = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))
        values["waiting_count_threshold"] = 0
        values["max_extension_seconds"] = 11
        values["roi"]["crosswalk"] = [550, 140, 350, 460]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps(values), encoding="utf-8")
            with self.assertLogs(level="WARNING") as logs:
                settings = load_settings(path)

        self.assertEqual(settings["waiting_count_threshold"], 3)
        self.assertEqual(settings["max_extension_seconds"], 5)
        self.assertEqual(settings["roi"], DEFAULT_SETTINGS["roi"])
        self.assertEqual(len(logs.output), 3)

    def test_malformed_file_fails_at_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_settings(path)


if __name__ == "__main__":
    unittest.main()
