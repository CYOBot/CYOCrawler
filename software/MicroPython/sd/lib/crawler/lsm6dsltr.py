# Ported from https://github.com/jposada202020/MicroPython_LSM6DSOX
# Customized to use with onboard LSM6DSLTR
# Subject to changes, need lots of checking

from time import sleep
from math import radians
from micropython import const
from lib.utils.i2c_helpers import CBits, RegisterStruct

try:
    from typing import Tuple
except ImportError:
    pass

RATE_SHUTDOWN = const(0b0000)
RATE_12_5_HZ = const(0b0001)
RATE_26_HZ = const(0b0010)
RATE_52_HZ = const(0b0011)
RATE_104_HZ = const(0b0100)
RATE_208_HZ = const(0b0101)
RATE_416_HZ = const(0b0110)
RATE_833_HZ = const(0b0111)
RATE_1_66K_HZ = const(0b1000)
RATE_3_33K_HZ = const(0b1001)
RATE_6_66K_HZ = const(0b1010)

data_rate_values = (
    RATE_12_5_HZ,
    RATE_26_HZ,
    RATE_52_HZ,
    RATE_104_HZ,
    RATE_208_HZ,
    RATE_416_HZ,
    RATE_833_HZ,
    RATE_1_66K_HZ,
    RATE_3_33K_HZ,
    RATE_6_66K_HZ
)

RANGE_2G = const(0b00)
RANGE_4G = const(0b10)
RANGE_8G = const(0b11)
RANGE_16G = const(0b01)
acceleration_range_values = (RANGE_2G, RANGE_16G, RANGE_4G, RANGE_8G)
acceleration_factor = (0.061, 0.488, 0.122, 0.244)

RANGE_250_DPS = const(0b00)
RANGE_500_DPS = const(0b01)
RANGE_1000_DPS = const(0b10)
RANGE_2000_DPS = const(0b11)
gyro_range_values = (RANGE_250_DPS, RANGE_500_DPS, RANGE_1000_DPS, RANGE_2000_DPS)
gyro_factor = (8.75, 17.50, 35.0, 70.0)

_LSM6DS_MLC_INT1 = const(0x0D)
_LSM6DS_WHOAMI = const(0xF)
_CTRL1_XL = const(0x10)
_CTRL2_G = const(0x11)
_LSM6DS_CTRL3_C = const(0x12) # not sure what this is for LSM6DSLTR
_OUT_TEMP_L = const(0x20)
_OUTX_L_G = const(0x22)
_OUTX_L_A = const(0x28) # this is OUTX_L_XL for LSM6DSLTR, wonder why the name here is _A
_MILLI_G_TO_ACCEL = 0.00980665
_TEMPERATURE_SENSITIVITY = 256
_TEMPERATURE_OFFSET = 25.0


class LSM6DSLTR:
    _device_id = RegisterStruct(_LSM6DS_WHOAMI, "<b")
    _raw_accel_data = RegisterStruct(_OUTX_L_A, "<hhh")
    _raw_gyro_data = RegisterStruct(_OUTX_L_G, "<hhh")
    _raw_temp_data = RegisterStruct(_OUT_TEMP_L, "<h")

    _acceleration_range = CBits(2, _CTRL1_XL, 2)
    _acceleration_data_rate = CBits(4, _CTRL1_XL, 2)

    _gyro_data_rate = CBits(4, _CTRL2_G, 4)
    _gyro_range = CBits(2, _CTRL2_G, 2)

    _sw_reset = CBits(1, _LSM6DS_CTRL3_C, 0)
    _bdu = CBits(1, _LSM6DS_CTRL3_C, 6)
    _block_data_enable = CBits(1, _LSM6DS_CTRL3_C, 4)

    def __init__(self, i2c, address: int = 0x6A) -> None:
        self._i2c = i2c
        self._address = address

        self.reset()

        self._bdu = True
        self._acceleration_full_scale = False
        self._acceleration_data_rate = RATE_104_HZ
        self._gyro_data_rate = RATE_104_HZ
        self.acceleration_range = RANGE_4G
        self.gyro_range = RANGE_250_DPS

    def reset(self) -> None:
        """Resets the sensor's configuration into an initial state"""
        self._sw_reset = True
        while self._sw_reset:
            sleep(0.001)

    @property
    def acceleration(self) -> Tuple[float, float, float]:
        """
        The x, y, z acceleration values returned in a 3-tuple and are in m / s ^ 2.
        """
        rawx, rawy, rawz = self._raw_accel_data

        x = rawx * self._cached_conversion_factor * _MILLI_G_TO_ACCEL
        y = rawy * self._cached_conversion_factor * _MILLI_G_TO_ACCEL
        z = rawz * self._cached_conversion_factor * _MILLI_G_TO_ACCEL

        return x, y, z

    @property
    def gyro(self) -> Tuple[float, float, float]:
        """
        The x, y, z angular velocity values returned in a 3-tuple and are in radians / second
        """
        rawx, rawy, rawz = self._raw_gyro_data
        x = radians(rawx * self._gyro_cached_conversion_factor / 1000)
        y = radians(rawy * self._gyro_cached_conversion_factor / 1000)
        z = radians(rawz * self._gyro_cached_conversion_factor / 1000)

        return x, y, z

    @property
    def acceleration_range(self) -> int:
        """
        Sensor acceleration_range

        +--------------------------------+------------------+
        | Mode                           | Value            |
        +================================+==================+
        | :py:const:`lsm6dsox.RANGE_2G`  | :py:const:`0b00` |
        +--------------------------------+------------------+
        | :py:const:`lsm6dsox.RANGE_4G`  | :py:const:`0b10` |
        +--------------------------------+------------------+
        | :py:const:`lsm6dsox.RANGE_8G`  | :py:const:`0b11` |
        +--------------------------------+------------------+
        | :py:const:`lsm6dsox.RANGE_16G` | :py:const:`0b01` |
        +--------------------------------+------------------+
        """
        values = ("RANGE_2G", "RANGE_16G", "RANGE_4G", "RANGE_8G")
        return values[self._cached_acceleration_range]

    @acceleration_range.setter
    def acceleration_range(self, value: int) -> None:
        if value not in acceleration_range_values:
            raise ValueError("Value must be a valid acceleration_range setting")
        self._acceleration_range = value
        self._cached_acceleration_range = value
        self._cached_conversion_factor = acceleration_factor[value]
        sleep(0.2)

    @property
    def gyro_range(self) -> int:
        """
        Sensor gyro_range

        +-------------------------------------+------------------+
        | Mode                                | Value            |
        +=====================================+==================+
        | :py:const:`lsm6dsox.RANGE_250_DPS`  | :py:const:`0b00` |
        +-------------------------------------+------------------+
        | :py:const:`lsm6dsox.RANGE_500_DPS`  | :py:const:`0b01` |
        +-------------------------------------+------------------+
        | :py:const:`lsm6dsox.RANGE_1000_DPS` | :py:const:`0b10` |
        +-------------------------------------+------------------+
        | :py:const:`lsm6dsox.RANGE_2000_DPS` | :py:const:`0b11` |
        +-------------------------------------+------------------+
        """
        values = ("RANGE_250_DPS", "RANGE_500_DPS", "RANGE_1000_DPS", "RANGE_2000_DPS")

        return values[self._cached_gyro_range]

    @gyro_range.setter
    def gyro_range(self, value: int) -> None:
        if value not in gyro_range_values:
            raise ValueError("Value must be a valid gyro_range setting")

        self._cached_gyro_range = value
        self._gyro_cached_conversion_factor = gyro_factor[value]
        sleep(0.2)

    @property
    def acceleration_data_rate(self) -> str:
        """
        Sensor acceleration_data_rate

        +------------------------------------+--------------------+
        | Mode                               | Value              |
        +====================================+====================+
        | :py:const:`lsm6dsox.RATE_SHUTDOWN` | :py:const:`0b0000` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_12_5_HZ`  | :py:const:`0b0001` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_26_HZ`    | :py:const:`0b0010` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_52_HZ`    | :py:const:`0b0011` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_104_HZ`   | :py:const:`0b0100` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_208_HZ`   | :py:const:`0b0101` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_416_HZ`   | :py:const:`0b0110` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_833_HZ`   | :py:const:`0b0111` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_1_66K_HZ` | :py:const:`0b1000` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_3_33K_HZ` | :py:const:`0b1001` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_6_66K_HZ` | :py:const:`0b1010` |
        +------------------------------------+--------------------+
        """
        values = (
            "RATE_SHUTDOWN",
            "RATE_12_5_HZ",
            "RATE_26_HZ",
            "RATE_52_HZ",
            "RATE_104_HZ",
            "RATE_208_HZ",
            "RATE_416_HZ",
            "RATE_833_HZ",
            "RATE_1_66K_HZ",
            "RATE_3_33K_HZ",
            "RATE_6_66K_HZ"
        )
        return values[self._acceleration_data_rate]

    @acceleration_data_rate.setter
    def acceleration_data_rate(self, value: int) -> None:
        if value not in data_rate_values:
            raise ValueError("Value must be a valid acceleration_data_rate setting")
        self._acceleration_data_rate = value
        sleep(0.2)

    @property
    def gyro_data_rate(self) -> str:
        """
        Sensor gyro_data_rate

        +------------------------------------+--------------------+
        | Mode                               | Value              |
        +====================================+====================+
        | :py:const:`lsm6dsox.RATE_SHUTDOWN` | :py:const:`0b0000` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_12_5_HZ`  | :py:const:`0b0001` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_26_HZ`    | :py:const:`0b0010` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_52_HZ`    | :py:const:`0b0011` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_104_HZ`   | :py:const:`0b0100` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_208_HZ`   | :py:const:`0b0101` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_416_HZ`   | :py:const:`0b0110` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_833_HZ`   | :py:const:`0b0111` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_1_66K_HZ` | :py:const:`0b1000` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_3_33K_HZ` | :py:const:`0b1001` |
        +------------------------------------+--------------------+
        | :py:const:`lsm6dsox.RATE_6_66K_HZ` | :py:const:`0b1010` |
        +------------------------------------+--------------------+
        """
        values = (
            "RATE_SHUTDOWN",
            "RATE_12_5_HZ",
            "RATE_26_HZ",
            "RATE_52_HZ",
            "RATE_104_HZ",
            "RATE_208_HZ",
            "RATE_416_HZ",
            "RATE_833_HZ",
            "RATE_1_66K_HZ",
            "RATE_3_33K_HZ",
            "RATE_6_66K_HZ"
        )
        return values[self._gyro_data_rate]

    @gyro_data_rate.setter
    def gyro_data_rate(self, value: int) -> None:
        if value not in data_rate_values:
            raise ValueError("Value must be a valid gyro_data_rate setting")
        self._gyro_data_rate = value

    @property
    def temperature(self) -> float:
        """Temperature in Celsius"""

        temp = self._raw_temp_data

        return temp / _TEMPERATURE_SENSITIVITY + _TEMPERATURE_OFFSET