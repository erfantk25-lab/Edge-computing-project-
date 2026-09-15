import rp2
import network
import json
import time

rp2.country("SE")

with open("wifi_credentials.json") as file:
<<<<<<< HEAD
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
=======
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
>>>>>>> d860b80dc3619d96c1bd93ef89ed47eab99fc72f

        waiting_time -= 1
        print("Trying to connect to wifi...")
        time.sleep(2)

<<<<<<< HEAD
    print("Failed to connect or obtain an IP address.")
    return False
=======
    return wlan.isconnected()
>>>>>>> d860b80dc3619d96c1bd93ef89ed47eab99fc72f
