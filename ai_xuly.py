from flask import Flask
import threading
import os
import paho.mqtt.client as mqtt

# -------- Flask giữ app sống trên Render --------
app = Flask(__name__)

@app.route("/")
def index():
    return "MQTT AI app is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render sẽ tự gán PORT, không để số cố định
    app.run(host="0.0.0.0", port=port)

# ---------- MQTT phần dưới y như bạn muốn ----------
def on_connect(client, userdata, flags, rc):
    print("✅ Đã kết nối MQTT")
    client.subscribe("ph")
    client.subscribe("ec")

ph = None
ec = None

def on_message(client, userdata, msg):
    global ph, ec
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "ph":
        try:
            ph = float(payload)
        except:
            print("Lỗi nhận giá trị pH:", payload)
    elif topic == "ec":
        try:
            ec = float(payload)
        except:
            print("Lỗi nhận giá trị EC:", payload)

    if (ph is not None) and (ec is not None):
        goi_y = ""
        if ph < 5.5:
            goi_y += "pH thấp → Bón vôi. "
        elif ph > 7.5:
            goi_y += "pH cao → Thêm lưu huỳnh. "
        else:
            goi_y += "pH ổn. "

        if ec > 4:
            goi_y += "EC cao → Xả mặn."
        elif ec < 1:
            goi_y += "EC thấp → Bón phân."

        print(f"📩 Gợi ý gửi ESP32: {goi_y}")
        client.publish("goiy", goi_y)
        ph = None
        ec = None

def run_mqtt():
    client = mqtt.Client()
    client.username_pw_set("Hieu12345", "Hieu12345")
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("0c64bc40bce34474a94c9709a84d047a.s1.eu.hivemq.cloud", 8883)
    client.loop_forever()

if __name__ == "__main__":
    # Chạy Flask ở thread nền để Render luôn nhận diện app "alive"
    t_web = threading.Thread(target=run_flask)
    t_web.daemon = True
    t_web.start()
    # Chạy chính MQTT AI
    run_mqtt()
