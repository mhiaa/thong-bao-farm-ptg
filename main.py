import requests, os, time, re
from flask import Flask
from threading import Thread
from datetime import datetime, timezone, timedelta

# 1. Cấu hình Server (Koyeb Port 8000)
app = Flask('')
@app.route('/')
def home(): 
    return "BOT FARM - FULL WEATHER VERSION"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()

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

# Danh sách các loại thời tiết cần canh chừng
WEATHER_LIST = ["Bão", "Mưa", "Tuyết", "Nắng", "Gió", "Sương mù", "Cát", "Lốc xoáy", "Hàn hán"]

def clean_extreme(text):
    if not text: return ""
    text = re.sub(r'http\S+', '', text) # Xóa link
    text = re.sub(r'[`*_~>|]', '', text) # Xóa ký tự rác Discord
    
    words = text.split()
    clean_words = []
    for i, word in enumerate(words):
        # Chống lặp từ nhưng KHÔNG xóa nếu đó là từ thời tiết quan trọng
        if i > 0 and word.lower() == words[i-1].lower():
            if not any(w.lower() in word.lower() for w in WEATHER_LIST):
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

    print("Bot đang quét mọi loại thời tiết và trái cây...")

    while True:
        try:
            res = requests.get(
                f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=5", 
                headers=headers, 
                timeout=10
            ).json()

            if res and isinstance(res, list):
                for msg in reversed(res):
                    msg_id = msg.get('id')
                    
                    if msg_id not in msg_cache:
                        raw_text = f"{msg.get('content', '')} " + (msg.get('embeds', [{}])[0].get('description', '') if msg.get('embeds') else '')
                        clean_text = clean_extreme(raw_text)
                        
                        if not clean_text or clean_text == last_sent_content:
                            msg_cache.append(msg_id)
                            continue
                        
                        ts = msg.get('timestamp')
                        vn_time = datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=7)))
                        time_str = vn_time.strftime('%I:%M %p')

                        # 1. Kiểm tra Trái cây
                        qua_gi = next((f for f in IMAGES if f.lower() in clean_text.lower()), "")
                        img_url = IMAGES.get(qua_gi, "")
                        
                        # 2. Kiểm tra mọi loại Thời tiết có trong WEATHER_LIST
                        loai_thoi_tiet = ""
                        for w in WEATHER_LIST:
                            if w.lower() in clean_text.lower():
                                loai_thoi_tiet = w
                                break

                        # TẠO TIÊU ĐỀ THÔNG BÁO NỔI
                        if loai_thoi_tiet:
                            # Nếu có bão hoặc thời tiết, hiện icon cảnh báo và tên thời tiết đó
                            title = f"⚠️ {loai_thoi_tiet} xuất hiện!! - {time_str}"
                        elif qua_gi:
                            title = f"{qua_gi} - {time_str}"
                        else:
                            title = time_str

                        payload = {
                            "content": title,
                            "embeds": [{
                                "description": clean_text,
                                "color": 3066993,
                                "thumbnail": {"url": img_url}
                            }]
                        }
                        
                        requests.post(webhook_url, json=payload, timeout=10)
                        
                        last_sent_content = clean_text 
                        time.sleep(2.5) 
                        msg_cache.append(msg_id)
                        if len(msg_cache) > 20: msg_cache.pop(0)
        except Exception as e:
            time.sleep(5)
        
        time.sleep(2)

if __name__ == "__main__":
    keep_alive()
    start_copy()
    
