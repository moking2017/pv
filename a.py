import requests
from datetime import datetime
import re

API_URL = "https://api.ppv.st/api/streams"

OUTPUT_ORIGINAL = "example.m3u8"
OUTPUT_PUBLIC = "PPV_IFRAME.m3u8"
OUTPUT_LOCAL = "PPV_LOCAL.m3u8"

PUBLIC_BASE = "https://ppv2.168.us.kg/stream?uri="
LOCAL_BASE = "http://192.168.2.139:8090/stream?uri="

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


def get_logo(stream):
    return (
        stream.get("logo")
        or stream.get("poster")
        or stream.get("image")
        or stream.get("thumbnail")
        or ""
    )


def convert_embed(url, base):
    """
    精准提取 /embed/ 后面的真实ID
    适配：
    /eu/embed/mlb/xxx
    /embed/mlb/xxx
    """
    if not url:
        return None

    # 只截取 embed/ 后面的内容
    m = re.search(r'/embed/(.+)', url)
    if m:
        return base + m.group(1)

    return None

def build_all_versions(data):
    original = ["#EXTM3U"]
    public = ["#EXTM3U"]
    local = ["#EXTM3U"]

    total = 0

    for cat in data.get("streams", []):
        category = cat.get("category", "PPV")

        for s in cat.get("streams", []):
            name = s.get("name", "Unnamed")
            iframe = s.get("iframe")
            logo = get_logo(s)

            if not iframe:
                continue

            total += 1

            if logo:
                extinf = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}",{name}'
            else:
                extinf = f'#EXTINF:-1 group-title="{category}",{name}'

            # 原始
            original.append(extinf)
            original.append(iframe)

            # 公网
            public_url = convert_embed(iframe, PUBLIC_BASE)
            if public_url:
                public.append(extinf)
                public.append(public_url)

            # 局域网
            local_url = convert_embed(iframe, LOCAL_BASE)
            if local_url:
                local.append(extinf)
                local.append(local_url)

    print(f"总频道: {total}")
    return (
        "\n".join(original),
        "\n".join(public),
        "\n".join(local),
    )


def main():
    print("PPV 自动生成 3版本")
    print(datetime.now())

    data = get_data()
    if not data:
        print("获取失败")
        return

    original, public, local = build_all_versions(data)

    with open(OUTPUT_ORIGINAL, "w", encoding="utf-8") as f:
        f.write(original)

    with open(OUTPUT_PUBLIC, "w", encoding="utf-8") as f:
        f.write(public)

    with open(OUTPUT_LOCAL, "w", encoding="utf-8") as f:
        f.write(local)

    print("已生成:")
    print(" -", OUTPUT_ORIGINAL)
    print(" -", OUTPUT_PUBLIC)
    print(" -", OUTPUT_LOCAL)


if __name__ == "__main__":
    main()
