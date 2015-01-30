import config_file_out
import process
import config
import router_module
import subprocess
import os
import time
import pinger

class LedHeartbeat(router_module.RouterModule):
	def __init__(self, ctx):
		router_module.RouterModule.__init__(self, ctx)

		conf = config.Config.get_config()

	def brutal_stop(self):
		pass

	def start(self):
		pid = os.fork()

		if pid == 0:
			# In child
			self.run()
		else:
			self.get_context().log("Heartbeat pid is {0}".format(pid))
			# FIXME: need to remember the child's pid

	def set_led_color(self, val):
		try:
			with open("/dev/ttyACM0", "w") as f:
				f.write("{0}\n".format(val))
		except:
			pass

	def run(self):
		while True:
			last_lost = pinger.Pinger.get_last_lost(self.get_context())

			all_ok = True

			if last_lost >= 20:
				all_ok = False
			if last_lost == None:
				all_ok = False

			color = 2
			if all_ok == False:
				color = 1

			self.get_context().log("color is {}".format(color))

			self.set_led_color(0)
			time.sleep(.100)
			self.set_led_color(color)
			time.sleep(3)
