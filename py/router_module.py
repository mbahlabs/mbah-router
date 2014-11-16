class RouterModule:
	def __init__(self, ctx):
		self.ctx = ctx

	def start(self):
		pass

	def stop(self):
		pass

	def brutal_stop(self):
		pass

	def get_context(self):
		return self.ctx
