import paho.mqtt.client as mqtt
import json
import os
import logging
from utils.connect_postgres import query_db

os.makedirs("logs", exist_ok=True)  # Creates logs/ if it doesn´t exists

logging.basicConfig(    # Common log-function för smaller projects
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

def on_message(client, userdata, message):
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

    print("Temperature:", temperature)
    print("Humidity:", humidity)


if __name__ == "__main__":
    query_db(
        """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            time TIMESTAMPTZ NOT NULL,
            temperature DOUBLE PRECISION,
            humidity DOUBLE PRECISION
        )
        """
    )

    client = mqtt.Client()

    client.connect("mosquitto", 1883)

    client.subscribe("home/pico/dht11")

    client.on_message = on_message

    client.loop_forever()
