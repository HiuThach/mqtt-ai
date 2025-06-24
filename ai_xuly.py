# ai_xuly.py
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("✅ Đã kết nối MQTT")
    client.subscribe("esp32/ph")
    client.subscribe("esp32/ec")
    client.subscribe("esp32/temp")

ph = 0
ec = 0
temp = 0

def on_message(client, userdata, msg):
    global ph, ec, temp
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "esp32/ph":
        ph = float(payload)
    elif topic == "esp32/ec":
        ec = float(payload)
    elif topic == "esp32/temp":
        temp = float(payload)

    if ph and ec:
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
        client.publish("esp32/goiy", goi_y)

client = mqtt.Client()
client.username_pw_set("Hieu12345", "Hieu12345")
client.on_connect = on_connect
client.on_message = on_message
client.connect("43f9541e13ef4c49ab177e4f8263c375.s1.eu.hivemq.cloud", 8883)

client.loop_forever()
