import machine, os, sdcard

# old cyobrain
# spi = machine.SoftSPI(sck=machine.Pin(14), miso=machine.Pin(2), mosi=machine.Pin(15))
# sd = sdcard.SDCard(spi, machine.Pin(13))

# cyobrain v2.0
spi = machine.SoftSPI(sck=machine.Pin(18), miso=machine.Pin(19), mosi=machine.Pin(23))
sd = sdcard.SDCard(spi, machine.Pin(4))

os.mount(sd, '/sd')