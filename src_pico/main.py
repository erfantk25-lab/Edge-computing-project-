from machine import Pin, PWM, I2C
from dht import DHT11
from time import sleep, sleep_ms
from umqtt.simple import MQTTClient
from wifi import connect_wifi
import json


MQTT_BROKER = "192.168.1.108"

TOPIC_DHT = b"home/pico/dht11"
TOPIC_LUX = b"home/pico/lux"




TEMP_MAX = 30  # °C
TEMP_MIN = 5   # °C
HUM_MIN = 10   # %

LUX_MIN = 100
LUX_MAX = 30000




ADDR = 0x52

i2c = I2C(
    1,
    scl=Pin(3),
    sda=Pin(2),
    freq=400000
)

# Enable ALS mode - measures ambient light
i2c.writeto_mem(ADDR, 0x00, b'\x02')
sleep_ms(150)



# DHT11 sensor
dht_sensor = DHT11(Pin(16))


# LEDs
# Green = normal
# Yellow = warning
# Red = error
green_led = Pin(15, Pin.OUT)
yellow_led = Pin(13, Pin.OUT)
red_led = Pin(12, Pin.OUT)


# Buzzer
buzzer = PWM(Pin(14))
buzzer.duty_u16(0)


# --------------------------------------------------
# LED / BUZZER STATUS
# --------------------------------------------------

# LLM-assisted code:
# LED status logic was generated with help from an LLM
# and then reviewed and adapted to the project hardware.


def all_leds_off():
    """Turn all LEDs off."""
    green_led.value(0)
    yellow_led.value(0)
    red_led.value(0)


def normal_status():
    """
    Normal system status:
    Green LED ON, buzzer OFF.
    """
    all_leds_off()

    green_led.value(1)

    buzzer.duty_u16(0)


def warning_status():
    """
    Warning status:
    Yellow LED ON and buzzer gives a short beep.
    """
    all_leds_off()

    yellow_led.value(1)

    buzzer.freq(4000)
    buzzer.duty_u16(32768)

    sleep(0.5)

    buzzer.duty_u16(0)


def sensor_error():
    """
    Sensor error:
    Red LED blinks.
    Buzzer stays OFF.
    """
    all_leds_off()

    buzzer.duty_u16(0)

    for _ in range(5):
        red_led.value(1)
        sleep(0.2)

        red_led.value(0)
        sleep(0.2)


def mqtt_error():
    """
    MQTT connection problem:
    Red LED blinks quickly.
    Buzzer stays OFF.
    """
    all_leds_off()

    buzzer.duty_u16(0)

    for _ in range(10):
        red_led.value(1)
        sleep(0.05)

        red_led.value(0)
        sleep(0.05)




if not connect_wifi():
    raise RuntimeError("WiFi connection failed")

print("WiFi is connected")




def read_lux_apds9999():
    """Read ambient light (lux) from APDS-9999."""

    # Read 3 bytes from ALS/Green data registers
    data = i2c.readfrom_mem(ADDR, 0x0D, 3)

    # Combine 3 bytes into a 24-bit raw value
    raw = data[0] | (data[1] << 8) | (data[2] << 16)

    # Convert raw value to lux
    return raw * 0.180




def check_conditions(temp, hum, lux):
    """
    Return a list containing sensor values
    that are outside the allowed limits.
    """

    alerts = []

    if temp < TEMP_MIN or temp > TEMP_MAX:
        alerts.append("temperature")

    if hum < HUM_MIN:
        alerts.append("humidity")

    if lux < LUX_MIN or lux > LUX_MAX:
        alerts.append("lux")

    return alerts



def read_lux_apds9999():
    """Read ambient light (lux) from an APDS-9999 sensor"""
    # Read 3 bytes from the ALS/Green data registers (0x0D-0x0F)
    data = i2c.readfrom_mem(ADDR, 0x0D, 3)

    # Combine the 3 bytes into 24-bit raw value:
    raw = data[0] | (data[1] << 8) | (data[2] << 16)

    # Convert to lux using the sensor's scale factor 0.180 lux/count
    return raw * 0.180

def check_conditions(temp, hum, lux):
    """Return a list of readings that are out of range."""
    alerts = []
    if temp < TEMP_MIN or temp > TEMP_MAX:
        alerts.append("temperature")
    if hum < HUM_MIN:
        alerts.append("humidity")
    if lux < LUX_MIN or lux > LUX_MAX:
        alerts.append("lux")
    return alerts


def connect_mqtt():
    """
    Connect to the MQTT broker.
    Retry every 5 seconds if connection fails.
    """

    while True:
        try:
            client = MQTTClient(
                client_id="pico",
                server=MQTT_BROKER,
                port=1883
            )

            client.connect()

            print("Connected to MQTT")

            # MQTT connection is working
            normal_status()

            return client

        except OSError as e:
            print(
                "MQTT connection failed, "
                "retrying in 5s:",
                e
            )

            # Fast red blinking
            mqtt_error()

            sleep(5)



client = connect_mqtt()

# Initial status
normal_status()

sleep(1)




while True:

    try:
        

        dht_sensor.measure()

        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()


       

        lux = read_lux_apds9999()


       

        print(
            "Temperature:",
            temp,
            "°C  Humidity:",
            hum,
            "%  Lux:",
            round(lux, 1)
        )


       

        dht_payload = json.dumps({
            "temperature": temp,
            "humidity": hum
        })

        lux_payload = json.dumps({
            "lux": round(lux, 1)
        })


        

        try:

            client.publish(
                TOPIC_DHT,
                dht_payload
            )

            client.publish(
                TOPIC_LUX,
                lux_payload
            )

            print("Sensor data sent to MQTT")

        except OSError as e:

            print(
                "MQTT publish failed, "
                "reconnecting:",
                e
            )

            # Fast red blinking
            mqtt_error()

            # Reconnect
            client = connect_mqtt()

            continue


        

        alerts = check_conditions(
            temp,
            hum,
            lux
        )


        if alerts:

            print(
                "ALERT: Plant conditions unsafe!",
                alerts
            )

            # Warning:
            # yellow LED + short buzzer
            warning_status()

        else:

            # Normal:
            # green LED
            normal_status()


    except OSError as e:

        print(
            "Could not read sensor:",
            e
        )

        # Sensor error:
        # red LED blinking
        sensor_error()


    sleep(2)
