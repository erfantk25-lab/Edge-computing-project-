from machine import Pin, I2C
from dht import DHT11
from time import sleep, sleep_ms
from umqtt.simple import MQTTClient
import json
import time

MQTT_BROKER = "" # TODO: Add the wifi-hotspot IP-address here
TOPIC_DHT = b"home/pico/dht11"
TOPIC_LUX = b"home/pico/lux"

TEMP_MAX = 30  # C
HUM_MAX = 60  # %

ADDR = 0x52
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)

i2c.writeto_mem(ADDR, 0x00, b'\x02')
sleep_ms(150)

dht_sensor = DHT11(Pin(16))
led = Pin(15, Pin.OUT)
buzzer = Pin(14, Pin.OUT)


# alarm
def alarm(on):
    led.value(on)
    buzzer.value(on)


# will beep for 10 times
def beep(times=10):
    for i in range(times):
        alarm(1)
        sleep(0.1)
        alarm(0)
        sleep(0.1)


def read_lux():
    data = i2c.readfrom_mem(ADDR, 0x00, 3)
    raw = data[0] | (data[1] << 8) | (data[2] << 16)
    return raw * 0.180


def connect_mqtt():
    """Connect to the MQTT broker, retrying every 5s until it succeeds."""
    while True:
        try:
            client = MQTTClient(client_id="pico", server=MQTT_BROKER, port=1883)
            client.connect()
            print("Connected to MQTT")
            return client
        except OSError as e:
            print("MQTT connection failed, retrying in 5s:", e)
            sleep(5)

client = connect_mqtt()

alarm(0) # shutdown after loop is done
sleep(1)  # give the sensor time to start

# Read temp/humidity and trigger the alarm if either is out of range.
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        lux = read_lux()
        print("Temperature:", temp, "°C  Humidity:", hum, "% Lux:", round(lux, 1))

        # Send temperature, humidity and lux data to MQTT-broker
        payload = json.dumps({"temperature": temp, "humidity": hum, "lux": round(lux, 1)})
        client.publish(TOPIC, payload)

        if temp > TEMP_MAX or hum > HUM_MAX:
            print("ALERT: Plant conditions unsafe!")
            beep()

    except OSError:
        print("Could not read the sensor")
        alarm(0)

    sleep(2)
