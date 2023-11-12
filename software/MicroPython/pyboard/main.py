from lib.crawler.display import *
import time

ring = LEDRing()
ring.reset()
for i in range(12):
    ring.set_manual(i, (0, 100, 0))
    time.sleep(0.05)
ring.reset()

import network
from lib.network.microWebSrv import MicroWebSrv
from lib.brain.wireless import *
from lib.brain.display import *
import json
import webrepl

matrix = Matrix()
wifi = WiFi()

try:
    file = open("/sd/lib/brain/config.json").read()
    content = json.loads(file)
    wifi.connect(content["ssid"], content["password"])
except:
    pass

def getWiFiAPList():
    def signal_strength(x):
        if x < -80:
            return 0
        elif x < -60:
            return 1
        elif x < -40:
            return 2
        else:
            return 3
    
    ap_list = wifi.wlan.scan()
    content = [{"ssid": x[0].decode('ascii'), "strength": signal_strength(x[3])} for x in ap_list]
    return content

last_wifi_ap_list = getWiFiAPList()
last_wifi_ap_scan_time = time.time()

if wifi.wlan.isconnected():
    file = open("/sd/portal/config.json").read()
    content = json.loads(file)
    content["pythonWebREPL"]["endpoint"] = "ws://{}:8266".format(wifi.wlan.ifconfig()[0])
    content["onboarding"]["hasProvidedWifiCredentials"] = True
    
    with open("/sd/portal/config.json", "w") as outfile:
        outfile.write(json.dumps(content))
else:
    file = open("/sd/portal/config.json").read()
    content = json.loads(file)
    content["pythonWebREPL"]["endpoint"] = "ws://192.168.4.1:8266"
    content["onboarding"]["hasProvidedWifiCredentials"] = False
    
    with open("/sd/portal/config.json", "w") as outfile:
        outfile.write(json.dumps(content))

ssid = 'CYOCrawler'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, pm=network.WLAN.PM_PERFORMANCE, txpower=20, channel=6)

while ap.active() == False:
    pass

print('Connection successful')
print(ap.config('essid'), ap.ifconfig())

if not wifi.wlan.isconnected():
    from lib.network.microDNSSrv import MicroDNSSrv
    if MicroDNSSrv.Create({"portal.cyobot.com": "192.168.4.1"}):
        print("MicroDNSSrv started.")
    else :
        print("Error to starts MicroDNSSrv...")

# handle request from portal
@MicroWebSrv.route('/api/config')
def _httpHandlerGetConfig(httpClient, httpResponse):
    httpResponse.WriteResponseFile("/sd/portal/config.json", contentType="application/json", headers=None)

@MicroWebSrv.route('/api/internet')
def _httpHandlerGetWiFiConnectivity(httpClient, httpResponse):
    if wifi.wlan.isconnected():
        httpResponse.WriteResponseJSONOk(obj=json.loads('{"status": "connected"}'), headers=None)
    else:
        httpResponse.WriteResponseJSONOk(obj=json.loads('{"status": "disconnected"}'), headers=None)

@MicroWebSrv.route('/api/wifi')
def _httpHandlerGetWiFi(httpClient, httpResponse):
    global last_wifi_ap_list
    global last_wifi_ap_scan_time
    if time.time() - last_wifi_ap_scan_time > 10:
        last_wifi_ap_list = getWiFiAPList()
        last_wifi_ap_scan_time = time.time()
    httpResponse.WriteResponseJSONOk(obj=last_wifi_ap_list, headers=None)

@MicroWebSrv.route('/api/wifi', 'POST')
def _httpHandlerPostWiFiCredential(httpClient, httpResponse):
    # receive credentials from portal
    # attempt to connect
    # if successful, update config.json (pythonwebrepl --> ws://<NEW IP>:8266) AND onboarding.hasProvidedWifiCredentials --> True
    # if not, do not need to update
    # return "success" or "fail" to client
    data = httpClient.ReadRequestContentAsJSON()
    wifi.connect(data["ssid"], data["password"])

    #! TODO: also store this credential in INTERNAL config so that we can connect in the future auto
    if wifi.wlan.isconnected():
        file = open("/sd/portal/config.json").read()
        content = json.loads(file)
        content["pythonWebREPL"]["endpoint"] = "ws://{}:8266".format(wifi.wlan.ifconfig()[0])
        content["onboarding"]["hasProvidedWifiCredentials"] = True
        
        with open("/sd/portal/config.json", "w") as outfile:
            outfile.write(json.dumps(content))

        file = open("/sd/lib/brain/config.json").read()
        content = json.loads(file)
        content["ssid"] = data["ssid"]
        content["password"] = data["password"]

        with open("/sd/lib/brain/config.json", "w") as outfile:
            outfile.write(json.dumps(content))

        httpResponse.WriteResponseJSONOk(obj=json.dumps("success"), headers=None)
    else:
        httpResponse.WriteResponseJSONOk(obj=json.dumps("fail"), headers=None)
    
    time.sleep(1)
    import machine
    machine.reset()

srv = MicroWebSrv(webPath='/sd/portal/')

if not wifi.wlan.isconnected():
    matrix.scroll("AP MODE", speed=0.05, red=0, green=0, blue=80)

srv.Start(threaded=True)

if wifi.wlan.isconnected():
    import webrepl
    while webrepl.client_s is None:
        matrix.scroll(wifi.wlan.ifconfig()[0], speed=0.1, red=0, green=0, blue=80)
        time.sleep(2.0)
# else:
#     while webrepl.client_s is None:
#         matrix.scroll(".", speed=0.1, red=0, green=0, blue=80)
#         time.sleep(1.0)

import gc
gc.mem_free()
gc.mem_alloc()