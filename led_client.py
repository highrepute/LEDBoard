import socket, json

SOCK_PATH = '/tmp/ledboard_led.sock'


def _send(cmd):
    """Send a command to the LED daemon. Fails silently if daemon not running."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCK_PATH)
        s.sendall(json.dumps(cmd).encode() + b'\n')
        s.recv(64)
        s.close()
    except OSError:
        pass


def light_problem(start, prob, fin, source='qt'):
    _send({'cmd': 'light', 'source': source, 'start': list(start), 'prob': list(prob), 'fin': list(fin)})


def off(source='qt'):
    _send({'cmd': 'off', 'source': source})


def raw(pixels, source='qt'):
    """pixels: list of [index, r, g, b] or dict {index: (r, g, b)}"""
    if isinstance(pixels, dict):
        pixels = [[i, r, g, b] for i, (r, g, b) in pixels.items()]
    _send({'cmd': 'raw', 'source': source, 'pixels': pixels})


def patch(pixels, source='qt'):
    """Set specific pixels without clearing the strip first."""
    if isinstance(pixels, dict):
        pixels = [[i, r, g, b] for i, (r, g, b) in pixels.items()]
    _send({'cmd': 'patch', 'source': source, 'pixels': pixels})
