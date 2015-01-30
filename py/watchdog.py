import config_file_out
import process
import config
import router_module
import subprocess
import os
import time

class Watchdog(router_module.RouterModule):
	def __init__(self, ctx):
		router_module.RouterModule.__init__(self, ctx)

		conf = config.Config.get_config()

		self.watchdog_fd = os.open("/dev/watchdog", os.O_WRONLY)
		if self.watchdog_fd == -1:
			raise RuntimeError("failed to open watchdog")

	def brutal_stop(self):
		pass

	def start(self):
		pid = os.fork()

		if pid == 0:
			# In child
			self.run()
		else:
			self.get_context().log("Watchdog pid is {0}".format(pid))
			# FIXME: need to remember the child's pid

	def run(self):
		while True:
			os.write(self.watchdog_fd, "hello\n")
			time.sleep(10)
