from lib.crawler.lsm6dsltr import *
import machine

class IMU(LSM6DSLTR):
    def __init__(self, SDA = 21, SCL = 22):
        _ADDRESS = 0x6A
        self.i2c = machine.I2C(scl = machine.Pin(SCL), sda = machine.Pin(SDA))
        super().__init__(self.i2c, address=_ADDRESS)