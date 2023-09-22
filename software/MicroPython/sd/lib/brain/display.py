import machine, neopixel, time

class Matrix:
	def __init__(self):
		self.np = neopixel.NeoPixel(machine.Pin(33), 33)

	def set_manual(self, index, data):
		self.np[index] = data
		self.np.write()
	
	def set_custom(self, indices, color):
		for i in range(33):
			if i in indices:
				self.np[i] = color
			else:
				self.np[i] = (0, 0, 0)
		self.np.write()

	def set_pixel(self, pixel):
		self.np[pixel.index] = pixel.get_color()
		self.np.write()

	def reset(self):
		for i in range(33):
			self.np[i] = (0, 0, 0)
		self.np.write()

	def set_all(self, color):
		if len(color) != 3:
			print("Input color is incorrect. Color value should be (red, green, blue)")
			return

		for i in range(33):
			self.np[i] = color
		self.np.write()
	
	def set_character(self, character, offset = 0, red = 5, green = 5, blue = 5, multiplex = False, indices=None):
		# The matrix is a 5x5 matrix, with following index
		# x x x x x       x x x       0  1  2  3  4
		# x x x x x     x       x     5  6  7  8  9
		# x x x x x =>  x x x x x     10 11 12 13 14
		# x x x x x     x       x     15 16 17 18 19
		# x x x x x     x       x     20 21 22 23 24
		# Need to map this index with the index of the physical matrix
		## There are 13 different positions that a character can take, with the following offset values [6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6]

		## The following shows the index of matrix at each offset position
		### The character of alphabet 3x5 can refer to the list of each position, and only turn on LED if it's not -1 here, and there's an index value in the character matrix
		
		offset_pixel_list = {
			6: [
				-1, -1, -1, -1, -1,
				-1, -1, -1, -1, -1,
				-1, -1, -1, -1, 12,
				-1, -1, -1, -1, -1,
				-1, -1, -1, -1, -1
				],
			5: [
				-1, -1, -1, -1, -1,
				-1, -1, -1, -1,  5,
				-1, -1, -1, 12, 13,
				-1, -1, -1, -1, 21,
				-1, -1, -1, -1, -1
				],
			4: [
				-1, -1, -1, -1,  0,
				-1, -1, -1,  5,  6,
				-1, -1, 12, 13, 14,
				-1, -1, -1, 21, 22,
				-1, -1, -1, -1, 28
				],
			3: [
				-1, -1, -1,  0,  1,
				-1, -1,  5,  6,  7,
				-1, 12, 13, 14, 15,
				-1, -1, 21, 22, 23,
				-1, -1, -1, 28, 29
				],
			2: [
				-1, -1,  0,  1,  2,
				-1,  5,  6,  7,  8,
				12, 13, 14, 15, 16,
				-1, 21, 22, 23, 24,
				-1, -1, 28, 29, 30
				],
			1: [
				-1,  0,  1,  2,  3,
				 5,  6,  7,  8,  9,
				13, 14, 15, 16, 17,
				21, 22, 23, 24, 25,
				-1, 28, 29, 30, 31
				],
			0: [
				 0,  1,  2,  3,  4,
				 6,  7,  8,  9, 10,
				14, 15, 16, 17, 18,
				22, 23, 24, 25, 26,
				28, 29, 30, 31, 32
				],
			-1: [
				 1,  2,  3,  4, -1,
				 7,  8,  9, 10, 11,
				15, 16, 17, 18, 19,
				23, 24, 25, 26, 27,
				29, 30, 31, 32, -1
				],
			-2: [
				 2,  3,  4, -1, -1, 
				 8,  9, 10, 11, -1, 
				16, 17, 18, 19, 20, 
				24, 25, 26, 27, -1, 
				30, 31, 32, -1, -1
			],
			-3: [
				 3,  4, -1, -1, -1, 
				 9, 10, 11, -1, -1, 
				17, 18, 19, 20, -1, 
				25, 26, 27, -1, -1, 
				31, 32, -1, -1, -1
				],
			-4: [
				 4, -1, -1, -1, -1, 
				10, 11, -1, -1, -1, 
				18, 19, 20, -1, -1, 
				26, 27, -1, -1, -1, 
				32, -1, -1, -1, -1
				],
			-5: [
				-1, -1, -1, -1, -1, 
				11, -1, -1, -1, -1, 
				19, 20, -1, -1, -1, 
				27, -1, -1, -1, -1, 
				-1, -1, -1, -1, -1
				],
			-6: [
				-1, -1, -1, -1, -1, 
				-1, -1, -1, -1, -1, 
				20, -1, -1, -1, -1, 
				-1, -1, -1, -1, -1, 
				-1, -1, -1, -1, -1
				]
		}

		pixel_list = []

		alphabet = Alphabet()

		if indices is None:
			indices = alphabet.alphabet[character] 
		
		for index in indices:
			p = offset_pixel_list[offset][index]
			if p != -1:
				pixel_list.append(Pixel(index = p, red = red, green = green, blue = blue))

		for pixel in pixel_list:
			self.np[pixel.index] = pixel.get_color()

		if not multiplex:
			self.np.write()
		return

	def scroll_character(self, character):
		for i in range(13):
			self.set_character(character, i - 6)
			time.sleep(0.25)
			self.reset()
	
	def scroll(self, string, speed = 0.2, red = 5, green = 5, blue = 5):
		character_list = [char for char in string]
		pipeline = []
		offset_list = []
		pipeline.append(character_list.pop(0))
		offset_list.append(-6)

		while len(pipeline) > 0:
			self.reset()
			for i in range(len(pipeline)):
				self.set_character(pipeline[i], offset = offset_list[i], multiplex = True, red = red, green = green, blue = blue)
			self.np.write()

			for i in range(len(offset_list)):
				offset_list.append(offset_list.pop(0) + 1)

			new_pipeline = []
			new_offset = []
			for i, c in enumerate(pipeline):
				if offset_list[i] < -6 or offset_list[i] > 6:
					continue
				else:
					new_pipeline.append(c)
					new_offset.append(offset_list[i])

			if len(new_pipeline) == 0:
				self.reset()
				break

			if new_offset[-1] == 1 and len(character_list) > 0:
				new_pipeline.append(character_list.pop(0))
				new_offset.append(-6)

			pipeline = new_pipeline
			offset_list = new_offset

			time.sleep(speed)

class Pixel:
	def __init__(self, index = 0, red = 0, green = 0, blue = 0):
		self.index = index
		self.red = red
		self.green = green
		self.blue = blue

	def set(self, red = -1, green = -1, blue = -1):
		if red !=  self.red and red != -1:
			self.red = red
		if blue != self.blue and blue != -1:
			self.blue = blue
		if green != self.green and green != -1:
			self.green = green

	def get_color(self):
		return (self.red, self.green, self.blue)

class Alphabet:
	# x x x x x       x x x       0  1  2  3  4
	# x x x x x     x       x     5  6  7  8  9
	# x x x x x =>  x x x x x     10 11 12 13 14
	# x x x x x     x       x     15 16 17 18 19
	# x x x x x     x       x     20 21 22 23 24
	def __init__(self):
		self.alphabet = {
			"A": [1, 2, 3, 5, 9, 10, 11, 12, 13, 14, 15, 19, 20, 24],
			"B": [0, 1, 2, 5, 8, 10, 11, 12, 13, 15, 19, 20, 21, 22, 23],
			"C": [1, 2, 3, 5, 9, 10, 15, 19, 21, 22, 23],
			"D": [0, 1, 2, 3, 5, 9, 10, 14, 15, 19, 20, 21, 22, 23],
			"E": [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 15, 20, 21, 22, 23, 24],
			"F": [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 15, 20],
			"G": [1, 2, 3, 5, 10, 12, 13, 14, 15, 19, 21, 22, 23],
			"H": [0, 4, 5, 9, 10, 11, 12, 13, 14, 15, 19, 20, 24],
			"I": [1, 2, 3, 7, 12, 17, 21, 22, 23],
			"J": [0, 1, 2, 3, 4, 8, 13, 15, 18, 21, 22],
			"K": [0, 4, 5, 8, 10, 11, 12, 15, 18, 20, 24],
			"L": [1, 6, 11, 16, 21, 22, 23, 24],
			"M": [0, 4, 5, 6, 8, 9, 10, 12, 14, 15, 19, 20, 24],
			"N": [0, 4, 5, 6, 9, 10, 12, 14, 15, 18, 19, 20, 24],
			"O": [1, 2, 3, 5, 9, 10, 14, 15, 19, 21, 22, 23],
			"P": [0, 1, 2, 3, 5, 9, 10, 11, 12, 13, 15, 20],
			"Q": [1, 2, 5, 8, 10, 13, 15, 18, 21, 22, 23, 24],
			"R": [0, 1, 2, 3, 5, 9, 10, 11, 12, 13, 15, 18, 20, 24],
			"S": [1, 2, 3, 5, 11, 12, 13, 19, 20, 21, 22, 23],
			"T": [0, 1, 2, 3, 4, 7, 12, 17, 22],
			"U": [0, 4, 5, 9, 10, 14, 15, 19, 21, 22, 23],
			"V": [0, 4, 5, 9, 10, 14, 16, 18, 22],
			"W": [0, 4, 5, 9, 10, 12, 14, 15, 17, 19, 21, 23],
			"X": [0, 4, 6, 8, 12, 16, 18, 20, 24],
			"Y": [0, 4, 6, 8, 12, 17, 22],
			"Z": [0, 1, 2, 3, 4, 8, 12, 16, 20, 21, 22, 23, 24],
			"0": [1, 2, 3, 5, 6, 9, 10, 12, 14, 15, 18, 19, 21, 22, 23],
			"1": [2, 6, 7, 12, 17, 21, 22, 23],
			"2": [1, 2, 5, 8, 12, 16, 20, 21, 22, 23],
			"3": [1, 2, 5, 8, 12, 15, 18, 21, 22],
			"4": [3, 7, 8, 11, 13, 15, 16, 17, 18, 19, 23],
			"5": [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 19, 20, 21, 22, 23],
			"6": [1, 2, 3, 5, 10, 11, 12, 13, 15, 19, 21, 22, 23],
			"7": [0, 1, 2, 3, 4, 8, 12, 16, 20],
			"8": [1, 2, 3, 5, 9, 11, 12, 13, 15, 19, 21, 22, 23],
			"9": [1, 2, 3, 5, 9, 11, 12, 13, 14, 19, 21, 22, 23],
			" ": [],
			".": [22],
			"_": [20, 21, 22, 23, 24],
			"[": [0, 1, 5, 10, 15, 20, 21],
			"]": [3, 4, 9, 14, 19, 23, 24],
		}