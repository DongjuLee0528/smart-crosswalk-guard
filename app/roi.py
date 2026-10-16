import math
from numbers import Real

from app.config import load_settings


ZONE_PRIORITY = ("crosswalk", "warning_north", "warning_south", "waiting_north", "waiting_south")


class RoiClassifier:
    def __init__(self, settings=None):
        self.settings = load_settings() if settings is None else settings
        self._people = {}
        self._last_timestamp = None

    def update(self, detections, timestamp):
        if not isinstance(timestamp, Real) or isinstance(timestamp, bool) or not math.isfinite(timestamp) or timestamp < 0:
            raise ValueError("timestamp must be a non-negative finite number")
        if self._last_timestamp is not None and timestamp < self._last_timestamp:
            raise ValueError("timestamp must not move backwards")
        if not isinstance(detections, dict):
            raise ValueError("detections must map person IDs to bounding boxes")

        zones = {}
        for person_id, box in detections.items():
            if not isinstance(box, (list, tuple)) or len(box) != 4 or any(
                not isinstance(edge, Real) or isinstance(edge, bool) or not math.isfinite(edge) or edge < 0
                for edge in box
            ) or box[0] >= box[2] or box[1] >= box[3]:
                raise ValueError("each detection must have a valid [left, top, right, bottom] box")
            foot_x = (box[0] + box[2]) / 2
            foot_y = box[3]
            zones[person_id] = None
            for name in ZONE_PRIORITY:
                left, top, right, bottom = self.settings["roi"][name]
                if left <= foot_x < right and top <= foot_y < bottom:
                    zones[person_id] = name
                    break

        self._last_timestamp = timestamp
        for person_id in set(self._people) | set(zones):
            state = self._people.get(person_id)
            zone = zones.get(person_id)
            if zone is None:
                if state is not None:
                    state["candidate"] = None
                    state["frames"] = 0
                    if timestamp - state["last_seen"] >= self.settings["exit_confirmation_seconds"]:
                        del self._people[person_id]
                continue

            if state is None:
                state = {"zone": None, "candidate": None, "frames": 0, "last_seen": timestamp}
                self._people[person_id] = state
            state["frames"] = state["frames"] + 1 if state["candidate"] == zone else 1
            state["candidate"] = zone
            state["last_seen"] = timestamp
            if state["frames"] >= self.settings["entry_confirmation_frames"]:
                state["zone"] = zone

        return {person_id: state["zone"] for person_id, state in self._people.items() if state["zone"] is not None}
