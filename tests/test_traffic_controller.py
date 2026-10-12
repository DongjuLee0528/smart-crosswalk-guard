import unittest

from app.traffic_controller import TrafficController


class TrafficControllerTests(unittest.TestCase):
    def test_normal_cycle(self):
        controller = TrafficController()
        for seconds, phase, signals in (
            (30, "B", ("red", "yellow")),
            (3, "C", ("red", "red")),
            (1, "D", ("green", "red")),
            (10, "E", ("green_blink", "red")),
            (3, "F", ("red", "red")),
            (2, "A", ("red", "green")),
        ):
            controller.advance(seconds)
            self.assertEqual(controller.phase, phase)
            self.assertEqual(
                (controller.signals["pedestrian"], controller.signals["vehicle"]),
                signals,
            )

    def test_pedestrian_request_respects_minimum_green(self):
        controller = TrafficController()
        controller.advance(7)
        self.assertFalse(controller.request_ped())
        controller.advance()
        self.assertTrue(controller.request_ped())
        self.assertEqual(controller.phase, "B")

        controller = TrafficController()
        controller.advance(20)
        self.assertTrue(controller.request_ped())
        self.assertEqual(controller.phase, "B")

    def test_extension_is_limited_to_five_seconds(self):
        controller = TrafficController()
        controller.advance(47)
        self.assertEqual(controller.phase, "F")
        self.assertEqual(controller.status["remaining_seconds"], 2)
        for _ in range(5):
            self.assertTrue(controller.request_extend())
        self.assertFalse(controller.request_extend())
        self.assertEqual(controller.status["remaining_seconds"], 7)
        controller.advance(6)
        self.assertEqual(controller.phase, "F")
        controller.advance()
        self.assertEqual(controller.phase, "A")
        controller.advance(30)
        self.assertEqual(controller.phase, "B")

    def test_car_stop_passes_through_yellow_and_holds_red(self):
        controller = TrafficController()
        self.assertTrue(controller.request_car_stop())
        self.assertEqual(controller.phase, "STOP_YELLOW")
        controller.advance()
        self.assertEqual(controller.phase, "STOP_RED")
        controller.advance(30)
        self.assertEqual(controller.phase, "STOP_RED")
        self.assertEqual(controller.status["remaining_seconds"], None)
        self.assertEqual(controller.status["heartbeat"], 31)
        self.assertTrue(controller.release_car_stop())
        controller.advance()
        self.assertEqual(controller.phase, "D")

    def test_status_is_read_only_and_heartbeat_advances_each_second(self):
        controller = TrafficController()
        self.assertEqual(
            controller.status,
            {"phase": "A", "remaining_seconds": 30, "heartbeat": 0},
        )
        controller.advance(7)
        self.assertEqual(controller.status["remaining_seconds"], 23)
        self.assertEqual(controller.status["heartbeat"], 7)
        snapshot = controller.status
        snapshot["phase"] = "F"
        self.assertEqual(controller.phase, "A")
        with self.assertRaises(AttributeError):
            controller.phase = "F"

    def test_invalid_requests_and_time(self):
        controller = TrafficController()
        self.assertFalse(controller.request_extend())
        controller.advance(34)
        self.assertTrue(controller.request_car_stop())
        self.assertEqual(controller.phase, "STOP_RED")
        with self.assertRaises(ValueError):
            controller.advance(-1)


if __name__ == "__main__":
    unittest.main()
