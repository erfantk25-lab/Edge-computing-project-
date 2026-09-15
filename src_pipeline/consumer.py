<<<<<<< HEAD
import paho.mqtt.client as mqtt
import json
from utils.connect_postgres import query_db


def on_message(client, userdata, message, *args):
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

        print("Temperature:", temperature)
        print("Humidity:", humidity)
    except Exception as err:
        print(f"Failed to process message on {message.topic}: {err}")



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

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    client.connect("mosquitto", 1883)

    client.subscribe("home/pico/dht11")
    print("Successfully connected to Mosquitto and subscribed to home/pico/dht11")


    client.loop_forever()
=======
import paho.mqtt.client as mqtt
import json
from utils.connect_postgres import query_db


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
>>>>>>> d860b80dc3619d96c1bd93ef89ed47eab99fc72f
