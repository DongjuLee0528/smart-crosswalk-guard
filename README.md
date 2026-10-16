# smart-crosswalk-guard

A diorama prototype of an AI-assisted crosswalk guard. The repository currently includes a software-only traffic-controller simulator and ROI classifier. Camera input, person detection, and firmware have not been implemented.

## Project Structure

- `app/`: Python code on the Arduino UNO Q Linux side for camera input, detection, decision logic, and the traffic-controller simulator
- `firmware/`: Arduino MCU code for traffic lights, barriers, and warning lights
- `assets/models/`: detection models used by the demonstration
- `assets/audio/`: recorded voice prompts
- `diorama/`: fabrication and 3D-printing files
- `tests/`: automated tests

The [Notion project page](https://app.notion.com/p/3f22febccaee80819442f99852cba8d5) contains the design and implementation specification.

The current demonstration settings are a 30-second vehicle-green phase (8-second minimum), a pedestrian request after 20 seconds of waiting, and a 2-second barrier descent. If a person is in front of a barrier, that barrier remains raised for the current cycle. The simulator accepts pedestrian, extension, and vehicle-stop requests. Its read-only status reports the current phase, remaining seconds, and a heartbeat counter that advances once per second when the real-time runner is active. `DecisionLogic.evaluate()` accepts synthetic waiting and crossing inputs, reads that status, and sends requests to the simulator. Camera detection and barrier decisions are separate future work.

Run the software-only real-time simulator with `python3 -m app.traffic_runtime`. It prints the status each second; press Ctrl+C to stop. Supply synthetic inputs with `--waiting-count 3`, `--longest-wait-seconds 20`, or `--crossing`. The runner can also be called with a `threading.Event` to stop it and an optional status callback.

The command-line runner calls `DecisionLogic.evaluate()` on each tick. The controller enforces the eight-second minimum green phase; crossing inputs can request a vehicle stop or extend the final all-red phase.

## Configuration

Edit `config.json` and restart the simulator to change the waiting-count and waiting-time thresholds, minimum vehicle green, pedestrian extension step and cap, barrier wait and descent times, entry and exit confirmation, waiting-person dwell time, voice repeat interval, or ROI coordinates. The same settings file is loaded by the traffic controller and decision logic. Use `--config path/to/settings.json` to run an experiment with another file without editing the default.

ROI boxes use `[left, top, right, bottom]` pixel coordinates. The warning-zone horizontal bounds initially reuse the waiting-zone bounds because the specification does not fix them. All ROI coordinates need calibration after the camera position is fixed. The zero-second barrier wait means no extra delay before the specified two-second descent. Camera, barrier, and audio consumers are not implemented yet; their settings are loaded and validated for those later features.

Invalid individual settings fall back to their defaults with a warning. A missing or malformed settings file stops startup so a configuration error is visible.

## ROI Classification

`RoiClassifier.update(detections, timestamp)` accepts one video frame as a mapping from stable person IDs to `[left, top, right, bottom]` bounding boxes and a monotonic timestamp in seconds. It returns confirmed person IDs mapped to ROI names. The box's bottom center is the foot point. A person enters a zone after three consecutive frames in that zone and leaves after two seconds without detection in any ROI. Both thresholds and all ROI boxes come from `config.json`. If boxes overlap, crosswalk takes priority, then warning, then waiting. The ROI coordinates are provisional until the camera and diorama are calibrated. This classifier currently uses synthetic detections; a camera and person tracker are not connected.

Run the software tests with `python3 -m unittest discover -s tests`.

## License

Original material created by Lee Dongju is available for non-commercial educational and research use under the custom [LICENSE](LICENSE). Commercial use requires contacting Lee Dongju and receiving explicit prior written permission; see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party materials remain subject to their own licenses.

This is a source-available license, not an OSI-approved open-source license.
