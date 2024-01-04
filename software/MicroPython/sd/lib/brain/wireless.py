import network, time

class WiFi:
	def __init__(self):
		self.wlan = network.WLAN(network.STA_IF)
		self.wlan.active(True)

	def connect(self, ssid = "", password = "", verbose=False):
		if ssid == "":
			print("Please input SSID")
			return
		if password == "":
			print("Please input password")
			return

		try:
			# ensure that if the new connection is wrong, it is wrong (not showing Connected anymore)
			self.wlan.disconnect()
		except Exception as e:
			print(e)
		self.wlan.connect(ssid, password)

		print("Attempt to connect to {}".format(ssid))
		count = 0
		if verbose:
			from .display import Matrix
			matrix = Matrix()
			on=False
		while count < 5 and not self.wlan.isconnected():
			if verbose:
				if not on:
					matrix.set_manual(16, (100, 0, 100))
					on=True
				else:
					matrix.reset()
					on=False
			print(".", end="")
			time.sleep(1)
			count += 1
		print("")
		if verbose:
			matrix.reset()

		if not self.wlan.isconnected():
			print("Connection timeout")
			self.wlan.disconnect()
			return

		print("Connection status: {}".format(self.wlan.isconnected()))
		print("Connection info: {}".format(self.wlan.ifconfig()))

		globals().pop("matrix", None)
		globals().pop("Matrix", None)
		import gc
		gc.collect()
		gc.mem_free()
		gc.mem_alloc()
