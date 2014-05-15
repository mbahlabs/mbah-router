import config_file_out
import process
import config
import router_module
import subprocess
import timeout
import time

class Dhcp6Client(router_module.RouterModule):
	def __init__(self, ctx):
		self.config_file = config_file_out.ConfigFileOut(ctx, "dhcp6c.conf")
		
		conf = config.Config.get_config()

		self.config_file.append((
			"interface {wan_if} {{\n" +
			"	send ia-pd 0;\n" +
			"	send ia-na 0;\n" +
			"}};\n" +
			"\n" +
			"id-assoc na 0 {{}};\n" +
			"\n" +
			"id-assoc pd {{\n" +
			"	prefix-interface {lan_if} {{\n" +
			"		sla-id 1;\n" +
			"		sla-len 0;\n" +
			"	}};\n" +
			"}};\n").format(**conf)
		)

		router_module.RouterModule.__init__(self, ctx)

	def brutal_stop(self):
		process.shell_command(self.get_context(), "killall dhcp6c", ignoreResult=True)

	def is_interface_up(self, iface):
		if process.shell_command(self.get_context(), "ip addr show dev eth0 | grep ,UP,", ignoreResult=True)['returncode'] == 0:
			return True
		else:
			return False


	def start(self):
		conf = config.Config.get_config()

		# First, need to wait for the interface to be up
		t = timeout.Timeout(10)

		while True:
			if self.is_interface_up(conf["wan_if"]):
				break

			if t.is_expired():
				raise RuntimeError("Timed out waiting for interface to come up")

			print "Waiting for interface to come up..."
			time.sleep(1)

		conf = config.Config.get_config()
		self.dhcpd_process = process.Process(self.get_context(), "dhcp6c", "dhcp6c -f -c {} {}".format(self.config_file.get_location(), conf["wan_if"]))
		self.dhcpd_process.start()
