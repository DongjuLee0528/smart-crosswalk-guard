import unittest
from unittest.mock import patch

from app.decision_logic import DecisionLogic
from app.traffic_controller import TrafficController


class DecisionLogicTests(unittest.TestCase):
    def test_waiting_inputs_request_pedestrian_after_minimum_green(self):
        for waiting_count, longest_wait_seconds in ((3, 0), (1, 20)):
            controller = TrafficController()
            decision = DecisionLogic(controller)
            controller.advance(7)
            with patch.object(controller, "request_ped", wraps=controller.request_ped) as request:
                self.assertIsNone(decision.evaluate(waiting_count, longest_wait_seconds))
                self.assertEqual(controller.phase, "A")
                request.assert_not_called()
                controller.advance()
                self.assertTrue(decision.evaluate(waiting_count, longest_wait_seconds))
                self.assertEqual(controller.phase, "B")
                request.assert_called_once_with()

    def test_danger_takes_priority_and_releases_when_clear(self):
        controller = TrafficController()
        decision = DecisionLogic(controller)
        controller.advance(8)
        self.assertTrue(decision.evaluate(waiting_count=3, crossing=True))
        self.assertEqual(controller.phase, "STOP_YELLOW")
        controller.advance()
        self.assertEqual(controller.phase, "STOP_RED")
        self.assertIsNone(decision.evaluate(crossing=True))
        self.assertTrue(decision.evaluate(crossing=False))
        self.assertEqual(controller.phase, "C")

    def test_remaining_crossing_extends_only_once_per_heartbeat_and_holds_at_limit(self):
        controller = TrafficController()
        decision = DecisionLogic(controller)
        controller.advance(46)
        self.assertEqual(controller.status["phase"], "E")
        self.assertEqual(controller.status["remaining_seconds"], 1)
        decision.evaluate(crossing=True)
        controller.advance()
        self.assertEqual(controller.phase, "F")

        for _ in range(5):
            self.assertTrue(decision.evaluate(crossing=True))
            remaining = controller.status["remaining_seconds"]
            self.assertIsNone(decision.evaluate(crossing=True))
            self.assertEqual(controller.status["remaining_seconds"], remaining)
            controller.advance()

        self.assertTrue(decision.evaluate(crossing=True))
        self.assertEqual(controller.phase, "STOP_RED")
        self.assertEqual(controller.signals["vehicle"], "red")

    def test_new_crossing_in_final_red_requests_stop(self):
        controller = TrafficController()
        decision = DecisionLogic(controller)
        controller.advance(47)
        self.assertEqual(controller.phase, "F")
        self.assertTrue(decision.evaluate(crossing=True))
        self.assertEqual(controller.phase, "STOP_RED")

    def test_rejects_invalid_synthetic_inputs(self):
        decision = DecisionLogic(TrafficController())
        for values in ((-1, 0, False), (0, -1, False), (0, 0, 1)):
            with self.assertRaises(ValueError):
                decision.evaluate(*values)


if __name__ == "__main__":
    unittest.main()
