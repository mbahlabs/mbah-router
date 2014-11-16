import router_context
import os

class ConfigFileOut:
	def __init__(self, ctx, casual_name):
		config_file_dir = ctx.get_out_config_dir()
		self.full_path = os.path.join(config_file_dir, casual_name)
		if os.path.exists(self.full_path):
			raise RuntimeError("Config file already exists")
		self.fh = open(self.full_path, "w")

	def append(self, v):
		self.fh.write(v)
		self.fh.flush()

	def get_location(self):
		return self.full_path
