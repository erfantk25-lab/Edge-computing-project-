from machine import Pin, PWM, I2C
from dht import DHT11
from time import sleep, sleep_ms
from umqtt.simple import MQTTClient
import json
from wifi import connect_wifi

MQTT_BROKER = "192.168.1.108"
TOPIC_DHT = b"home/pico/dht11"
TOPIC_LUX = b"home/pico/lux"

TEMP_MAX = 30  # C
TEMP_MIN = 5  # C
HUM_MIN = 10  # %
BUZZER_FREQ = 4000

LUX_MIN = 100
LUX_MAX = 30000

ADDR = 0x52     # 0x52 is a Deafult address which APDS-9999 answers on
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000) # Creates a I2C object. 400000 = 400 kHz (highest speed for APDS-9999)

i2c.writeto_mem(ADDR, 0x00, b'\x02') # Measures in ALS mode > only light, not full RGB
sleep_ms(150)

dht_sensor = DHT11(Pin(16))
led = Pin(15, Pin.OUT)
buzzer = PWM(Pin(14))
buzzer.duty_u16(0)

if connect_wifi():
    print("Wifi is connected")


# alarm
def alarm(on):
    led.value(on)
    if on:
        buzzer.freq(BUZZER_FREQ)
        buzzer.duty_u16(32768)  # 50 % duty = max volym
    else:
        buzzer.duty_u16(0)


# will beep for 10 times
def beep(times=10):
    for i in range(times):
        alarm(1)
        sleep(0.1)
        alarm(0)
        sleep(0.1)


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

alarm(0)  # shutdown after loop is done
sleep(1)  # give the sensor time to start

# Read temp/humidity/lux and trigger the alarm if either is out of range.
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        lux = read_lux_apds9999()
        print("Temperature:", temp, "°C  Humidity:", hum, "% Lux:", round(lux, 1))

        # Send temperature, humidity and lux data to MQTT-broker
        dht_payload = json.dumps({"temperature": temp, "humidity": hum})
        lux_payload = json.dumps({"lux": round(lux, 1)})

        try: 
            client.publish(TOPIC_DHT, dht_payload)
            client.publish(TOPIC_LUX, lux_payload)
        except OSError as e:
            print("MQTT publish faild, reconnecting:", e)
            client = connect_mqtt()

        alerts = check_conditions(temp, hum, lux)
        if alerts:
            print("ALERT: Plant conditions unsafe!", alerts)
            beep()

    except OSError:
        print("Could not read the sensor")
        alarm(0)

    sleep(2)