import requests, os, time, re
from flask import Flask
from threading import Thread
from datetime import datetime, timezone, timedelta

# 1. Cấu hình Server để chạy trên Koyeb (Port 8000)
app = Flask('')
@app.route('/')
def home(): 
    return "BOT FARM - FINAL VERSION IS RUNNING"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Danh sách hình ảnh trái cây (Direct Link Drive)
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

# 3. Hàm xử lý: Xóa link gây nền xám và chống lặp từ
def clean_extreme(text):
    if not text: return ""
    # Xóa toàn bộ URL ẩn để Discord không hiện khung nền xám
    text = re.sub(r'http\S+', '', text)
    # Xóa các ký tự đặc biệt của Discord
    text = re.sub(r'[`*_~>|]', '', text)
    # Chống lặp từ (Ví dụ: "Nho Nho" -> "Nho")
    words = text.split()
    clean_words = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() != words[i-1].lower():
            clean_words.append(word)
    return " ".join(clean_words).strip()

def start_copy():
    # Lấy thông tin từ Environment Variables trên Koyeb
    token = os.environ.get('TOKEN')
    channel_id = os.environ.get('CHANNEL_ID')
    webhook_url = os.environ.get('WEBHOOK')
    
    headers = {'Authorization': token}
    msg_cache = [] # Lưu ID tin nhắn để tránh trùng lặp

    print("Bot đang bắt đầu quét tin nhắn...")

    while True:
        try:
            # Lấy 5 tin nhắn mới nhất
            res = requests.get(
                f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=5", 
                headers=headers, 
                timeout=10
            ).json()

            if res and isinstance(res, list):
                for msg in reversed(res):
                    msg_id = msg.get('id')
                    
                    if msg_id not in msg_cache:
                        # Gom nội dung từ cả tin nhắn text và Embed của server gốc
                        raw_text = f"{msg.get('content', '')} " + (msg.get('embeds', [{}])[0].get('description', '') if msg.get('embeds') else '')
                        clean_text = clean_extreme(raw_text)
                        
                        if not clean_text: continue
                        
                        # Xử lý giờ Việt Nam
                        ts = msg.get('timestamp')
                        vn_time = datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=7)))
                        time_str = vn_time.strftime('%I:%M %p')

                        # Xác định loại trái cây để lấy ảnh và tạo Tiêu đề thông báo nổi
                        qua_gi = next((f for f in IMAGES if f.lower() in clean_text.lower()), "")
                        img_url = IMAGES.get(qua_gi, "")
                        
                        # Tiêu đề hiển thị trên thanh thông báo điện thoại
                        if qua_gi:
                            title = f"{qua_gi} - {time_str}"
                        elif any(x in clean_text for x in ["Tuyết", "Mưa", "Nắng"]):
                            title = f"Thời tiết - {time_str}"
                        else:
                            title = time_str

                        # Gửi qua Webhook với giao diện Embed màu xanh lá, thumbnail bên phải
                        payload = {
                            "content": title, # Nội dung này sẽ hiện trên thông báo nổi
                            "embeds": [{
                                "description": clean_text,
                                "color": 3066993, # Màu xanh lá
                                "thumbnail": {"url": img_url}
                            }]
                        }
                        
                        requests.post(webhook_url, json=payload, timeout=10)
                        
                        # Quan trọng: Nghỉ 2.5s để điện thoại hiện nhiều thông báo tách biệt
                        time.sleep(2.5)
                        
                        msg_cache.append(msg_id)
                        if len(msg_cache) > 20: msg_cache.pop(0)
        except Exception as e:
            print(f"Lỗi: {e}")
            time.sleep(5)
        
        time.sleep(2) # Đợi trước khi quét đợt tiếp theo

if __name__ == "__main__":
    keep_alive() # Chạy web server để Koyeb không tắt bot
    start_copy() # Chạy trình copy tin nhắn
