import requests, os, time, re
from flask import Flask
from threading import Thread
from datetime import datetime, timezone, timedelta

# 1. Cấu hình Server duy trì trên Koyeb
app = Flask('')
@app.route('/')
def home(): return "BOT FARM - FINAL CLEAN VERSION"
def keep(): Thread(target=lambda: app.run(host='0.0.0.0', port=8000)).start()

# 2. Danh sách hình ảnh trái cây
IMAGES = {
    "Bí ngô": "https://docs.google.com/uc?export=download&id=1_8bJk5VFrzpRwLqwFx2wWiv7ue_RFyGI",
    "Đậu": "https://docs.google.com/uc?export=download&id=1FyFviSqYIn--Dj5m5I_PaWbCPxOn-HL6",
    "Dưa hấu": "https://docs.google.com/uc?export=download&id=18d52gH4094L1gCk5zFq_Gm3sUYOrHeAV",
    "Dừa": "https://docs.google.com/uc?export=download&id=1XRsIeWN0g-wAldeDHk1GqRtENIDPvEfb",
    "Khế": "https://docs.google.com/uc?export=download&id=1_jHGLxg6E0f9iiQEmdKUQFuPHF1pIkep",
    "Nho": "https://docs.google.com/uc?export=download&id=1r5HqB_4Xs1rG0bs0bJPjmFv559frBc6M",
    "Táo đường": "https://docs.google.com/uc?export=download&id=1SUHVCw5D9iNzDLmQe5cc0XR1c1RevDMX",
    "Xoài": "https://docs.google.com/uc?export=download&id=1-57KkKrwRN5ftkzZfI5ZTcoVMmdlTcI2"
}

# 3. Bản đồ Thời tiết - Biến thể chuẩn (Đã xóa ⚠️)
WEATHER_MAP = {
    "Ẩm ướt": "Mưa/Sương mù",
    "Cát": "Gió cát",
    "Khí lạnh": "Tuyết",
    "nhiễm điện": "Bão",
    "sương": "Sương sớm",
    "Ánh trăng": "Ánh trăng",
    "cực quang": "Cực quang",
    "Gió": "Gió",
    "Khô": "Nắng nóng",
    "Nắng Nóng": "Nắng nóng"
}

def clean_extreme(text):
    if not text: return ""
    # Xóa link để tránh nền xám
    text = re.sub(r'http\S+', '', text)
    # FIX LỖI TRIỆT ĐỂ: Xóa sạch các mã @role, emote, mã ID lằng nhằng dạng <@...> hoặc <:..:>
    text = re.sub(r'<[^>]+>', '', text)
    # Xóa ký tự rác Discord
    text = re.sub(r'[`*_~>|]', '', text)
    
    words = text.split()
    clean_words = []
    for i, word in enumerate(words):
        # Chống lặp từ nhưng giữ lại từ thời tiết
        if i > 0 and word.lower() == words[i-1].lower():
            if not any(w.lower() in word.lower() for w in WEATHER_MAP):
                continue
        clean_words.append(word)
    return " ".join(clean_words).strip()

def start_copy():
    token = os.environ.get('TOKEN')
    channel_id = os.environ.get('CHANNEL_ID')
    webhook_url = os.environ.get('WEBHOOK')
    headers = {'Authorization': token}
    msg_cache = [] 
    last_sent_content = ""

    while True:
        try:
            res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=5", headers=headers, timeout=10).json()
            if res and isinstance(res, list):
                for msg in reversed(res):
                    msg_id = msg.get('id')
                    if msg_id not in msg_cache:
                        # Gom nội dung
                        raw_text = f"{msg.get('content', '')} " + (msg.get('embeds', [{}])[0].get('description', '') if msg.get('embeds') else '')
                        clean_text = clean_extreme(raw_text)
                        
                        # Chống trùng lặp tin nhắn
                        if not clean_text or clean_text == last_sent_content:
                            msg_cache.append(msg_id)
                            continue
                        
                        # Giờ Việt Nam
                        ts = msg.get('timestamp')
                        vn_time = datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=7)))
                        time_str = vn_time.strftime('%I:%M %p')

                        # Nhận diện trái cây
                        qua_gi = next((f for f in IMAGES if f.lower() in clean_text.lower()), "")
                        
                        # Nhận diện thời tiết/biến thể
                        ten_thoi_tiet = ""
                        for bien_the, thoi_tiet_chinh in WEATHER_MAP.items():
                            if bien_the.lower() in clean_text.lower():
                                ten_thoi_tiet = thoi_tiet_chinh
                                break

                        # TẠO TIÊU ĐỀ (Sạch sẽ, không icon)
                        if ten_thoi_tiet:
                            title = f"{ten_thoi_tiet} - {time_str}"
                        elif qua_gi:
                            title = f"{qua_gi} - {time_str}"
                        else:
                            title = time_str

                        # Gửi Webhook
                        payload = {
                            "content": title,
                            "embeds": [{
                                "description": clean_text,
                                "color": 3066993,
                                "thumbnail": {"url": IMAGES.get(qua_gi, "")}
                            }]
                        }
                        requests.post(webhook_url, json=payload, timeout=10)
                        
                        last_sent_content = clean_text
                        time.sleep(2.5)
                        msg_cache.append(msg_id)
                        if len(msg_cache) > 20: msg_cache.pop(0)
        except: time.sleep(5)
        time.sleep(2)

if __name__ == "__main__":
    keep()
    start_copy()
    
