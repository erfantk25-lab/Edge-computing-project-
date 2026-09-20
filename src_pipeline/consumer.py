import paho.mqtt.client as mqtt
import json
from utils.connect_postgres import query_db


def on_message(client, userdata, message):
    payload = message.payload.decode()
    data = json.loads(payload)

    temperature = float(data["temperature"])
    humidity = float(data["humidity"])

    # TODO: Add light sensor data when the light sensor is implemented.

    query_db(
        """
        INSERT INTO sensor_readings
            (time, temperature, humidity)
        VALUES (NOW(), %s, %s)
        """,
        (temperature, humidity),
    )

    print("Temperature:", temperature)
    print("Humidity:", humidity)


if __name__ == "__main__":
    import os
    
    import time
    
    # Simple retry loop to wait for TimescaleDB to be ready (critical for ACI where all containers start at once)
    max_retries = 10
    for attempt in range(max_retries):
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
            print("Successfully connected to TimescaleDB and verified table.")
            break
        except Exception as e:
            print(f"Waiting for TimescaleDB... (Attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(5)
    else:
        print("Failed to connect to TimescaleDB after multiple attempts. Exiting.")
        exit(1)

    client = mqtt.Client()
    
    # Configure authentication if credentials are provided in the environment
    mqtt_user = os.getenv("MQTT_USER")
    mqtt_password = os.getenv("MQTT_PASSWORD")
    if mqtt_user and mqtt_password:
        client.username_pw_set(mqtt_user, mqtt_password)

    # Use environment variable for the MQTT host, defaulting to localhost (used in ACI)
    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    
    for attempt in range(max_retries):
        try:
            client.connect(mqtt_host, 1883)
            print(f"Successfully connected to MQTT broker at {mqtt_host}.")
            break
        except Exception as e:
            print(f"Waiting for Mosquitto... (Attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(5)
    else:
        print("Failed to connect to Mosquitto after multiple attempts. Exiting.")
        exit(1)

    client.subscribe("home/pico/dht11")

    client.on_message = on_message

    client.loop_forever()
