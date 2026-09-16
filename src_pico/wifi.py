import rp2
import network
import json
from time import sleep

rp2.country("SE")

with open("wifi_credentials.json") as file:
    credentials = json.load(file)

def connect_wifi(waiting_time = 10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    sleep(1)
    wlan.active(True)
    wlan.connect(credentials.get("WIFI_SSID"), credentials.get("WIFI_PASSWORD"))

    print(f"{wlan.ifconfig()}")

    while waiting_time > 0:
      if wlan.isconnected():
        print("Connected:", wlan.ifconfig())
        break
      print("status:", wlan.status())
      waiting_time -= 1
      sleep(2)

    return wlan.isconnected()