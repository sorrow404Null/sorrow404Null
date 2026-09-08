#!/usr/bin/env python3
"""Generate a NetEase Cloud Music listening stats SVG for the profile README."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

UID = os.environ.get("NETEASE_UID", "538737104")
MUSIC_U = os.environ.get("MUSIC_U", "").strip()
OUT = Path(os.environ.get("NETEASE_SVG_OUT", "assets/netease-stats.svg"))


def fetch_detail() -> dict:
    req = urllib.request.Request(
        f"https://music.163.com/api/v1/user/detail/{UID}",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.163.com/",
            "Cookie": f"MUSIC_U={MUSIC_U}" if MUSIC_U else "",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_songs(n: int) -> str:
    if n >= 10_000:
        return f"{n / 1000:.1f}k"
    return f"{n:,}"


def render(detail: dict) -> str:
    listen = int(detail.get("listenSongs") or 0)
    level = int(detail.get("level") or 0)
    days = int(detail.get("createDays") or 0)
    nick = esc((detail.get("profile") or {}).get("nickname") or "netease")

    listen_label = format_songs(listen)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="520" height="120" viewBox="0 0 520 120" role="img">
  <title>{nick} - NetEase listening</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1a0a0c"/>
      <stop offset="100%" stop-color="#2b0f14"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#e60026"/>
      <stop offset="100%" stop-color="#ff4d6d"/>
    </linearGradient>
  </defs>
  <rect width="520" height="120" rx="14" fill="url(#bg)" stroke="#5a1822" stroke-width="1"/>
  <rect x="0" y="0" width="6" height="120" rx="3" fill="url(#accent)"/>
  <text x="24" y="32" fill="#ff8a9a" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">NETEASE / {nick}</text>
  <text x="24" y="68" fill="#f5f5f5" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="28" font-weight="700">{esc(listen_label)}</text>
  <text x="24" y="92" fill="#c9a0a6" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">songs logged</text>
  <g transform="translate(250, 42)">
    <text fill="#c9a0a6" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11">LEVEL</text>
    <text y="28" fill="#ffffff" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="26" font-weight="700">{level}</text>
  </g>
  <g transform="translate(360, 42)">
    <text fill="#c9a0a6" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11">DAYS ON</text>
    <text y="28" fill="#ffffff" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="26" font-weight="700">{days}</text>
  </g>
  <text x="250" y="100" fill="#8f5a63" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">live listen counter from music.163.com</text>
</svg>
"""


def main() -> None:
    detail = fetch_detail()
    if detail.get("code") not in (None, 200) and "listenSongs" not in detail:
        raise SystemExit(f"bad netease response: {detail.get('code')}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(detail), encoding="utf-8")
    print(f"wrote {OUT} listenSongs={detail.get('listenSongs')} level={detail.get('level')}")


if __name__ == "__main__":
    main()
