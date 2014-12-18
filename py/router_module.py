class RouterModule:
	def __init__(self, ctx):
		self.ctx = ctx
		self.processes = []

	def start(self):
		pass

	def stop(self):
		pass

	def brutal_stop(self):
		pass

	def get_context(self):
		return self.ctx

	def register_process(self, process):
		self.processes.append(process)

	def check_health(self):
		for p in self.processes:
			if not p.is_alive():
				self.ctx.log("Process {} has unexpectedly died; restarting".format(p.name()))
				#self.brutal_stop()
				# FIXME: should wait for the brutal stop to take effect
				#self.start()
			else:
				self.ctx.log("Process {} is still alive".format(p.name()))
