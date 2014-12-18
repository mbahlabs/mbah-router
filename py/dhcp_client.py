import config_file_out
import process
import config
import router_module
import subprocess

config_file_body = """
request routers, subnet-mask, broadcast-address, time-offset, interface-mtu, ntp-servers;
"""

class DhcpClient(router_module.RouterModule):
	def __init__(self, ctx):
		self.config_file = config_file_out.ConfigFileOut(ctx, "dhclient.conf")
		
		conf = config.Config.get_config()

		self.config_file.append(config_file_body.format(**conf))

		router_module.RouterModule.__init__(self, ctx)

	def brutal_stop(self):
		process.shell_command(self.get_context(), "killall dhclient", ignoreResult=True)

	def start(self):
		conf = config.Config.get_config()
		self.process = process.Process(self.get_context(), self, "dhclient", "dhclient -d -cf {} {}".format(self.config_file.get_location(), conf["wan_if"]))
		self.process.start()
