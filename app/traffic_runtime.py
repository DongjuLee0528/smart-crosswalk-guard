import argparse
import time
from threading import Event

from app.config import load_settings
from app.decision_logic import DecisionLogic
from app.traffic_controller import TrafficController


def run_realtime(controller, stop_event, on_tick=None):
    next_tick = time.monotonic() + 1
    while not stop_event.wait(max(0, next_tick - time.monotonic())):
        elapsed = int(time.monotonic() - next_tick) + 1
        if elapsed < 1:
            continue
        for _ in range(elapsed):
            controller.advance()
            if on_tick is not None:
                on_tick(controller.status)
        next_tick += elapsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the software-only traffic simulator")
    parser.add_argument("--waiting-count", type=int, default=0)
    parser.add_argument("--longest-wait-seconds", type=int, default=0)
    parser.add_argument("--crossing", action="store_true")
    parser.add_argument("--config", help="path to a JSON settings file")
    args = parser.parse_args()
    if args.waiting_count < 0 or args.longest_wait_seconds < 0:
        parser.error("waiting inputs must be non-negative")

    controller = TrafficController(load_settings(args.config) if args.config else None)
    decision = DecisionLogic(controller)

    def on_tick(status):
        decision.evaluate(args.waiting_count, args.longest_wait_seconds, args.crossing)
        print(controller.status, flush=True)

    print(controller.status, flush=True)
    try:
        run_realtime(controller, Event(), on_tick)
    except KeyboardInterrupt:
        pass
