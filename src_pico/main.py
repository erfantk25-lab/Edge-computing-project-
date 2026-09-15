from machine import Pin
from dht import DHT11
from time import sleep
from umqtt.simple import MQTTClient
import json
from wifi import connect_wifi

MQTT_BROKER = "172.31.32.1"
TOPIC = b"home/pico/dht11"

TEMP_MAX = 30  # C
HUM_MAX = 60  # %

dht_sensor = DHT11(Pin(16))
led = Pin(15, Pin.OUT)
buzzer = Pin(14, Pin.OUT)

if connect_wifi():
    led.value(1)

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


alarm(0)  # shutdown after loop is done
sleep(1)  # give the sensor time to start

# Read temp/humidity and trigger the alarm if either is out of range.
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        print("Temperature:", temp, "°C  Humidity:", hum, "%")

        if temp > TEMP_MAX or hum > HUM_MAX:
            print("ALERT: Plant conditions unsafe!")
            beep()

    except OSError:
        print("Could not read the sensor")
        alarm(0)

    sleep(2)
