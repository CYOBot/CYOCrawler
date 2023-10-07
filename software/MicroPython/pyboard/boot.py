# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import webrepl
webrepl.start()

import mount_sd
import sys
sys.path.append("/sd")

# import os
# os.chdir("/sd")

# check to see if there is main.py in SD card, if there is, overwrite the current file and restart
import os

try:
    os.stat("/sd/main.py")
    print("Found main.py, overwrite the main.py")
    
    # remove current main.py
    os.remove("main.py")
    
    with open('main.py', 'wt') as outfile:
        file = open('/sd/main.py', 'rt').read()
        outfile.write(file)
    
    # remove main.py in SD card
    os.remove("/sd/main.py")

except:
    print("No new file, continue")