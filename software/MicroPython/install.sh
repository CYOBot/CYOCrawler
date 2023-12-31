# Color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Check to see if board is found on /dev/ttyUSB0${NC}"

if [ -e /dev/ttyUSB0 ]; then
    echo -e "${GREEN}/dev/ttyUSB0 is available on this device.${NC}"
else
    echo -e "${RED}/dev/ttyUSB0 is not available on this device.${NC}"
fi

if [ -e /dev/ttyUSB0 ]; then
	echo -e "${GREEN}Erase memory${NC}"
	esptool.py --port /dev/ttyUSB0 erase_flash

	echo -e "${GREEN}Start writing cyobot-os.bin to board${NC}"
	esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 cyobot-os.bin
	
	echo -e "${GREEN}Copy files to /pyboard${NC}"
	cd pyboard
	rshell -p /dev/ttyUSB0 -b 115200 rsync . /pyboard

	echo -e "${GREEN}Done${NC}"

fi
