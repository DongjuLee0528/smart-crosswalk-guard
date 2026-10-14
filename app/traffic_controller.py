PHASE_SECONDS = {"A": 30, "B": 3, "C": 1, "D": 10, "E": 3, "F": 2}
MIN_GREEN_SECONDS = 8
SIGNALS = {
    "A": ("red", "green"),
    "B": ("red", "yellow"),
    "C": ("red", "red"),
    "D": ("green", "red"),
    "E": ("green_blink", "red"),
    "F": ("red", "red"),
    "STOP_YELLOW": ("red", "yellow"),
    "STOP_RED": ("red", "red"),
}
NEXT_PHASE = {"A": "B", "B": "C", "C": "D", "D": "E", "E": "F", "F": "A"}


class TrafficController:
    def __init__(self):
        self._phase = "A"
        self._elapsed = 0
        self._extension = 0
        self._heartbeat = 0

    @property
    def phase(self):
        return self._phase

    @property
    def status(self):
        remaining = None
        if self._phase == "STOP_YELLOW":
            remaining = 1 - self._elapsed
        elif self._phase != "STOP_RED":
            remaining = PHASE_SECONDS[self._phase] + (self._extension if self._phase == "F" else 0) - self._elapsed
        return {"phase": self._phase, "remaining_seconds": remaining, "heartbeat": self._heartbeat}

    @property
    def signals(self):
        ped, car = SIGNALS[self._phase]
        return {"pedestrian": ped, "vehicle": car}

    def advance(self, seconds=1):
        if type(seconds) is not int or seconds < 0:
            raise ValueError("seconds must be a non-negative integer")
        for _ in range(seconds):
            self._heartbeat += 1
            if self._phase == "STOP_RED":
                continue
            self._elapsed += 1
            duration = 1 if self._phase == "STOP_YELLOW" else PHASE_SECONDS[self._phase] + (self._extension if self._phase == "F" else 0)
            if self._elapsed < duration:
                continue
            self._phase = "STOP_RED" if self._phase == "STOP_YELLOW" else NEXT_PHASE[self._phase]
            self._elapsed = 0
            if self._phase == "F":
                self._extension = 0

    def request_ped(self):
        if self._phase != "A" or self._elapsed < MIN_GREEN_SECONDS:
            return False
        self._phase = "B"
        self._elapsed = 0
        return True

    def request_extend(self):
        if self._phase != "F" or self._extension >= 5:
            return False
        self._extension += 1
        return True

    def request_car_stop(self):
        if self._phase in ("STOP_YELLOW", "STOP_RED"):
            return True
        self._phase = "STOP_YELLOW" if self.signals["vehicle"] in ("green", "yellow") else "STOP_RED"
        self._elapsed = 0
        return True

    def release_car_stop(self):
        if self._phase != "STOP_RED":
            return False
        self._phase = "C"
        self._elapsed = 0
        return True
