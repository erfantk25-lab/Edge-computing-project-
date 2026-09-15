import rp2
import network
import json
import time

rp2.country("SE")

with open("wifi_credentials.json") as file:
    credentials = json.load(file)


def connect_wifi(waiting_time=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.get("WIFI_SSID"), credentials.get("WIFI_PASSWORD"))

    while waiting_time > 0:
        if wlan.isconnected() and wlan.ifconfig()[0] != "0.0.0.0":
            print(f"Connected to Wi-Fi! IP: {wlan.ifconfig()[0]}")
            print(f"Full network details: {wlan.ifconfig()}")
            return True

        waiting_time -= 1
        print("Trying to connect to wifi...")
        time.sleep(2)

    print("Failed to connect or obtain an IP address.")
    return False