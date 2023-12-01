from lib.crawler.display import *
from lib.brain.display import *
import time

# check to see if button is pressed down
left = machine.Pin(27, machine.Pin.IN)
right = machine.Pin(0, machine.Pin.IN)

ring = LEDRing()
matrix = Matrix()
ring.reset()
matrix.reset()

if left.value() == 0:
    for i in range(12):
        ring.set_manual(i, (100, 0, 0))
        time.sleep(0.05)
    
    # enter factory reset mode
    cur_time = time.time()

    from lib.brain.display import *
    matrix.reset()
    while time.time() - cur_time < 3:
        if left.value() != 0:
            machine.reset()
    
    matrix.scroll("RESET", blue=100, speed=0.05)
    # run factory reset
    import json
    ## fix portal config file
    file = open("/sd/portal/config.json").read()
    content = json.loads(file)
    content["pythonWebREPL"]["endpoint"] = "ws://192.168.4.1:8266"
    content["onboarding"]["hasProvidedWifiCredentials"] = False
    
    with open("/sd/portal/config.json", "w") as outfile:
        outfile.write(json.dumps(content))
    
    ## fix brain config file
    with open("/sd/lib/brain/config.json", "w") as outfile:
        outfile.write(json.dumps({}))

for i in range(12):
    ring.set_manual(i, (0, 100, 0))
    time.sleep(0.05)
ring.reset()

import network
from lib.network.microWebSrv import MicroWebSrv
from lib.brain.wireless import *
import json
import webrepl

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
    from lib.crawler.sound import Speaker
    speaker = Speaker()
    time.sleep(1.0)
    ring.loading(blue=100)
    speaker.play_tone(frequency=3500, duration=0.1, volume=1)
    time.sleep(0.01)
    speaker.play_tone(frequency=3500, duration=0.1, volume=1)

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

ssid = 'CYOBot'

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

# if not wifi.wlan.isconnected():
    # matrix.scroll("AP MODE", speed=0.05, red=0, green=0, blue=80)

srv.Start(threaded=True)

import webrepl
if wifi.wlan.isconnected():
    ip_address = wifi.wlan.ifconfig()[0]
    character_list = [char for char in ip_address]
    offset_list = [(-7*i) for i in range(len(character_list))]
    
    matrix.reset()
    for i in range(len(character_list)):
        if offset_list[i] <= 6 and offset_list[i] >=-6:
            matrix.set_character(character_list[i], offset = offset_list[i] // 1, multiplex = True, blue = 100)
    matrix.np.write()
    
    redraw = False
    
    while webrepl.client_s is None:
        redraw = False

        if left.value() == 0 and right.value() != 0:
            for i in range(len(offset_list)):
                offset_list.append(offset_list.pop(0) + 0.1)
            redraw = True
        elif right.value() == 0 and left.value() != 0:
            for i in range(len(offset_list)):
                offset_list.append(offset_list.pop(0) - 0.1)
            redraw = True
        
        if redraw:
            matrix.reset()
            for i in range(len(character_list)):
                if offset_list[i] <= 6 and offset_list[i] >=-6:
                    matrix.set_character(character_list[i], offset = offset_list[i] // 1, multiplex = True, blue = 100)
            matrix.np.write()
        else:
            time.sleep(1.0)
else:
    on=True
    while webrepl.client_s is None:
        if on:
            matrix.reset()
            on = False
        else:
            matrix.set_manual(16, (100, 0, 100))
            on = True
        time.sleep(1.0)

matrix.reset()

import gc
gc.mem_free()
gc.mem_alloc()