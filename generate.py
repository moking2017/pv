import requests
from datetime import datetime, timedelta

MAX_CHANNELS = 16

def format_time(dt):
    dt = dt + timedelta(hours=8)  # SG时间
    return dt.strftime("%Y%m%dT%H%M%S +0800")

url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
res = requests.get(url)
games = res.json()["scoreboard"]["games"]

# 按时间排序（建议）
games.sort(key=lambda x: x["gameTimeUTC"])

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'

# ===== 频道 =====
for i in range(1, MAX_CHANNELS + 1):
    xml += f'''
  <channel id="NBA{i}">
    <display-name>NBA Live {i}</display-name>
  </channel>'''

# ===== 节目 =====
for i in range(MAX_CHANNELS):
    channel_id = f"NBA{i+1}"

    if i < len(games):
        g = games[i]

        start_dt = datetime.fromisoformat(g["gameTimeUTC"].replace("Z", "+00:00"))
        stop_dt = start_dt + timedelta(hours=2, minutes=30)

        start = format_time(start_dt)
        stop = format_time(stop_dt)

        home = g["homeTeam"]["teamName"]
        away = g["awayTeam"]["teamName"]
        status = g["gameStatusText"]

        title = f"{away} vs {home}"
        desc = status
    else:
        # 没比赛的频道
        now = datetime.utcnow()
        start = format_time(now)
        stop = format_time(now + timedelta(hours=3))
        title = "No Game"
        desc = "NBA"

    xml += f'''
  <programme start="{start}" stop="{stop}" channel="{channel_id}">
    <title>{title}</title>
    <desc>{desc}</desc>
  </programme>'''

xml += "\n</tv>"

# 输出文件
with open("nba_epg.xml", "w", encoding="utf-8") as f:
    f.write(xml)

print("✅ nba_epg.xml generated")
