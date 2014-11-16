import config_file_out
import process
import config
import router_module
import subprocess
import os
import time

class Pinger(router_module.RouterModule):
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
			pass
			# FIXME: need to remember the child's pid

	def ping_loss_test(self, target, iface, count, interv):
		ping_result = process.shell_command(self.ctx,
			"ping -n -q -i {} -c {} -I {} {}".format(interv, count, iface, target), ignoreResult=True)

		if ping_result['returncode'] != 0:
			return None

		grep_result = process.shell_command(self.ctx,
			"egrep -o '[0-9]{1,3}% packet loss' | cut -d '%' -f 1", input=ping_result["stdout"]+"\x04")

		if grep_result['returncode'] != 0:
			raise RuntimeError("grep filter failed, shouldn't happen")

		return int(grep_result['stdout'].rstrip())

	def run(self):
		f = self.ctx.open_persistent_file("pinger", "ping.csv", "a")

		while True:
			result = self.ping_loss_test("www.google.com", "eth1", 10, 0.2)
			time.sleep(15)

			f.write("{},{},{},{}\n".format(
				time.time(),
				"www.google.com",
				"10",
				result))
			f.flush()
