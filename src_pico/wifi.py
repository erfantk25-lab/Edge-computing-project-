import rp2
import network
import json
import time

rp2.country("SE")

with open("wifi_credentials.json") as file:
    credentrials = json.load(file)

def connect_wifi(waiting_time = 10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    wlan.connect(credentrials.get("WIFI_SSID"), credentrials.get("WIFI_PASSWORD"))

    print(f"{wlan.ifconfig()}")

    while waiting_time > 0:
      if wlan.isconnected():
        print("Ansluten:", wlan.ifconfig())
        break
      print("status:", wlan.status())
      waiting_time -= 1
      time.sleep(2)

    return wlan.isconnected()