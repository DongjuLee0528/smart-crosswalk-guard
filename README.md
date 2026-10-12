# smart-crosswalk-guard

A diorama prototype of an AI-assisted crosswalk guard. The repository currently contains the project structure; the runtime and firmware have not been implemented.

## Project Structure

- `app/`: Python code on the Arduino UNO Q Linux side for camera input, detection, decision logic, and the traffic-controller simulator
- `firmware/`: Arduino MCU code for traffic lights, barriers, and warning lights
- `assets/models/`: detection models used by the demonstration
- `assets/audio/`: recorded voice prompts
- `diorama/`: fabrication and 3D-printing files
- `tests/`: automated tests

The [Notion project page](https://app.notion.com/p/3f22febccaee80819442f99852cba8d5) contains the design and implementation specification.

The current demonstration settings are a 30-second vehicle-green phase (8-second minimum), a pedestrian request after 20 seconds of waiting, and a 2-second barrier descent. If a person is in front of a barrier, that barrier remains raised for the current cycle.

## License

Original material created by Lee Dongju is available for non-commercial educational and research use under the custom [LICENSE](LICENSE). Commercial use requires contacting Lee Dongju and receiving explicit prior written permission; see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party materials remain subject to their own licenses.

This is a source-available license, not an OSI-approved open-source license.
