import shutil
import os
import errno

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def rm_rf(path):
	try:
		shutil.rmtree(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.ENOENT:
			pass
		else:
			raise
	

class RouterContext:

	def __init__(self):
		self.modules = []

		self.out_config_dir = "/tmp/router/config_out"
		self.log_dir = "/tmp/router/log"
		self.legacy_bin_dir = os.path.dirname(os.path.realpath(__file__))

		rm_rf("/tmp/router")

		mkdir_p(self.out_config_dir)

		# Delete and recreate log dir
		mkdir_p(self.log_dir)

		master_log_filename = os.path.join(self.log_dir, "log")
		self.master_log_file_fp = open(master_log_filename, "w")

	def get_out_config_dir(self):
		return self.out_config_dir

	def get_log_dir(self):
		return self.log_dir

	def get_legacy_bin_dir(self):
		return self.legacy_bin_dir

	def log(self, msg):
		self.master_log_file_fp.write(msg + "\n")
		self.master_log_file_fp.flush()

	def add_module(self, module):
		self.modules.append(module)

		module.brutal_stop()
		module.start()

	def open_persistent_file(self, module, file, mode):
		persistent_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "private")
		module_dir = os.path.join(persistent_dir, module)
		mkdir_p(module_dir)
		full_path = os.path.join(module_dir, file)

		return open(full_path, mode)

	def get_module_static_dir(self, module):
		static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "module_static", module)
		mkdir_p(static_dir)
		return static_dir

	def check_health(self):
		for m in self.modules:
			m.check_health()
