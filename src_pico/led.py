from machine import Pin
from time import sleep

green_led = Pin(15, Pin.OUT)
yellow_led = Pin(12, Pin.OUT)
red_led = Pin(13, Pin.OUT)


def all_off():
    green_led.value(0)
    yellow_led.value(0)
    red_led.value(0)


def normal():
    all_off()
    green_led.value(1)


def warning():
    all_off()
    yellow_led.value(1)


def error_blink(times=5, delay=0.2):
    all_off()

    for _ in range(times):
        red_led.value(1)
        sleep(delay)
        red_led.value(0)
        sleep(delay)

    red_led.value(1)


def mqtt_error(times=10, delay=0.05):
    all_off()

    for _ in range(times):
        red_led.value(1)
        sleep(delay)
        red_led.value(0)
        sleep(delay)

    red_led.value(1)
