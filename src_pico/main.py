from machine import Pin
from dht import DHT11
from time import sleep

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
        time.sleep(0.1)
        alarm(0)
        time.sleep(0.1)

alarm(0) # shutdown after loop is done
time.sleep(1)  # give the sensor time to start

# Read temp/humidity and trigger the alarm if either is out of range.
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        print("Temp:", temp, "°C  Fukt:", hum, "%")

        if temp > TEMP_MAX or hum > HUM_MAX:
            print("LARM!! VÄXTERNA DÖR!!")
            beep()

    except OSError:
        print("Kunde inte läsa sensorn")
        alarm(0)

    time.sleep(2)