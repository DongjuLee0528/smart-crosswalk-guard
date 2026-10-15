import json
import logging
from copy import deepcopy
from pathlib import Path


DEFAULT_SETTINGS = {
    "waiting_count_threshold": 3,
    "waiting_seconds_threshold": 20,
    "min_green_seconds": 8,
    "extension_step_seconds": 1,
    "max_extension_seconds": 5,
    "barrier_wait_seconds": 0,
    "barrier_descent_seconds": 2,
    "entry_confirmation_frames": 3,
    "exit_confirmation_seconds": 2,
    "waiting_presence_seconds": 2,
    "voice_repeat_seconds": 5,
    "roi": {
        "waiting_north": [330, 20, 570, 90],
        "waiting_south": [330, 510, 570, 580],
        "warning_north": [330, 90, 570, 140],
        "warning_south": [330, 460, 570, 510],
        "crosswalk": [350, 140, 550, 460],
    },
}
MINIMUMS = {
    "waiting_count_threshold": 1,
    "waiting_seconds_threshold": 1,
    "min_green_seconds": 1,
    "extension_step_seconds": 1,
    "max_extension_seconds": 0,
    "barrier_wait_seconds": 0,
    "barrier_descent_seconds": 1,
    "entry_confirmation_frames": 1,
    "exit_confirmation_seconds": 1,
    "waiting_presence_seconds": 0,
    "voice_repeat_seconds": 1,
}
MAXIMUMS = {"min_green_seconds": 30, "max_extension_seconds": 10}
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "config.json"


def _valid_roi(value):
    if type(value) is not dict or value.keys() != DEFAULT_SETTINGS["roi"].keys():
        return False
    for box in value.values():
        if type(box) is not list or len(box) != 4 or any(type(edge) is not int or edge < 0 for edge in box):
            return False
        if box[0] >= box[2] or box[1] >= box[3]:
            return False
    return True


def load_settings(path=DEFAULT_PATH):
    with open(path, encoding="utf-8") as file:
        configured = json.load(file)
    if type(configured) is not dict:
        raise ValueError("config root must be an object")

    settings = {}
    for name, default in DEFAULT_SETTINGS.items():
        value = configured.get(name)
        valid = _valid_roi(value) if name == "roi" else (
            type(value) is int
            and value >= MINIMUMS[name]
            and (name not in MAXIMUMS or value <= MAXIMUMS[name])
        )
        if not valid:
            logging.warning("Invalid or missing %s; using default", name)
        settings[name] = value if valid else deepcopy(default)

    if settings["max_extension_seconds"] and settings["extension_step_seconds"] > settings["max_extension_seconds"]:
        logging.warning("Extension step exceeds maximum; using default step")
        settings["extension_step_seconds"] = DEFAULT_SETTINGS["extension_step_seconds"]
    return settings
