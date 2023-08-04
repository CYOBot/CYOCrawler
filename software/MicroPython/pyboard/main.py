import usocket as socket
import network
from lib.network.microWebSrv import MicroWebSrv
from lib.brain.wireless import *
from lib.brain.display import *

wifi = WiFi()
wifi.connect("<NAME_OF_AP>", "<PASSWORD_OF_AP>")

matrix = Matrix()

if wifi.wlan.isconnected():
    matrix.scroll("INTERNET MODE", speed=0.05, red=50, green=100, blue=80)
    # srv = MicroWebSrv(webPath='/sd/portal/', bindIP=wifi.wlan.ifconfig()[0])

ssid = 'CYOCrawler'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, pm=network.WLAN.PM_PERFORMANCE, txpower=20)

while ap.active() == False:
    pass

print('Connection successful')
print(ap.config('essid'), ap.ifconfig())

from lib.network.microDNSSrv import MicroDNSSrv
if MicroDNSSrv.Create({"portal.cyobot.com": "192.168.4.1"}):
    print("MicroDNSSrv started.")
else :
    print("Error to starts MicroDNSSrv...")

srv = MicroWebSrv(webPath='/sd/portal/')

if not wifi.wlan.isconnected():
    matrix.scroll("AP MODE", speed=0.05, red=50, green=100, blue=80)

srv.Start(threaded=True)
