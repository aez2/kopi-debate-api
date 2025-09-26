import signal
from contextlib import contextmanager

@contextmanager
def time_limit(seconds: int):
    def handler(signum, frame):
        raise TimeoutError("response timed out")
    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)
        yield
    finally:
        try:
            signal.alarm(0)
        except Exception:
            pass
