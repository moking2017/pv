#!/usr/bin/env python3
"""
ppv_to_m3u.py
从 ppv.to API 抓取赛事，生成 m3u 文件
- group-title 按 category 分组
- 流地址：https://ppv2.168.us.kg/stream?uri={uri_name}
- logo 用 poster 字段
"""

import json
import requests
from datetime import datetime, timezone, timedelta

API_URL     = "https://api.ppv.st/api/streams"
OUTPUT_FILE = "ppv_events.m3u"
BASE_STREAM = "https://ppv2.168.us.kg/stream?uri={uri}"
TZ_OFFSET   = timedelta(hours=8)   # UTC → UTC+8

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def fetch_json(url: str) -> dict:
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    r.raise_for_status()
    return r.json()

def ts_to_local(ts: int) -> str:
    """Unix timestamp → UTC+8 时间字符串 HH:MM"""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc) + TZ_OFFSET
    return dt.strftime("%H:%M")

def ts_to_date(ts: int) -> str:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc) + TZ_OFFSET
    return dt.strftime("%Y-%m-%d")

def build_m3u(data: dict) -> str:
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc + TZ_OFFSET

    categories = data.get("streams", [])

    lines = [
        "#EXTM3U",
        f"# Source: ppv.to API",
        f"# UTC+8 | Generated: {now_local.strftime('%Y-%m-%d %H:%M')}",
        f"# Total: 0",   # placeholder, updated below
        "",
    ]

    total = 0

    for cat in categories:
        category = cat.get("category", "Other")
        streams  = cat.get("streams", [])
        if not isinstance(streams, list):
            continue

        for s in streams:
            name     = s.get("name", "Unknown")
            uri      = s.get("uri_name", "")
            poster   = s.get("poster", "")
            starts   = s.get("starts_at", 0)
            ends     = s.get("ends_at", 0)

            if not uri:
                continue

            # 时间标签
            time_str = ts_to_local(starts) if starts else ""
            date_str = ts_to_date(starts)  if starts else ""
            time_tag = f"[{date_str} {time_str}] " if time_str else ""

            stream_url = BASE_STREAM.format(uri=uri)

            extinf = (
                f'#EXTINF:-1 tvg-logo="{poster}" '
                f'group-title="{category}",'
                f'{time_tag}{name}'
            )
            lines.append(extinf)
            lines.append(stream_url)
            lines.append("")
            total += 1

    # 更新 Total 行
    lines[3] = f"# Total: {total}"

    return "\n".join(lines)

def main():
    print("[*] Fetching ppv.to streams ...")
    data = fetch_json(API_URL)

    if not data.get("success"):
        print("[!] API returned success=false, aborting.")
        return

    m3u = build_m3u(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    count = sum(1 for l in m3u.splitlines() if l.startswith("#EXTINF"))
    print(f"[✓] Saved → {OUTPUT_FILE}  ({count} entries)")

if __name__ == "__main__":
    main()
