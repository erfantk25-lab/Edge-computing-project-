from machine import Pin
from dht import DHT11
from time import sleep
from umqtt.robust import MQTTClient
import json

MQTT_BROKER = "" # TODO: Add the wifi-hotspot IP-address here
TOPIC = b"home/pico/dht11"

TEMP_MAX = 20   # C
HUM_MAX = 10    # %

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
        print("Temp:", temp, "°C  Fukt:", hum, "%")

        # Send temperature and humidity data to MQTT-broker
        payload = json.dumps({"temperature": temp, "humidity": hum})
        client.publish(TOPIC, payload)

        if temp > TEMP_MAX or hum > HUM_MAX:
            print("LARM!! VÄXTERNA DÖR!!")
            beep()

    except OSError:
        print("Kunde inte läsa sensorn")
        alarm(0)

    sleep(2)