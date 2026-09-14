import paho.mqtt.client as mqtt
import json
from utils.connect_postgres import query_db


def on_message(client, userdata, message):
    payload = message.payload.decode()
    data = json.loads(payload)

    temperature = float(data["temperature"])
    humidity = float(data["humidity"])
    light = float(data["light"])

    query_db(
        """
        INSERT INTO sensor_readings
            (time, temperature, humidity, light)
        VALUES (NOW(), %s, %s, %s)
        """,
        (temperature, humidity, light),
    )

    print(temperature, humidity, light)


if __name__ == "__main__":
    query_db(
        """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            time TIMESTAMPTZ NOT NULL,
            temperature DOUBLE PRECISION,
            humidity DOUBLE PRECISION,
            light DOUBLE PRECISION
        )
        """
    )

    client = mqtt.Client()
    client.connect("mosquitto", 1883)

    client.subscribe("home/pico/dht11")

    client.on_message = on_message
    client.loop_forever()
