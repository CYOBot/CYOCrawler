import machine
import time
import neopixel

class LEDRing:
	def __init__(self):
		self.np = neopixel.NeoPixel(machine.Pin(13), 12)

	def set_manual(self, index, data):
		self.np[index] = data
		self.np.write()
	
	def set_custom(self, indices, color):
		for i in range(12):
			if i in indices:
				self.np[i] = color
			else:
				self.np[i] = (0, 0, 0)
		self.np.write()
	
	def set_pixel(self, pixel):
		self.np[pixel.index] = pixel.get_color()
		self.np.write()
	
	def reset(self):
		for i in range(12):
			self.np[i] = (0, 0, 0)
		self.np.write()
	
	def set_all(self, color):
		if len(color) != 3:
			print("Input color is incorrect. Color value should be (red, green, blue)")
			return

		for i in range(12):
			self.np[i] = color
		self.np.write()

	def loading(self, red = 10, green = 20, blue = 10, speed = 0.1):
		for i in range(12):
			self.np[i] = (red, green, blue)
			self.np.write()
			time.sleep(speed)
		for i in range(12):
			self.np[i] = (0, 0, 0)
			self.np.write()
			time.sleep(speed)
