"""
File-based lock for LED strip access.
Flask acquires and releases per LED request.
Qt app acquires once at startup and holds for its lifetime.
"""
import fcntl
import os

LOCK_PATH = '/tmp/ledboard_led.lock'
_lock_fh = None


def acquire():
    """Try to acquire the LED lock. Returns True if acquired, False if held by another process."""
    global _lock_fh
    try:
        fd = os.open(LOCK_PATH, os.O_WRONLY | os.O_CREAT, 0o666)
        _lock_fh = os.fdopen(fd, 'w')
        fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        if _lock_fh:
            _lock_fh.close()
            _lock_fh = None
        return False


def release():
    global _lock_fh
    if _lock_fh:
        fcntl.flock(_lock_fh, fcntl.LOCK_UN)
        _lock_fh.close()
        _lock_fh = None
