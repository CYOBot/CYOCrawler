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

try:
    del file
    del outfile
except:
    pass

import network
from lib.network.microWebSrv import MicroWebSrv
from lib.brain.wireless import *
import json
import webrepl

wifi = WiFi()

try:
    file = open("/sd/lib/brain/config.json").read()
    content = json.loads(file)
    wifi.connect(content["ssid"], content["password"], verbose=True)
    del file
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
    
    try:
        ap_list = wifi.wlan.scan()
    except:
        try:
            ap_list = ap.scan()
        except:
            pass
    content = [{"ssid": x[0].decode('ascii'), "strength": signal_strength(x[3])} for x in ap_list]
    return content

last_wifi_ap_list = getWiFiAPList()
last_wifi_ap_scan_time = time.time()

"""
for i in range(12):
    self.np[i] = (red, green, blue)
    self.np.write()
    time.sleep(speed)
for i in range(12):
    self.np[i] = (0, 0, 0)
    self.np.write()
    time.sleep(speed)
"""

if wifi.wlan.isconnected():
    from lib.crawler.sound import Speaker
    speaker = Speaker()
    ring.np[0] = (0, 100, 0)
    ring.np.write()
    ring.np[1] = (0, 100, 0)
    ring.np.write()
    speaker.play_tone(frequency=261, duration=0.2, volume=2)
    time.sleep(0.01)
    ring.np[2] = (0, 100, 0)
    ring.np.write()
    ring.np[3] = (0, 100, 0)
    ring.np.write()
    speaker.play_tone(frequency=392, duration=0.2, volume=2)
    time.sleep(0.01)
    ring.np[4] = (0, 100, 0)
    ring.np.write()
    ring.np[5] = (0, 100, 0)
    ring.np.write()
    speaker.play_tone(frequency=659, duration=0.2, volume=2)
    time.sleep(0.01)
    ring.np[6] = (0, 100, 0)
    ring.np.write()
    ring.np[7] = (0, 100, 0)
    ring.np.write()
    speaker.play_tone(frequency=1047, duration=0.2, volume=2)
    time.sleep(0.01)
    for i in range(8, 12):
        ring.np[i] = (0, 100, 0)
        ring.np.write()
        time.sleep(0.1)
    for i in range(12):
        ring.np[i] = (0, 0, 0)
        ring.np.write()
        time.sleep(0.1)

    file = open("/sd/portal/config.json").read()
    content = json.loads(file)
    content["pythonWebREPL"]["endpoint"] = "ws://{}:8266".format(wifi.wlan.ifconfig()[0])
    content["onboarding"]["hasProvidedWifiCredentials"] = True
    del file
    
    with open("/sd/portal/config.json", "w") as outfile:
        outfile.write(json.dumps(content))
    del outfile
else:
    file = open("/sd/portal/config.json").read()
    content = json.loads(file)
    content["pythonWebREPL"]["endpoint"] = "ws://192.168.4.1:8266"
    content["onboarding"]["hasProvidedWifiCredentials"] = False
    del file
    
    with open("/sd/portal/config.json", "w") as outfile:
        outfile.write(json.dumps(content))
    del outfile

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
    httpResponse.WriteResponseFile("/sd/portal/config.json", contentType="application/json", headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*'
    })

@MicroWebSrv.route('/api/internet')
def _httpHandlerGetWiFiConnectivity(httpClient, httpResponse):
    if wifi.wlan.isconnected():
        httpResponse.WriteResponseJSONOk(obj=json.loads('{"status": "connected"}'), headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        })
    else:
        httpResponse.WriteResponseJSONOk(obj=json.loads('{"status": "disconnected"}'), headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        })

@MicroWebSrv.route('/api/wifi')
def _httpHandlerGetWiFi(httpClient, httpResponse):
    global last_wifi_ap_list
    global last_wifi_ap_scan_time
    if time.time() - last_wifi_ap_scan_time > 10:
        last_wifi_ap_list = getWiFiAPList()
        last_wifi_ap_scan_time = time.time()
    httpResponse.WriteResponseJSONOk(obj=last_wifi_ap_list, headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*'
    })

@MicroWebSrv.route('/api/wifi', method='OPTIONS')
def _httpHandlerOptionWiFiCredential(httpClient, httpResponse):
    httpResponse.WriteResponseOk(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*'
    })

@MicroWebSrv.route('/api/wifi', 'POST')
def _httpHandlerPostWiFiCredential(httpClient, httpResponse):
    # receive credentials from portal
    # attempt to connect
    # if successful, update config.json (pythonwebrepl --> ws://<NEW IP>:8266) AND onboarding.hasProvidedWifiCredentials --> True
    # if not, do not need to update
    # return "success" or "fail" to client
    data = httpClient.ReadRequestContentAsJSON()

    # try 4 times (5 seconds/time)
    for i in range(4):
        wifi.connect(data["ssid"], data["password"], verbose=True)
        if wifi.wlan.isconnected():
            break

    #! TODO: also store this credential in INTERNAL config so that we can connect in the future auto
    if wifi.wlan.isconnected():
        file = open("/sd/portal/config.json").read()
        content = json.loads(file)
        content["pythonWebREPL"]["endpoint"] = "ws://{}:8266".format(wifi.wlan.ifconfig()[0])
        content["onboarding"]["hasProvidedWifiCredentials"] = True
        del file
        
        with open("/sd/portal/config.json", "w") as outfile:
            outfile.write(json.dumps(content))
        del outfile

        file = open("/sd/lib/brain/config.json").read()
        content = json.loads(file)
        content["ssid"] = data["ssid"]
        content["password"] = data["password"]
        del file

        with open("/sd/lib/brain/config.json", "w") as outfile:
            outfile.write(json.dumps(content))
        del outfile

        httpResponse.WriteResponseJSONOk(obj=json.dumps("success"), headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        })
        
        time.sleep(2)
        import machine
        machine.reset()

    else:
        httpResponse.WriteResponseJSONOk(obj=json.dumps("fail"), headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        })

# @MicroWebSrv.route('/api/config', method='OPTIONS')
# def _httpHandlerOptionConfig(httpClient, httpResponse):
#     httpResponse.WriteResponseOk(headers={
#         'Access-Control-Allow-Origin': '*',
#         'Access-Control-Allow-Methods': '*',
#         'Access-Control-Allow-Headers': '*'
#     })

@MicroWebSrv.route('/api/config', 'POST')
def _httpHandlerPostConfig(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    print(data)
    
    try:
        file = open("/sd/portal/config.json").read()
        content = json.loads(file)
        content["pythonWebREPL"]["endpoint"] = data["wsEndpoint"]
        del file
        
        with open("/sd/portal/config.json", "w") as outfile:
            outfile.write(json.dumps(content))
        del outfile
        
        httpResponse.WriteResponseOk(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        })
    except Exception as e:
        print(e)
        httpResponse.WriteReponseError(500, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        })

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

        if left.value() != 0 and right.value() == 0:
            for i in range(len(offset_list)):
                offset_list.append(offset_list.pop(0) + 0.1)
            redraw = True
        elif right.value() != 0 and left.value() == 0:
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

globals().pop("ring", None)
globals().pop("LEDRing", None)
globals().pop("matrix", None)
globals().pop("Matrix", None)
globals().pop("speaker", None)
globals().pop("Speaker", None)
globals().pop("left", None)
globals().pop("right", None)
globals().pop("content", None)
globals().pop("webrepl", None)

import gc
gc.collect()
gc.mem_free()
gc.mem_alloc()