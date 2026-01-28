import requests, os, time, re
from flask import Flask
from threading import Thread
from datetime import datetime, timezone, timedelta

app = Flask('')
@app.route('/')
def home():
    return "BOT ACTIVE"

def keep():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8000)).start()

ROLE_ID = os.environ.get('ROLE_ID')

IMAGES_FRUIT = {
    "Vòi Xanh": "https://docs.google.com/uc?export=download&id=1Avt4uEi68aguVcSS2xKzfAc1BkytBWtT",
    "Vòi Đỏ": "https://docs.google.com/uc?export=download&id=1X5o3QcLVLpLnf22cXWoklsQ5E89or0tz",
    "Bí ngô": "https://docs.google.com/uc?export=download&id=1_8bJk5VFrzpRwLqwFx2wWiv7ue_RFyGI",
    "Dưa hấu": "https://docs.google.com/uc?export=download&id=18d52gH4094L1gCk5zFq_Gm3sUYOrHeAV",
    "Táo đường": "https://docs.google.com/uc?export=download&id=1SUHVCw5D9iNzDLmQe5cc0XR1c1RevDMX",
    "Đậu": "https://docs.google.com/uc?export=download&id=1FyFviSqYIn--Dj5m5I_PaWbCPxOn-HL6",
    "Dừa": "https://docs.google.com/uc?export=download&id=1XRsIeWN0g-wAldeDHk1GqRtENIDPvEfb",
    "Khế": "https://docs.google.com/uc?export=download&id=1_jHGLxg6E0f9iiQEmdKUQFuPHF1pIkep",
    "Nho": "https://docs.google.com/uc?export=download&id=1r5HqB_4Xs1rG0bs0bJPjmFv559frBc6M",
    "Xoài": "https://docs.google.com/uc?export=download&id=1-57KkKrwRN5ftkzZfI5ZTcoVMmdlTcI2",
    "Hạt giống cổ đại": "https://docs.google.com/uc?export=download&id=13y-SR3fD4rsmYafIFl9imLiprednEno7"
}

IMAGES_WEATHER = {
    "Ánh trăng": "https://docs.google.com/uc?export=download&id=1RnCoa7Q9lozV5Hykre3yZttHRgCjvRvt",
    "Bão": "https://docs.google.com/uc?export=download&id=1LtMmLCtQBkSmLTDrtqpE0IGaZnUJLqIG",
    "Cực quang": "https://docs.google.com/uc?export=download&id=13_ZrJufLT36CnjuTf24HWjzJtqGBN_v3",
    "Gió cát": "https://docs.google.com/uc?export=download&id=14dRpd_0VOb9uI7cqYMRXKnYFc2ZLugBF",
    "Gió": "https://docs.google.com/uc?export=download&id=1Q2AgAFs5I5G5Aesb72dI4jUtxQO6FSBl",
    "Mưa": "https://docs.google.com/uc?export=download&id=1ViM9l0nnVxpu3GxbErf0JL3HjvpSAR7W",
    "Sương mù": "https://docs.google.com/uc?export=download&id=1ClBFxlXKevf5pz0hn6i7d_osPFWgI5Up",
    "Sương sớm": "https://docs.google.com/uc?export=download&id=1JSrhfORRipnJyKKtDBKcR-1dGgjQ3tSz",
    "Tuyết": "https://docs.google.com/uc?export=download&id=1DFIjESV2BGMY_aeeVJoi9shvgg-XqrMk",
    "Nắng nóng": "https://docs.google.com/uc?export=download&id=11A-tvciVbgNoZgiILJnYUdnoeM0XujJK",
    "Băng": "https://docs.google.com/uc?export=download&id=18g8AYVKbAUQDMyoOaPbHXmRf5HlNKYY2"
}

WEATHER_MAP = {"Ẩm ướt": "Mưa", "Cát": "Gió cát", "Khí lạnh": "Tuyết", "nhiễm điện": "Bão", "sương sớm": "Sương sớm", "sương mù": "Sương mù", "Ánh trăng": "Ánh trăng", "cực quang": "Cực quang", "Gió": "Gió", "Khô": "Nắng nóng", "Băng": "Băng"}

def clean_extreme(text):
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[`*_~>|]', '', text)
    targets = ["Vòi Xanh", "Vòi Đỏ", "Dưa hấu", "Bí ngô", "Táo đường", "Hạt giống cổ đại"]
    for t in targets:
        text = re.sub(rf"(?i)({t})\s+\1", r"\1", text)
    words = text.split()
    clean_words = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() != words[i-1].lower():
            clean_words.append(word)
    return " ".join(clean_words).strip()

def start_copy():
    token = os.environ.get('TOKEN')
    ch_id = os.environ.get('CHANNEL_ID')
    webhook_url = os.environ.get('WEBHOOK')
    headers = {'Authorization': token}
    msg_cache = [] 
    print("=== BOT DANG QUET TOC DO 2.0S ===") 
    while True:
        try:
            resp = requests.get(f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=5", headers=headers, timeout=10)
            if resp.status_code == 429:
                print("BI RATE LIMIT. NGHI 30S...")
                time.sleep(30)
                continue
            if resp.status_code == 401:
                print("TOKEN LOI!")
                time.sleep(60)
                continue
                
            res = resp.json()
            if isinstance(res, list):
                for msg in reversed(res):
                    msg_id = msg.get('id')
                    if msg_id not in msg_cache:
                        raw = f"{msg.get('content', '')} " + (msg.get('embeds', [{}])[0].get('description', '') if msg.get('embeds') else '')
                        clean = clean_extreme(raw)
                        if not clean:
                            msg_cache.append(msg_id)
                            continue
                        
                        vn_t = datetime.fromisoformat(msg.get('timestamp').replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=7)))
                        t_str = vn_t.strftime('%I:%M %p')
                        
                        is_v = False
                        q = ""
                        if "vòi xanh" in clean.lower():
                            q = "Vòi Xanh"
                            is_v = True
                        elif "vòi đỏ" in clean.lower():
                            q = "Vòi Đỏ"
                            is_v = True
                        else:
                            q = next((f for f in IMAGES_FRUIT if f.lower() in clean.lower()), "")
                        
                        # TAM THOI CHAN NHO
                        if q == "Nho":
                            msg_cache.append(msg_id)
                            continue

                        w = ""
                        for b, tc in sorted(WEATHER_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                            if b.lower() in clean.lower():
                                w = tc
                                break
                        
                        if w:
                            c = 9442302
                            img = IMAGES_WEATHER.get(w, "")
                            name = w
                        elif is_v:
                            c = 16776960
                            img = IMAGES_FRUIT.get(q, "")
                            name = q
                        else:
                            c = 3066993
                            img = IMAGES_FRUIT.get(q, "")
                            name = q if q else "FARM"
                        
                        payload = {
                            "content": f"<@&{ROLE_ID}> {name.upper()} — {t_str}",
                            "embeds": [{"description": clean, "color": c, "thumbnail": {"url": img}}]
                        }
                        requests.post(webhook_url, json=payload, timeout=10)
                        msg_cache.append(msg_id)
                        if len(msg_cache) > 100: msg_cache.pop(0)
                        print(f"DONE: {name}")
            
            # De 2.0s de khong bi Rate Limit tren Koyeb
            time.sleep(2.0)
            
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    keep()
    start_copy()
    
