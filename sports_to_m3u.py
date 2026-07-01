#!/usr/bin/env python3
"""
sports_to_m3u.py
从 cdn-live.tv Sports Events API 抓取赛事，生成带 EXTVLCOPT 的 m3u 文件
- 过滤掉 status=finished 的比赛
- 时间从 UTC 转换为 UTC+8
- 每个频道独立生成一条 m3u 记录
"""

import json
import re
import urllib.request
import urllib.parse
import html
from datetime import datetime, timezone, timedelta

SPORTS_API  = "https://api.cdnlivetv.tv/api/v1/events/sports/?user=cdnlivetv&plan=free"
OUTPUT_FILE = "sports_events.m3u"
BASE_STREAM = "https://cdnlivetv.168.us.kg/play?name={name}&code={code}"
TZ_OFFSET   = timedelta(hours=8)   # UTC → UTC+8

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Referer":  "https://cdnlivetv.tv/",
    "Origin":   "https://cdnlivetv.tv",
    "Accept":   "application/json",
}

# ── 辅助函数 ──────────────────────────────────────────────

def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def utc_to_local(time_str: str) -> str:
    """'22:00'  (UTC)  →  '05:00'  (UTC+8)，跨天自动处理"""
    h, m = map(int, time_str.split(":"))
    total = h * 60 + m + 8 * 60
    return f"{(total // 60) % 24:02d}:{total % 60:02d}"

def name_from_url(url_str: str) -> str:
    url_str = html.unescape(url_str)
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(url_str).query)
    return qs.get("name", [""])[0]

def name_to_slug(name: str) -> str:
    return name.replace("+", "-").replace(" ", "-").lower()

def build_display_name(game: dict) -> str:
    """生成比赛标题：优先 homeTeam vs awayTeam，否则用 event 字段"""
    home = game.get("homeTeam", "").strip()
    away = game.get("awayTeam", "").strip()
    if home and away:
        return f"{home} vs {away}"
    return game.get("event", "Unknown Event").strip()

def build_extinf(time_local: str, sport: str, match_title: str,
                  ch_name: str, ch_code: str, logo: str) -> str:
    label = f"[{time_local}] {sport} - {match_title} - {ch_name} 🌐 {ch_code.upper()}"
    return (
        f'#EXTINF:-1 tvg-logo="{logo}" '
        f'group-title="{sport}",'
        f'{label}'
    )

def build_stream_block(name_raw: str, code: str) -> str:
    return BASE_STREAM.format(
        name=urllib.parse.quote_plus(name_raw),
        code=code.lower()
    )

# ── 主逻辑 ────────────────────────────────────────────────

def build_m3u(data: dict) -> str:
    now_utc = datetime.now(timezone.utc)
    events_data = data.get("cdn-live-tv", {})

    lines = [
        "#EXTM3U",
        f"# Generated from cdn-live.tv Sports API",
        f"# UTC+8 timezone | Generated: {(now_utc + TZ_OFFSET).strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    total_channels = 0
    skipped = 0

    for sport, games in events_data.items():
        if not isinstance(games, list):
            continue
        for game in games:
            status = game.get("status", "")

            # 跳过已结束比赛
            if status == "finished":
                skipped += 1
                continue

            channels = game.get("channels", [])
            if not channels:
                continue  # 没有频道信息，跳过

            time_utc   = game.get("time", "00:00")
            time_local = utc_to_local(time_utc)
            match_title = build_display_name(game)

            # 状态标记
            status_tag = "🔴 LIVE" if status == "live" else "⏳"

            for ch in channels:
                player_url = html.unescape(ch.get("url", ""))
                if not player_url:
                    continue

                name_raw = name_from_url(player_url)
                code = ch.get("channel_code", "xx").lower()
                ch_name = ch.get("channel_name", name_raw)
                logo = ch.get("image", "")

                label = (
                    f"[{time_local}] {status_tag} {sport} - "
                    f"{match_title} - {ch_name} 🌐 {code.upper()}"
                )

                extinf = (
                    f'#EXTINF:-1 tvg-logo="{logo}" '
                    f'group-title="{sport}",'
                    f'{label}'
                )

                lines.append(extinf)
                lines.append(build_stream_block(name_raw, code))
                lines.append("")
                total_channels += 1

    # 更新头部统计
    lines[3] = f"# Total Entries: {total_channels}  |  Skipped (finished): {skipped}"

    return "\n".join(lines)

def main():
    print(f"[*] Fetching sports events ...")
    raw = fetch_json(SPORTS_API)

    sports = raw.get("cdnlivetv", {})
    total_games = sum(len(v) for v in sports.values() if isinstance(v, list))
    sport_keys = [k for k, v in sports.items() if isinstance(v, list)]
    print(f"[*] Sports categories: {sport_keys}")
    print(f"[*] Total games found: {total_games}")

    m3u = build_m3u(raw)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    lines = m3u.splitlines()
    entry_count = sum(1 for l in lines if l.startswith("#EXTINF"))
    print(f"[✓] Saved → {OUTPUT_FILE}  ({entry_count} channel entries)")

if __name__ == "__main__":
    main()
