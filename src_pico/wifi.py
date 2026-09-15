import rp2
import network
import json
import time

rp2.country("SE")

with open("wifi_credentials.json") as file:
    credentrials = json.load(file)

def connect_wifi(waiting_time = 10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentrials.get("WIFI_SSID"), credentrials.get("WIFI_PASSWORD"))

    print(f"{wlan.ifconfig()}")

    while waiting_time > 0:
        if wlan.isconnected():
            print("You are connected to wifi")
            break

        waiting_time -= 1
        print("Trying to connect to wifi...")
        time.sleep(2)

    return wlan.isconnected()