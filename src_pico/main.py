from machine import Pin
import dht
import time

TEMP_MAX = 20   # C
HUM_MAX = 10    # %

sensor = dht.DHT11(Pin(16))
led = Pin(15, Pin.OUT)
buzzer = Pin(14, Pin.OUT)

# alarm
def alarm(on):
    led.value(on)
    buzzer.value(on)

# går 10 gånger om alarmet går igång.
def beep(times=10):
    for i in range(times):
        alarm(1)
        time.sleep(0.1)
        alarm(0)
        time.sleep(0.1)

alarm(0) # stänger av efter loppen har gått och alarmet är av
time.sleep(1)  # ge sensorn tid att starta


while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print("Temp:", temp, "°C  Fukt:", hum, "%")

        if temp > TEMP_MAX or hum > HUM_MAX:
            print("LARM!! VÄXTERNA DÖR!!")
            beep()

    except OSError:
        print("Kunde inte läsa sensorn")
        alarm(0)

    time.sleep(2)