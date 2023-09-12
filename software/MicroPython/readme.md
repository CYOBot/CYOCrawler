# Introdution
This is the official release of CYOBot OS for CYOCrawler v2.0
The repo includes source code for onboard peripherals, including:
* Source code for robot kinematics (walking, rotating, PCA9685 control)
* Source code for NeoPixel LED Ring and LED matrix: individual LED control, text scrolling, bitmap display, etc
* Source code for micro SD card mounting
* Network management system, including AP mode and STA mode, DNS
* * Portal for coding interface and WiFi setup

# Installation
## Windows
For Windows, **esptool** and **rshell** work on top of a Conda environment. An `install.ps1` file is included to help with the process.

## Ubuntu
The `cyobot-os.bin` is the MicroPython release that works with CYOBrain v2.0

To burn the CYOBrain, install `esptool.py` to your computer, and run the following commands:

```bash
esptool.py --port <PORT> erase_flash
```
Then
```bash
esptool.py --chip esp32 --port <PORT> --baud 460800 write_flash -z 0x1000 cyobot-os.bin
```
Example if you are running this on Ubuntu

```bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 cyobot-os.bin
```

Then, copy content in the folder `/sd` to the micro SD card to be plugged into CYOBrain.

Next, copy all the source code from `/pyboard` folder to root directory of CYOBrain by install [rshell](https://github.com/dhylands/rshell), connect to the board running MicroPython, and call the following command:

```bash
# go to pyboard directory in this folder (not to confuse this with the root directory, /pyboard)
cd pyboard

# copy everything from the pyboard folder to the root directory of CYOBrain
rsync . /pyboard
```

Finally, hard reset your CYOBrain by either pressing the reset button at the top of the CYOBrain, or disconnect power source (unplug USB cable/switch off the board) and reconnect. If you see the LED matrix scrolling text "AP MODE", the board is now running OS with everything else setup. Connect your computer to the board via WiFi (find the access point name `CYOCrawler`), open browser and either type in `portal.cyobot.com` or `192.168.4.1` to load the portal and start coding.

# Troubleshoot
## WebREPL is not on
The file `webrepl_cfg.py` with password information of WebREPL, and the following code in `boot.py` should be sufficient to turn on and configure WebREPL at startup:
```python
import webrepl
webrepl.start()
```

However, if WebREPL is not turned on, go through the following steps to turn on `webrepl` to be loaded on startup. Open `REPL` by typing into a terminal running `rshell` connected to CYOBrain
```bash
repl
```
Then turn on `webrepl` with:
```python
import webrepl_setup
```
Press `E` to enable webrepl on startup, and set `cyobot` as the password.

**Note**: The portal will attempt to connect to CYOBrain via webrepl with the password `cyobot`, so if you set the password to be anything else, the connection will not be successfully established.