from machine import Pin, PWM, I2C
from dht import DHT11
from time import sleep, sleep_ms
from umqtt.simple import MQTTClient
from wifi import connect_wifi
from led import normal, warning, error_blink, mqtt_error
import json


MQTT_BROKER = "192.168.1.108"

TOPIC_DHT = b"home/pico/dht11"
TOPIC_LUX = b"home/pico/lux"

TEMP_MAX = 30
TEMP_MIN = 5
HUM_MIN = 10

LUX_MIN = 100
LUX_MAX = 30000

ADDR = 0x52

# I2C light sensor
i2c = I2C(
    1,
    scl=Pin(3),
    sda=Pin(2),
    freq=400000
)

# Enable ambient light measurement
i2c.writeto_mem(ADDR, 0x00, b"\x02")
sleep_ms(150)

# DHT11 sensor
dht_sensor = DHT11(Pin(16))

# Buzzer
buzzer = PWM(Pin(14))
buzzer.duty_u16(0)


def buzzer_off():
    buzzer.duty_u16(0)


def warning_beep():
    buzzer.freq(4000)
    buzzer.duty_u16(32768)
    sleep(0.5)
    buzzer_off()


def read_lux_apds9999():
    """Read ambient light in lux from the APDS-9999 sensor."""
    data = i2c.readfrom_mem(ADDR, 0x0D, 3)
    raw = data[0] | (data[1] << 8) | (data[2] << 16)
    return raw * 0.180


def check_conditions(temp, hum, lux):
    """Return a list of sensor readings outside the allowed limits."""
    alerts = []

    if temp < TEMP_MIN or temp > TEMP_MAX:
        alerts.append("temperature")

    if hum < HUM_MIN:
        alerts.append("humidity")

    if lux < LUX_MIN or lux > LUX_MAX:
        alerts.append("lux")

    return alerts


def connect_mqtt():
    """Connect to MQTT and retry every 5 seconds if connection fails."""
    while True:
        try:
            client = MQTTClient(
                client_id="pico",
                server=MQTT_BROKER,
                port=1883
            )
            client.connect()

            print("Connected to MQTT")
            normal()
            buzzer_off()

            return client

        except OSError as e:
            print("MQTT connection failed, retrying in 5s:", e)
            mqtt_error()
            sleep(5)


# Connect to Wi-Fi
if not connect_wifi():
    raise RuntimeError("WiFi connection failed")

print("WiFi is connected")

# Connect to MQTT
client = connect_mqtt()

while True:
    try:
        # Read DHT11
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()

        # Read light sensor
        lux = read_lux_apds9999()

        print(
            "Temperature:",
            temp,
            "°C | Humidity:",
            hum,
            "% | Lux:",
            round(lux, 1)
        )

        # Create MQTT payloads
        dht_payload = json.dumps({
            "temperature": temp,
            "humidity": hum
        })

        lux_payload = json.dumps({
            "lux": round(lux, 1)
        })

        # Publish sensor data
        try:
            client.publish(TOPIC_DHT, dht_payload)
            client.publish(TOPIC_LUX, lux_payload)
            print("Sensor data sent to MQTT")

        except OSError as e:
            print("MQTT publish failed, reconnecting:", e)
            mqtt_error()
            client = connect_mqtt()
            continue

        # Check plant conditions
        alerts = check_conditions(temp, hum, lux)

        if alerts:
            print("ALERT: Plant conditions unsafe:", alerts)
            warning()
            warning_beep()
        else:
            normal()
            buzzer_off()

    except OSError as e:
        print("Could not read sensor:", e)
        buzzer_off()
        error_blink()

    sleep(2)
