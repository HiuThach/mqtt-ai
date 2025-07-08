import paho.mqtt.client as mqtt

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

    # Khi đã nhận đủ giá trị ph và ec thì xử lý gợi ý
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
        ph = None  # Reset để nhận lần mới
        ec = None

client = mqtt.Client()
client.username_pw_set("Hieu12345", "Hieu12345")
client.tls_set()  # Enable TLS cho cổng 8883
client.on_connect = on_connect
client.on_message = on_message
client.connect("940bb465734c4cb091dcf59c3a066cb6.s1.eu.hivemq.cloud", 8883)

client.loop_forever()
