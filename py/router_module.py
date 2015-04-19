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
				# don't want to check it anymore
				self.processes.remove(p)
				self.ctx.log("Process {} has unexpectedly died; restarting".format(p.name()))

				# We restart the whole module, which is a bit intense
				self.brutal_stop()
				self.start()
			else:
				self.ctx.log("Process {} is still alive".format(p.name()))
