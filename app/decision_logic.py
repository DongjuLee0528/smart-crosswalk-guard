from app.traffic_controller import PHASE_SECONDS


class DecisionLogic:
    def __init__(self, controller):
        self.controller = controller
        self._eligible_crossing = False
        self._last_extension_heartbeat = -1

    def evaluate(self, waiting_count=0, longest_wait_seconds=0, crossing=False):
        if type(waiting_count) is not int or waiting_count < 0:
            raise ValueError("waiting_count must be a non-negative integer")
        if type(longest_wait_seconds) is not int or longest_wait_seconds < 0:
            raise ValueError("longest_wait_seconds must be a non-negative integer")
        if type(crossing) is not bool:
            raise ValueError("crossing must be a boolean")

        status = self.controller.status
        phase = status["phase"]

        if phase == "E" and status["remaining_seconds"] == 1:
            self._eligible_crossing = crossing
        elif phase == "A":
            self._eligible_crossing = False

        if phase == "STOP_RED":
            if not crossing:
                return self.controller.release_car_stop()
            return None
        if crossing and phase in ("A", "B", "C"):
            return self.controller.request_car_stop()
        if crossing and phase == "F":
            if not self._eligible_crossing:
                return self.controller.request_car_stop()
            if self._last_extension_heartbeat != status["heartbeat"]:
                self._last_extension_heartbeat = status["heartbeat"]
                if self.controller.request_extend():
                    return True
                return self.controller.request_car_stop()
            return None
        if (
            phase == "A"
            and status["remaining_seconds"] <= PHASE_SECONDS["A"] - self.controller.settings["min_green_seconds"]
            and (
                waiting_count >= self.controller.settings["waiting_count_threshold"]
                or longest_wait_seconds >= self.controller.settings["waiting_seconds_threshold"]
            )
        ):
            return self.controller.request_ped()
        return None
