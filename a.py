import requests
from datetime import datetime

API_URL = "https://api.ppv.st/api/streams"
OUTPUT = "PPV_IFRAME.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_data():
    try:
        r = requests.get(API_URL, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print("API失败:", r.status_code)
            return None
        return r.json()
    except Exception as e:
        print("请求异常:", e)
        return None

def build_m3u(data):
    lines = ["#EXTM3U"]
    total = 0

    for cat in data.get("streams", []):
        category = cat.get("category", "PPV")

        for s in cat.get("streams", []):
            name = s.get("name", "Unnamed")
            iframe = s.get("iframe")

            if not iframe:
                continue

            total += 1

            lines.append(
                f'#EXTINF:-1 group-title="{category}",{name}'
            )
            lines.append(iframe)

    print(f"总频道: {total}")
    return "\n".join(lines)

def main():
    print("PPV IFRAME M3U 生成")
    print(datetime.now())

    data = get_data()
    if not data:
        print("获取失败")
        return

    m3u = build_m3u(data)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(m3u)

    print("已保存:", OUTPUT)

if __name__ == "__main__":
    main()
