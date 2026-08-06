import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


MOBILE_PAGE_HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>PiMP3bPlus Remote</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; margin: 0; background: #f3f6f8; color: #0f172a; }
    .wrap { max-width: 720px; margin: 0 auto; padding: 16px; }
    .card { background: #ffffff; border-radius: 14px; padding: 14px; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08); margin-bottom: 12px; }
    h1 { margin: 0 0 8px; font-size: 1.3rem; }
    h2 { margin: 0 0 8px; font-size: 1rem; }
    .muted { color: #475569; font-size: 0.9rem; }
    .song { font-size: 1.05rem; margin: 6px 0; word-break: break-word; }
    .row { display: flex; gap: 8px; flex-wrap: wrap; }
    button { border: none; background: #0ea5e9; color: #fff; border-radius: 10px; padding: 12px 14px; font-weight: 600; min-width: 96px; }
    button.secondary { background: #334155; }
    button.ghost { background: #e2e8f0; color: #0f172a; }
    select { width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #cbd5e1; }
    .chip { display: inline-block; border-radius: 999px; padding: 4px 8px; margin-right: 6px; font-size: 0.82rem; background: #dbeafe; color: #1e3a8a; }
    .progress { width: 100%; height: 8px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
    .bar { height: 100%; width: 0%; background: #0ea5e9; }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"card\">
      <h1>PiMP3bPlus Remote</h1>
      <div id=\"song\" class=\"song\">No song loaded</div>
      <div class=\"muted\" id=\"meta\">State unknown</div>
      <div class=\"progress\" style=\"margin-top:10px\"><div id=\"bar\" class=\"bar\"></div></div>
      <div class=\"muted\" id=\"time\" style=\"margin-top:6px\">00:00 / 00:00</div>
    </div>

    <div class=\"card\">
      <h2>Playback</h2>
      <div class=\"row\">
        <button class=\"secondary\" onclick=\"sendAction('PREV')\">Prev</button>
        <button onclick=\"sendAction('PLAY_PAUSE')\">Play/Pause</button>
        <button class=\"secondary\" onclick=\"sendAction('NEXT')\">Next</button>
      </div>
      <div class=\"row\" style=\"margin-top:8px\">
        <button class=\"ghost\" onclick=\"sendAction('VOL_DOWN')\">Vol -</button>
        <button class=\"ghost\" onclick=\"sendAction('VOL_UP')\">Vol +</button>
      </div>
    </div>

    <div class=\"card\">
      <h2>Modes</h2>
      <div class=\"row\">
        <button id=\"shuffleBtn\" class=\"ghost\" onclick=\"toggleMode('SHUFFLE')\">Shuffle</button>
        <button id=\"repeatBtn\" class=\"ghost\" onclick=\"toggleMode('REPEAT')\">Repeat</button>
      </div>
      <div style=\"margin-top:10px\">
        <span class=\"chip\" id=\"shuffleChip\">Shuffle: OFF</span>
        <span class=\"chip\" id=\"repeatChip\">Repeat: OFF</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>Pick Song</h2>
      <select id=\"songSelect\"></select>
      <div class=\"row\" style=\"margin-top:8px\">
        <button onclick=\"playSelectedSong()\">Play Selected</button>
        <button class=\"secondary\" onclick=\"refreshSongs()\">Refresh List</button>
      </div>
    </div>
  </div>

  <script>
    const fmt = (s) => {
      s = Math.max(0, parseInt(s || 0, 10));
      const m = String(Math.floor(s / 60)).padStart(2, '0');
      const r = String(s % 60).padStart(2, '0');
      return `${m}:${r}`;
    };

    async function postJson(path, payload) {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || {}),
      });
      return await res.json();
    }

    async function sendAction(action) {
      await postJson('/api/action', { action });
      await refreshStatus();
    }

    async function toggleMode(mode) {
      await postJson('/api/action', { action: mode === 'SHUFFLE' ? 'TOGGLE_SHUFFLE' : 'TOGGLE_REPEAT' });
      await refreshStatus();
    }

    async function playSelectedSong() {
      const song = document.getElementById('songSelect').value;
      if (!song) return;
      await postJson('/api/action', { action: 'PLAY_SONG', song });
      await refreshStatus();
    }

    async function refreshSongs() {
      const res = await fetch('/api/songs');
      const data = await res.json();
      const select = document.getElementById('songSelect');
      select.innerHTML = '';
      (data.songs || []).forEach((song) => {
        const opt = document.createElement('option');
        opt.value = song;
        opt.textContent = song;
        select.appendChild(opt);
      });
      if (data.current_song) {
        select.value = data.current_song;
      }
    }

    async function refreshStatus() {
      const res = await fetch('/api/status');
      const data = await res.json();
      document.getElementById('song').textContent = data.song || 'No song loaded';
      document.getElementById('meta').textContent = `${data.state} | ${data.paused ? 'Paused' : (data.playing ? 'Playing' : 'Stopped')} | Vol ${Math.round((data.volume || 0) * 100)}%`;
      document.getElementById('shuffleChip').textContent = `Shuffle: ${data.shuffle ? 'ON' : 'OFF'}`;
      document.getElementById('repeatChip').textContent = `Repeat: ${data.repeat ? 'ON' : 'OFF'}`;

      const pos = data.position_s || 0;
      const len = data.length_s || 0;
      document.getElementById('time').textContent = `${fmt(pos)} / ${fmt(len)}`;
      const pct = len > 0 ? Math.min(100, Math.max(0, Math.round((pos / len) * 100))) : 0;
      document.getElementById('bar').style.width = `${pct}%`;
    }

    (async function init() {
      await refreshSongs();
      await refreshStatus();
      setInterval(refreshStatus, 1500);
    })();
  </script>
</body>
</html>
"""


class _ControlRequestHandler(BaseHTTPRequestHandler):
    def _json_response(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html_response(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        controller = self.server.controller

        if self.path == "/":
            self._html_response(MOBILE_PAGE_HTML)
            return

        if self.path == "/api/status":
            self._json_response(controller.get_web_status())
            return

        if self.path == "/api/songs":
            self._json_response(controller.get_web_songs())
            return

        self._json_response({"error": "Not found"}, status=404)

    def do_POST(self):
        controller = self.server.controller

        if self.path != "/api/action":
            self._json_response({"error": "Not found"}, status=404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._json_response({"ok": False, "error": "Invalid JSON payload"}, status=400)
            return

        action = payload.get("action")
        result = controller.handle_web_action(action, payload)
        self._json_response(result)

    def log_message(self, fmt, *args):
        logging.debug("web: " + fmt, *args)


class PiMP3WebServer:
    def __init__(self, controller, host="0.0.0.0", port=8080):
        self.controller = controller
        self.host = host
        self.port = int(port)
        self._httpd = None
        self._thread = None

    def start(self):
        if self._httpd is not None:
            return True

        try:
            self._httpd = ThreadingHTTPServer((self.host, self.port), _ControlRequestHandler)
            self._httpd.controller = self.controller
            self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
            self._thread.start()
            logging.info(f"Web control server started on http://0.0.0.0:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to start web control server: {e}")
            self._httpd = None
            self._thread = None
            return False

    def stop(self):
        if self._httpd is None:
            return
        try:
            self._httpd.shutdown()
            self._httpd.server_close()
        except Exception as e:
            logging.warning(f"Error while stopping web control server: {e}")
        self._httpd = None
        self._thread = None
