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
