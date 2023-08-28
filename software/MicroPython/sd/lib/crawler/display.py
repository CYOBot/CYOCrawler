import machine
import time
import neopixel

class LEDRing:
	def __init__(self):
		self.np = neopixel.NeoPixel(machine.Pin(13), 12)

	def reset(self):
		for i in range(12):
			self.np[i] = (0, 0, 0)
		self.np.write()

	def loading(self, red = 10, green = 20, blue = 10, speed = 0.1):
		while True:
			for i in range(12):
				self.np[i] = (red, green, blue)
				self.np.write()
				time.sleep(speed)
			for i in range(12):
				self.np[i] = (0, 0, 0)
				self.np.write()
				time.sleep(speed)
