import config_file_out
import process
import config
import router_module
import subprocess
import os

class Rdiscd(router_module.RouterModule):
	def __init__(self, ctx):
		router_module.RouterModule.__init__(self, ctx)

	def brutal_stop(self):
		process.shell_command(self.ctx, "killall rdiscd", ignoreResult=True)

	def start(self):
		conf = config.Config.get_config()

		wan_if = conf["wan_if"]
		legacy_bin_dir = self.get_context().get_legacy_bin_dir()
		rdiscd_path = os.path.join(legacy_bin_dir, "rdiscd")

		rdiscd = process.Process(
				self.get_context(),
				self,
				"rdiscd",
				"{0} {1} 60".format(
					rdiscd_path,
					conf.get("wan_if")))
		rdiscd.start()
