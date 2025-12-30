import requests, os, time, re
from flask import Flask
from threading import Thread
from datetime import datetime, timezone, timedelta

# 1. Server Flask duy trì trên Koyeb
app = Flask('')
@app.route('/')
def home(): return "BOT FARM - NO LIMITS VERSION"
def keep(): Thread(target=lambda: app.run(host='0.0.0.0', port=8000)).start()

# 2. Danh sách hình ảnh TRÁI CÂY
IMAGES_FRUIT = {
    "Bí ngô": "https://docs.google.com/uc?export=download&id=1_8bJk5VFrzpRwLqwFx2wWiv7ue_RFyGI",
    "Đậu": "https://docs.google.com/uc?export=download&id=1FyFviSqYIn--Dj5m5I_PaWbCPxOn-HL6",
    "Dưa hấu": "https://docs.google.com/uc?export=download&id=18d52gH4094L1gCk5zFq_Gm3sUYOrHeAV",
    "Dừa": "https://docs.google.com/uc?export=download&id=1XRsIeWN0g-wAldeDHk1GqRtENIDPvEfb",
    "Khế": "https://docs.google.com/uc?export=download&id=1_jHGLxg6E0f9iiQEmdKUQFuPHF1pIkep",
    "Nho": "https://docs.google.com/uc?export=download&id=1r5HqB_4Xs1rG0bs0bJPjmFv559frBc6M",
    "Táo đường": "https://docs.google.com/uc?export=download&id=1SUHVCw5D9iNzDLmQe5cc0XR1c1RevDMX",
    "Xoài": "https://docs.google.com/uc?export=download&id=1-57KkKrwRN5ftkzZfI5ZTcoVMmdlTcI2"
}

# 3. Danh sách hình ảnh THỜI TIẾT
IMAGES_WEATHER = {
    "Ánh trăng": "https://docs.google.com/uc?export=download&id=1RnCoa7Q9lozV5Hykre3yZttHRgCjvRvt",
    "Bão": "https://docs.google.com/uc?export=download&id=1LtMmLCtQBkSmLTDrtqpE0IGaZnUJLqIG",
    "Cực quang": "https://docs.google.com/uc?export=download&id=13_ZrJufLT36CnjuTf24HWjzJtqGBN_v3",
    "Gió cát": "https://docs.google.com/uc?export=download&id=14dRpd_0VOb9uI7cqYMRXKnYFc2ZLugBF",
    "Gió": "https://docs.google.com/uc?export=download&id=1Q2AgAFs5I5G5Aesb72dI4jUtxQO6FSBl",
    "Mưa": "https://docs.google.com/uc?export=download&id=1ViM9l0nnVxpu3GxbErf0JL3HjvpSAR7W",
    "Sương mù": "https://docs.google.com/uc?export=download&id=1ClBFxlXKevf5pz0hn6i7d_osPFWgI5Up",
    "Sương sớm": "https://docs.google.com/uc?export=download&id=11A-tvciVbgNoZgiILJnYUdnoeM0XujJK",
    "Tuyết": "https://docs.google.com/uc?export=download&id=1DFIjESV2BGMY_aeeVJoi9shvgg-XqrMk",
    "Nắng nóng": "https://docs.google.com/uc?export=download&id=1SUHVCw5D9iNzDLmQe5cc0XR1c1RevDMX"
}

WEATHER_MAP = {
    "Ẩm ướt": "Mưa", "Cát": "Gió cát", "Khí lạnh": "Tuyết", "nhiễm điện": "Bão",
    "sương": "Sương sớm", "Ánh trăng": "Ánh trăng", "cực quang": "Cực quang",
    "Gió": "Gió", "Khô": "Nắng nóng", "Sương mù": "Sương mù"
}

def clean_extreme(text):
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[`*_~>|]', '', text)
    words = text.split()
    clean_words = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() != words[i-1].lower():
            if len(clean_words) >= 2:
                phrase_2 = (clean_words[-2] + " " + clean_words[-1]).lower()
                current_phrase = (clean_words[-1] + " " + word).lower()
                if phrase_2 == current_phrase: continue
            clean_words.append(word)
    return " ".join(clean_words).strip()

def start_copy():
    token = os.environ.get('TOKEN')
    channel_id = os.environ.get('CHANNEL_ID')
    webhook_url = os.environ.get('WEBHOOK')
    headers = {'Authorization': token}
    msg_cache = [] 

    while True:
        try:
            res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=5", headers=headers, timeout=10).json()
            if res and isinstance(res, list):
                for msg in reversed(res):
                    msg_id = msg.get('id')
                    # Chỉ chặn nếu chính cái ID tin nhắn đó đã được gửi (tránh gửi 1 tin nhiều lần)
                    if msg_id not in msg_cache:
                        raw_text = f"{msg.get('content', '')} " + (msg.get('embeds', [{}])[0].get('description', '') if msg.get('embeds') else '')
                        clean_text = clean_extreme(raw_text)
                        
                        if not clean_text:
                            msg_cache.append(msg_id)
                            continue
                        
                        vn_time = datetime.fromisoformat(msg.get('timestamp').replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=7)))
                        time_str = vn_time.strftime('%I:%M %p')

                        qua_gi = next((f for f in IMAGES_FRUIT if f.lower() in clean_text.lower()), "")
                        ten_thoi_tiet = ""
                        for bien_the, thoi_tiet_chinh in WEATHER_MAP.items():
                            if bien_the.lower() in clean_text.lower():
                                ten_thoi_tiet = thoi_tiet_chinh
                                break

                        if ten_thoi_tiet:
                            color_code = 9442302
                            img_url = IMAGES_WEATHER.get(ten_thoi_tiet, "")
                            display_name = ten_thoi_tiet
                        else:
                            color_code = 3066993
                            img_url = IMAGES_FRUIT.get(qua_gi, "")
                            display_name = qua_gi if qua_gi else "FARM"

                        clean_title = f"{display_name.upper()} — {time_str}"
                        display_text = clean_text
                        for word in list(IMAGES_FRUIT.keys()) + list(WEATHER_MAP.keys()) + ["xuất hiện", "biến thể", "đang bán"]:
                            display_text = re.sub(f"(?i){word}", f"**{word}**", display_text)

                        payload = {
                            "content": clean_title,
                            "embeds": [{
                                "description": display_text,
                                "color": color_code,
                                "thumbnail": {"url": img_url}
                            }]
                        }
                        requests.post(webhook_url, json=payload, timeout=10)
                        
                        time.sleep(2.5)
                        msg_cache.append(msg_id)
                        if len(msg_cache) > 20: msg_cache.pop(0)
        except: time.sleep(5)
        time.sleep(2)

if __name__ == "__main__":
    keep()
    start_copy()
    
