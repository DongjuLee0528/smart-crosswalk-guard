import time
from threading import Event

from app.traffic_controller import TrafficController


def run_realtime(controller, stop_event, on_tick=None):
    next_tick = time.monotonic() + 1
    while not stop_event.wait(max(0, next_tick - time.monotonic())):
        elapsed = int(time.monotonic() - next_tick) + 1
        if elapsed < 1:
            continue
        controller.advance(elapsed)
        next_tick += elapsed
        if on_tick is not None:
            on_tick(controller.status)


if __name__ == "__main__":
    controller = TrafficController()
    print(controller.status, flush=True)
    try:
        run_realtime(controller, Event(), lambda status: print(status, flush=True))
    except KeyboardInterrupt:
        pass
