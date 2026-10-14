# smart-crosswalk-guard

A diorama prototype of an AI-assisted crosswalk guard. The repository currently includes a software-only traffic-controller simulator. Camera processing and firmware have not been implemented.

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

Run the software tests with `python3 -m unittest discover -s tests`.

## License

Original material created by Lee Dongju is available for non-commercial educational and research use under the custom [LICENSE](LICENSE). Commercial use requires contacting Lee Dongju and receiving explicit prior written permission; see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party materials remain subject to their own licenses.

This is a source-available license, not an OSI-approved open-source license.
