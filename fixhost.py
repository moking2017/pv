import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/moking2017/pv/refs/heads/main/playtorrio.m3u"
OUTPUT_FILE = "local.m3u8"

OLD_PREFIX = "https://cdn-live.tv/api/v1/channels/player/?"
NEW_PREFIX = "http://192.168.2.139:8383/play?"

def main():
    print("Downloading M3U...")
    r = requests.get(SOURCE_URL, timeout=20)
    r.raise_for_status()

    content = r.text
    new_content = content.replace(OLD_PREFIX, NEW_PREFIX)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Done at:", datetime.now())

if __name__ == "__main__":
    main()
