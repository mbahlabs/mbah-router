import time

class Timeout:
	def __init__(self, timeout):
		self.expiry = time.time() + timeout

	def is_expired(self):
		if time.time() > self.expiry:
			return True
		return False
