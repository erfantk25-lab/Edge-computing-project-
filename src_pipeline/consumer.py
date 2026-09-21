import paho.mqtt.client as mqtt
import json
import os
from utils.connect_postgres import query_db
import requests

TOPIC_DHT11 = "home/pico/dht11"
TOPIC_LUX = "home/pico/lux"

WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

latest = {"temperature": None, "humidity": None, "lux": None}

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:    # 0 = succeeded to connect
        print("Connected to broker")
        client.subscribe(TOPIC_DHT11, qos=1) # qos1 = resends message if not received
        client.subscribe(TOPIC_LUX, qos=1)
    else:
        print("Connection failed:", reason_code)    


def notify_discord(alerts):
    if not WEBHOOK or not alerts:
        return

    text = (
        "**Warning!**\n\n"
        + f"Temp: {latest['temperature']} °C"
        + f" | Humidity: {latest['humidity']} %"
        + f" | Light: {latest['lux']} lux"
        + "\n\nPlease check on the plants!"
    )
    try:
        requests.post(WEBHOOK, json={"content": text}, timeout=5)
    except requests.RequestException as e:
        print("Discord message failed:", e)

def on_message(client, userdata, message):
    """Callback by paho-mqtt when a message is received. 
     
    Decodes the JSON payload and saves the values to the database. If the 
    payload's "alerts" list in non-empty, a Discord webhook triggers a notification. 

    Handles topics:
    - home/pico/dht11
    - home/pico/lux

    """
    
    payload = message.payload.decode()
    data = json.loads(payload)

    if message.topic == "home/pico/dht11":
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        query_db(
                """
                INSERT INTO sensor_readings
                    (time, temperature, humidity)
                VALUES (NOW(), %s, %s)
                """,
                (temperature, humidity),
            )
        latest["temperature"] = temperature
        latest["humidity"] = humidity
        notify_discord(data.get("alerts", []))

    elif message.topic == "home/pico/lux":
        lux = float(data["lux"])

        query_db(
            """
            INSERT INTO sensor_readings (time, lux)
            VALUES (NOW(), %s)
            """,
            (lux,),
        )
        print("Lux:", lux)
        latest["lux"] = lux
        notify_discord(data.get("alerts", []))


if __name__ == "__main__":
    query_db(
        """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            time TIMESTAMPTZ NOT NULL,
            temperature DOUBLE PRECISION,
            humidity DOUBLE PRECISION,
            lux DOUBLE PRECISION
        )
        """
    )

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) # newer callback interface
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mosquitto", 1883)
    client.loop_forever()
