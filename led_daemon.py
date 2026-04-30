import socket, os, json, threading, sys, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from const import const

SOCK_PATH = '/tmp/ledboard_led.sock'
_strip = None
_lock = threading.Lock()
_flask_active = False  # True while Flask owns the strip; suppresses Qt patch calls


def _init():
    global _strip
    try:
        from rpi_ws281x import PixelStrip
        _strip = PixelStrip(const.TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
    except ImportError:
        from neopixel import Adafruit_NeoPixel
        _strip = Adafruit_NeoPixel(const.TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
    _strip.begin()
    _strip.show()


def _handle(cmd):
    global _flask_active
    with _lock:
        source = cmd.get('source', 'qt')

        # Suppress all timer-driven Qt commands while Flask owns the strip
        if _flask_active and source == 'qt-timer':
            return

        if cmd['cmd'] == 'off':
            # Flask off: stay active (keep suppressing timer). Qt off: release.
            _flask_active = (source == 'flask')
            for i in range(const.TOTAL_LED_COUNT):
                _strip.setPixelColorRGB(i, 0, 0, 0)
            _strip.show()
        elif cmd['cmd'] == 'light':
            _flask_active = (source == 'flask')
            v = const.LED_VALUE
            for i in range(const.TOTAL_LED_COUNT):
                _strip.setPixelColorRGB(i, 0, 0, 0)
            for h in cmd.get('start', []):
                if h > 0: _strip.setPixelColorRGB(h - 1, 0, v, 0)
            for h in cmd.get('prob', []):
                if h > 0: _strip.setPixelColorRGB(h - 1, 0, 0, v)
            for h in cmd.get('fin', []):
                if h > 0: _strip.setPixelColorRGB(h - 1, v, 0, 0)
            _strip.show()
        elif cmd['cmd'] == 'raw':
            _flask_active = (source == 'flask')
            for i in range(const.TOTAL_LED_COUNT):
                _strip.setPixelColorRGB(i, 0, 0, 0)
            for pix in cmd.get('pixels', []):
                i, r, g, b = pix
                print("[daemon raw] setPixelColorRGB(%s, r=%s, g=%s, b=%s)" % (i, r, g, b), flush=True)
                _strip.setPixelColorRGB(i, r, g, b)
            _strip.show()
        elif cmd['cmd'] == 'patch':
            for pix in cmd.get('pixels', []):
                i, r, g, b = pix
                _strip.setPixelColorRGB(i, r, g, b)
            _strip.show()


def _client_thread(conn):
    try:
        data = b''
        while b'\n' not in data:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        print("[led_daemon] received: %s" % data.strip(), flush=True)
        cmd = json.loads(data.strip().decode('utf-8'))
        _handle(cmd)
        conn.sendall(b'{"ok":true}\n')
    except Exception as e:
        print("[led_daemon] exception in _client_thread: %s" % e, flush=True)
        try:
            conn.sendall(json.dumps({'ok': False, 'error': str(e)}).encode() + b'\n')
        except Exception:
            pass
    finally:
        conn.close()


if __name__ == '__main__':
    const.initConfigVariables()
    if const.LINUX != 1:
        print("LINUX=0, daemon not needed", flush=True)
        sys.exit(0)
    _init()
    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCK_PATH)
    os.chmod(SOCK_PATH, 0o666)
    srv.listen(5)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    print("LED daemon listening on %s" % SOCK_PATH, flush=True)
    while True:
        conn, _ = srv.accept()
        _client_thread(conn)
