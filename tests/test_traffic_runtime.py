import threading
import unittest
from unittest.mock import patch

from app.decision_logic import DecisionLogic
from app.traffic_controller import TrafficController
from app.traffic_runtime import run_realtime


class TrafficRuntimeTests(unittest.TestCase):
    def test_delayed_wake_delivers_every_missed_tick(self):
        controller = TrafficController()
        heartbeats = []

        class StopAfterOneWake:
            calls = 0

            def wait(self, timeout):
                self.calls += 1
                return self.calls > 1

        with patch("app.traffic_runtime.time.monotonic", side_effect=[0, 0, 3.2, 3.2]):
            run_realtime(controller, StopAfterOneWake(), lambda status: heartbeats.append(status["heartbeat"]))

        self.assertEqual(heartbeats, [1, 2, 3])

    def test_wall_clock_updates_status_and_stops(self):
        controller = TrafficController()
        stop_event = threading.Event()
        ticks = []
        second_tick = threading.Event()

        def on_tick(status):
            ticks.append(status)
            if status["heartbeat"] >= 2:
                second_tick.set()

        worker = threading.Thread(target=run_realtime, args=(controller, stop_event, on_tick))
        worker.start()
        try:
            self.assertTrue(second_tick.wait(3.5), "heartbeat did not advance with wall-clock time")
        finally:
            stop_event.set()
            worker.join(timeout=1)

        self.assertFalse(worker.is_alive())
        self.assertGreaterEqual(controller.status["heartbeat"], 2)
        self.assertEqual(controller.status["remaining_seconds"], 30 - controller.status["heartbeat"])
        self.assertEqual(ticks[-1], controller.status)

    def test_runner_delivers_ticks_to_decision_logic(self):
        controller = TrafficController()
        decision = DecisionLogic(controller)
        stop_event = threading.Event()
        requested = threading.Event()

        def on_tick(status):
            decision.evaluate(crossing=True)
            requested.set()

        worker = threading.Thread(target=run_realtime, args=(controller, stop_event, on_tick))
        worker.start()
        try:
            self.assertTrue(requested.wait(2), "decision logic did not receive a real-time tick")
        finally:
            stop_event.set()
            worker.join(timeout=1)

        self.assertFalse(worker.is_alive())
        self.assertEqual(controller.phase, "STOP_YELLOW")
        self.assertGreaterEqual(controller.status["heartbeat"], 1)


if __name__ == "__main__":
    unittest.main()
