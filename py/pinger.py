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

	def ping_loss_test(self, target, count, interv):
		ping_result = process.shell_command(self.ctx,
			"ping -n -q -i {} -c {} {}".format(interv, count, target), ignoreResult=True)

		if ping_result['returncode'] != 0:
			self.ctx.log("ping returned code {0} stderr {1}".format(ping_result['returncode'], ping_result['stderr']))
			return None

		grep_result = process.shell_command(self.ctx,
			"egrep -o '[0-9]{1,3}% packet loss' | cut -d '%' -f 1", input=ping_result["stdout"]+"\x04")

		if grep_result['returncode'] != 0:
			self.ctx.log("grep returned code {0} with stderr {1}".format(grep_result['returncode'], grep_result['stderr']))
			return None

		return int(grep_result['stdout'].rstrip())

	def run(self):
		f = self.ctx.open_persistent_file("pinger", "ping.csv", "a")

		while True:
			result = self.ping_loss_test("www.google.com", 10, 0.2)
			time.sleep(15)

			f.write("{},{},{},{}\n".format(
				time.time(),
				"www.google.com",
				"10",
				result))
			f.flush()

	@staticmethod
	def get_last_lost(ctx):
		try:
			with ctx.open_persistent_file("pinger", "ping.csv", "r") as fh:
				fh.seek(-1024, 2)
				last = fh.readlines()[-1].decode()
				last = last.rstrip()

				fields = last.split(",")

				ts = float(fields[0])
				ts_diff = time.time() - ts
				if ts_diff < 0 or ts_diff > 60:
					return None

				last_lost = int(fields[3])

				return last_lost
		except:
			return None
