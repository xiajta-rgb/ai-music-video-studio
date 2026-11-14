from __future__ import annotations

import json
import math
import random
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
DATA = ROOT / "data" / "style_profiles.json"


def load_profiles():
    return json.loads(DATA.read_text(encoding="utf-8"))


def slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text.strip().lower()).strip("-")
    return value[:48] or "untitled-composition"


def make_notes(scale, bars, density, seed):
    rng = random.Random(seed)
    notes = []
    steps = max(3, min(7, int(2 + density * 5)))
    for bar in range(bars):
        count = 3 + (bar + seed) % steps
        for idx in range(count):
            degree = (bar * 2 + idx * (1 if bar % 2 else 2) + rng.choice([-1, 0, 0, 1])) % len(scale)
            pitch = scale[degree] + 60 + (12 if bar >= bars * 0.52 and idx % 4 == 0 else 0)
            start = bar * 4 + idx * (4 / count)
            duration = max(0.18, min(0.9, 3.2 / count + (0.12 if idx == count - 1 else 0)))
            notes.append({"start": round(start, 3), "duration": round(duration, 3), "pitch": pitch, "velocity": 70 + ((idx * 7 + bar) % 28)})
    return notes


def compose(payload):
    profiles = load_profiles()
    style_id = payload.get("style", "chinese-pentatonic")
    profile = profiles.get(style_id, profiles["chinese-pentatonic"])
    prompt = str(payload.get("prompt", "月下古城，灯火与风穿过长街"))[:160]
    tempo = max(60, min(180, int(payload.get("tempo", profile["tempo"]))))
    bars = max(8, min(64, int(payload.get("bars", 32))))
    density = max(0.1, min(1.0, float(payload.get("density", 0.72))))
    seed = sum(ord(c) for c in prompt) + bars + tempo
    scale = profile["scale_midi"]
    notes = make_notes(scale, bars, density, seed)
    section_size = max(4, bars // 4)
    sections = []
    names = ["引子", "主题", "展开", "回望"]
    for idx, name in enumerate(names):
        start = idx * section_size
        end = min(bars, (idx + 1) * section_size)
        sections.append({"name": name, "startBar": start + 1, "endBar": end, "caption": profile["captions"][idx]})
    tracks = []
    for i, item in enumerate(profile["tracks"]):
        track_notes = []
        for n in notes:
            if item["role"] == "melody" and i != 0:
                continue
            if item["role"] == "harmony" and n["pitch"] % 3 == 1:
                continue
            if item["role"] == "rhythm":
                continue
            track_notes.append({**n, "pitch": n["pitch"] - item.get("transpose", 0), "velocity": max(35, n["velocity"] - i * 5)})
        if item["role"] == "rhythm":
            for beat in range(bars * 4):
                if beat % 2 == 0 or (density > 0.65 and beat % 4 == 3):
                    track_notes.append({"start": beat, "duration": 0.12, "pitch": 36 if beat % 4 == 0 else 42, "velocity": 52 + (beat % 3) * 8})
        tracks.append({"name": item["name"], "instrument": item["instrument"], "role": item["role"], "color": item["color"], "notes": track_notes[:600]})
    return {
        "id": slug(prompt) + "-" + str(seed % 10000),
        "prompt": prompt,
        "style": {"id": style_id, "name": profile["name"], "mode": profile["mode"], "palette": profile["palette"], "tags": profile["tags"]},
        "tempo": tempo,
        "bars": bars,
        "density": density,
        "scale": profile["scale"],
        "sections": sections,
        "tracks": tracks,
        "visual": {"background": "#060b18", "grid": "#1c3154", "glow": profile["palette"][1], "particleCount": int(80 + density * 160), "subtitleStyle": "chapter-caption"},
        "export": {"midi": True, "musicxml": True, "wav": True, "mp4": True, "nextStep": "Connect a renderer such as Remotion, Blender, or FFmpeg to the same timeline JSON."},
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json({"ok": True, "service": "ai-music-video-studio"})
        if path == "/api/styles":
            return self._json(load_profiles())
        if path.startswith("/api/"):
            return self._json({"error": "not found"}, 404)
        file_path = PUBLIC / ("index.html" if path == "/" else path.lstrip("/"))
        if not file_path.exists() or not file_path.is_file():
            return self._json({"error": "asset not found"}, 404)
        content_type = "text/html; charset=utf-8" if file_path.suffix == ".html" else "text/css; charset=utf-8" if file_path.suffix == ".css" else "application/javascript; charset=utf-8" if file_path.suffix == ".js" else "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if urlparse(self.path).path != "/api/compose":
            return self._json({"error": "not found"}, 404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            return self._json(compose(payload))
        except Exception as exc:
            return self._json({"error": str(exc)}, 400)

    def log_message(self, fmt, *args):
        print("[server] " + fmt % args)


if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", "4173"))
    print(f"AI Music Video Studio running at http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
