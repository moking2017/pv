#!/usr/bin/env python3
import requests
from datetime import datetime

# ===== 配置 =====
SOURCE_URL = "https://raw.githubusercontent.com/moking2017/pv/refs/heads/main/playtorrio.m3u"
OUTPUT_FILE = "local.m3u8"

OLD_PREFIX = "https://cdn-live.tv/api/v1/channels/player/"
NEW_PREFIX = "http://192.168.2.139:8383/play"

# ===== 下载 =====
def fetch_m3u():
    print("正在下载 M3U...")
    r = requests.get(SOURCE_URL, timeout=20)
    r.raise_for_status()
    return r.text

# ===== 替换 =====
def rewrite(content):
    print("正在替换域名...")
    return content.replace(OLD_PREFIX, NEW_PREFIX)

# ===== 保存 =====
def save(content):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("保存完成:", OUTPUT_FILE)

if __name__ == "__main__":
    try:
        data = fetch_m3u()
        new_data = rewrite(data)
        save(new_data)
        print("完成时间:", datetime.now())
    except Exception as e:
        print("错误:", e)
