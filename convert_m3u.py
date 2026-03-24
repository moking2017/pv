#!/usr/bin/env python3
"""
convert_m3u.py
把 playtorrio.m3u 里的 cdn-live.tv player URL 替换成带 EXTVLCOPT 的真实流地址
"""

import re
import urllib.request
from urllib.parse import urlparse, parse_qs

SOURCE_URL = "https://raw.githubusercontent.com/moking2017/pv/refs/heads/main/playtorrio.m3u"
OUTPUT_FILE = "playtorrio_converted.m3u"

BASE_STREAM = "http://cdnlivetv.168.us.kg/live/{code}/{slug}"
CDN_PLAYER_PATTERN = re.compile(
    r"https://cdn-live\.tv/api/v1/channels/player/\?(.+)"
)

def name_to_slug(name: str) -> str:
    """'tnt+sports+2'  →  'tnt-sports-2'"""
    return name.replace("+", "-").replace(" ", "-").lower()

def build_vlcopt_block(name_raw: str, code: str, player_url: str) -> str:
    slug = name_to_slug(name_raw)
    stream_url = BASE_STREAM.format(code=code, slug=slug)
    return (
        f"#EXTVLCOPT:http-referrer={player_url}\n"
        f"#EXTVLCOPT:http-origin=https://cdn-live.tv\n"
        f"#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36\n"
        f"{stream_url}"
    )

def convert(content: str) -> str:
    lines = content.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测是否是 cdn-live player URL
        m = CDN_PLAYER_PATTERN.match(line.strip())
        if m:
            qs = parse_qs(m.group(1))
            name_raw = qs.get("name", ["unknown"])[0]
            code = qs.get("code", ["xx"])[0]
            player_url = line.strip()
            out.append(build_vlcopt_block(name_raw, code, player_url))
        else:
            out.append(line)

        i += 1

    return "\n".join(out)

def main():
    print(f"[*] Fetching: {SOURCE_URL}")
    with urllib.request.urlopen(SOURCE_URL) as resp:
        content = resp.read().decode("utf-8")

    print(f"[*] Converting {len(content.splitlines())} lines ...")
    converted = convert(content)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(converted)

    print(f"[✓] Saved → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
