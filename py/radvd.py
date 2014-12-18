import config_file_out
import process
import config
import router_module
import subprocess
import os

class Radvd(router_module.RouterModule):
	def __init__(self, ctx):
		router_module.RouterModule.__init__(self, ctx)

		conf = config.Config.get_config()

		self.config_file = config_file_out.ConfigFileOut(ctx, "radvd.conf")

		self.config_file.append(
			("interface {} {{" +
			"	AdvSendAdvert on;" +
			"	prefix ::/64" +
			"	{{" +
			"		AdvOnLink on;" +
			"		AdvAutonomous on;" +
			"	}};" +
			"	RDNSS 2001:4860:4860::8888 2001:4860:4860::8844" +
			"	{{" +
			"	}};" +
			"}};").format(conf['lan_if'])
		)



	def brutal_stop(self):
		process.shell_command(self.ctx, "killall radvd", ignoreResult=True)

	def start(self):
		radvd = process.Process(
				self.get_context(),
				self,
				"radvd",
				"radvd -d 1 -C {0}".format(self.config_file.get_location()))
		radvd.start()
