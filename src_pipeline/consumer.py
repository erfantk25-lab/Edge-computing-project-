```python
import json
import os
import time
import traceback

import paho.mqtt.client as mqtt
import requests

from utils.connect_postgres import query_db


TOPIC_DHT11 = "home/pico/dht11"
TOPIC_LUX = "home/pico/lux"

WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

latest = {
    "temperature": None,
    "humidity": None,
    "lux": None,
}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to broker", flush=True)
        client.subscribe(TOPIC_DHT11, qos=1)
        client.subscribe(TOPIC_LUX, qos=1)
    else:
        print("Connection failed:", reason_code, flush=True)


def notify_discord(alerts):
    if not WEBHOOK or not alerts:
        return

    text = (
        "**Warning!**\n\n"
        f"Temp: {latest['temperature']} °C"
        f" | Humidity: {latest['humidity']} %"
        f" | Light: {latest['lux']} lux"
        "\n\nPlease check on the plants!"
    )

    try:
        requests.post(
            WEBHOOK,
            json={"content": text},
            timeout=5,
        )
    except requests.RequestException as e:
        print(f"Discord message failed: {e}", flush=True)


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        if message.topic == TOPIC_DHT11:
            temperature = float(data["temperature"])
            humidity = float(data["humidity"])

            latest["temperature"] = temperature
            latest["humidity"] = humidity

        elif message.topic == TOPIC_LUX:
            lux = float(data["lux"])

            latest["lux"] = lux

        else:
            print(f"Unknown topic: {message.topic}", flush=True)
            return

        query_db(
            """
            INSERT INTO sensor_readings
                (time, temperature, humidity, lux)
            VALUES (NOW(), %s, %s, %s)
            """,
            (
                latest["temperature"],
                latest["humidity"],
                latest["lux"],
            ),
        )

        notify_discord(data.get("alerts", []))

        print(
            f"Temperature: {latest['temperature']}, "
            f"Humidity: {latest['humidity']}, "
            f"Lux: {latest['lux']}",
            flush=True,
        )

    except Exception as e:
        print(
            f"Error processing message on topic {message.topic}:",
            flush=True,
        )

        try:
            print(
                f"Raw payload: {message.payload.decode()}",
                flush=True,
            )
        except Exception:
            print(
                f"Raw payload (bytes): {message.payload}",
                flush=True,
            )

        print(f"Exception: {e}", flush=True)
        traceback.print_exc()


if __name__ == "__main__":
    # Wait for DB to be ready
    db_ready = False

    while not db_ready:
        try:
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

            query_db(
                """
                ALTER TABLE sensor_readings
                ADD COLUMN IF NOT EXISTS lux DOUBLE PRECISION
                """
            )

            db_ready = True
            print("Database is ready and initialized.", flush=True)

        except Exception as e:
            print(
                f"Waiting for database to start... ({e})",
                flush=True,
            )
            time.sleep(2)

    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    mqtt_user = os.getenv("MQTT_USER")
    mqtt_password = os.getenv("MQTT_PASSWORD")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if mqtt_user and mqtt_password:
        client.username_pw_set(
            mqtt_user,
            mqtt_password,
        )

    client.on_connect = on_connect
    client.on_message = on_message

    # Wait for MQTT to be ready
    mqtt_ready = False

    while not mqtt_ready:
        try:
            client.connect(mqtt_host, 1883)
            mqtt_ready = True
            print(
                f"Connected to MQTT broker at {mqtt_host}.",
                flush=True,
            )
        except Exception as e:
            print(
                f"Waiting for MQTT broker to start... ({e})",
                flush=True,
            )
            time.sleep(2)

    client.loop_forever()
```

