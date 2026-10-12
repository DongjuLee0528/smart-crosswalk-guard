import threading
import unittest

from app.traffic_controller import TrafficController
from app.traffic_runtime import run_realtime


class TrafficRuntimeTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
