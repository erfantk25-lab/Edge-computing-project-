import paho.mqtt.client as mqtt
import json
import traceback
from utils.connect_postgres import query_db


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        # TODO: Add light sensor data when the light sensor is implemented.
        # light = float(data["light"])

        query_db(
            """
            INSERT INTO sensor_readings
                (time, temperature, humidity)
            VALUES (NOW(), %s, %s)
            """,
            (temperature, humidity),
        )

        print("Temperature:", temperature, flush=True)
        print("Humidity:", humidity, flush=True)
    except Exception as e:
        print(f"Error processing message on topic {message.topic}:", flush=True)
        try:
            print(f"Raw payload: {message.payload.decode()}", flush=True)
        except Exception:
            print(f"Raw payload (bytes): {message.payload}", flush=True)
        print(f"Exception: {e}", flush=True)
        traceback.print_exc()


if __name__ == "__main__":
    import os
    import time
    
    # Wait for DB to be ready
    db_ready = False
    while not db_ready:
        try:
            query_db(
                """
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    time TIMESTAMPTZ NOT NULL,
                    temperature DOUBLE PRECISION,
                    humidity DOUBLE PRECISION
                )
                """
            )
            db_ready = True
            print("Database is ready and initialized.")
        except Exception as e:
            print(f"Waiting for database to start... ({e})")
            time.sleep(2)

    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    mqtt_user = os.getenv("MQTT_USER")
    mqtt_password = os.getenv("MQTT_PASSWORD")
    
    client = mqtt.Client()
    if mqtt_user and mqtt_password:
        client.username_pw_set(mqtt_user, mqtt_password)

    # Wait for MQTT to be ready
    mqtt_ready = False
    while not mqtt_ready:
        try:
            client.connect(mqtt_host, 1883)
            mqtt_ready = True
            print(f"Connected to MQTT broker at {mqtt_host}.")
        except Exception as e:
            print(f"Waiting for MQTT broker to start... ({e})")
            time.sleep(2)

    client.on_message = on_message
    client.subscribe("home/pico/dht11")
    client.loop_forever()
