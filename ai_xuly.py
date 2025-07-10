from flask import Flask
import threading
import os
import paho.mqtt.client as mqtt
import time
import requests

# -------- Flask giữ app sống trên Render --------
app = Flask(__name__)

@app.route("/")
def index():
    return "MQTT AI app is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render sẽ tự gán PORT, không để số cố định
    app.run(host="0.0.0.0", port=port)

# ---------- MQTT ----------
def on_connect(client, userdata, flags, rc):
    print("✅ Đã kết nối MQTT")
    # KHÔNG cần subscribe ph/ec nữa
    # client.subscribe("ph")
    # client.subscribe("ec")

def run_mqtt():
    client = mqtt.Client()
    client.username_pw_set("Hieu12345", "Hieu12345")
    client.tls_set()
    client.on_connect = on_connect
    client.connect("0c64bc40bce34474a94c9709a84d047a.s1.eu.hivemq.cloud", 8883)
    client.loop_start()

    # --- Lấy EC, pH từ ThingSpeak định kỳ ---
    THINGSPEAK_URL = "https://api.thingspeak.com/channels/3006092/feeds.json?api_key=6FLQLSHLR9UVUG0N&results=1"

    while True:
        try:
            resp = requests.get(THINGSPEAK_URL, timeout=10)
            feeds = resp.json().get("feeds", [])
            if feeds:
                newest = feeds[0]
                ph = newest.get("field1")
                ec = newest.get("field2")
                try:
                    ph = float(ph)
                    ec = float(ec)
                except:
                    print("Lỗi chuyển đổi pH/EC:", ph, ec)
                    time.sleep(15)
                    continue

                goi_y = ""
                # Gợi ý pH
                if ph < 5.5:
                    goi_y += "pH thấp → Bón vôi. "
                elif ph > 7.5:
                    goi_y += "pH cao → Thêm lưu huỳnh. "
                else:
                    goi_y += "pH ổn. "

                # Gợi ý EC
                if ec > 4:
                    goi_y += "EC cao → Xả mặn."
                elif ec < 1:
                    goi_y += "EC thấp → Bón phân NPK tổng hợp hoặc phân hữu cơ để tăng dinh dưỡng."
                else:
                    goi_y += "EC ổn."

                print(f"📩 Gợi ý gửi ESP32: {goi_y}")
                client.publish("goiy", goi_y)
            else:
                print("Không lấy được dữ liệu ThingSpeak")
        except Exception as e:
            print("Lỗi khi lấy ThingSpeak hoặc gửi MQTT:", e)
        time.sleep(15)  # Lặp lại mỗi 15 giây, có thể chỉnh nhanh/chậm tùy ý

if __name__ == "__main__":
    # Chạy Flask ở thread nền để Render luôn nhận diện app "alive"
    t_web = threading.Thread(target=run_flask)
    t_web.daemon = True
    t_web.start()
    # Chạy AI gợi ý dựa vào dữ liệu ThingSpeak
    run_mqtt()
