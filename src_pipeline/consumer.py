import paho.mqtt.client as mqtt
import json
from utils.connect_postgres import query_db

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:    # 0 = succeeded to connect
        print("Connected to broker")
        client.subscribe("home/pico/dht11")
        client.subscribe("home/pico/lux")
    else:
        print("Connection failed:", reason_code)

def on_message(client, userdata, message):
    """
    Handles an incoming MQTT message by decoding JSON. Stores 
    the information in the database, based on its topics. 
    
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

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mosquitto", 1883)
    client.loop_forever()
