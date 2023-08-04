import network, time

class WiFi:
	def __init__(self):
		self.wlan = network.WLAN(network.STA_IF)
		self.wlan.active(True)

	def connect(self, ssid = "", password = ""):
		if ssid == "":
			print("Please input SSID")
			return
		if password == "":
			print("Please input password")
			return
		self.wlan.connect(ssid, password)

		print("Attempt to connect to {}".format(ssid))
		count = 0
		while count < 20 and not self.wlan.isconnected():
			print(".", end="")
			time.sleep(1)
			count += 1
		print("")

		if not self.wlan.isconnected():
			print("Connection timeout")
			return

		print("Connection status: {}".format(self.wlan.isconnected()))
		print("Connection info: {}".format(self.wlan.ifconfig()))
