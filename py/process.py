import subprocess
import os
import router_context
import time

def shell_command(ctx, cmd, **args):

	if not args.has_key("retries"):
		args["retries"] = 0

	if not args.has_key("input"):
		args["input"] = None
		stdinpipe = None
	else:
		stdinpipe = subprocess.PIPE

	tryno = 0

	while True:
		ctx.log("running command line '{}'".format(cmd))
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=stdinpipe, shell=True)

		(stdout, stderr) = proc.communicate(args["input"])

		if proc.returncode != 0:
			# if we have another chance, then let's just use it
			if tryno < args['retries']:
				tryno += 1
				time.sleep(1)
				continue

			# Otherwise deal with the error
			if not args.has_key('ignoreResult') or args['ignoreResult'] == False:
				ctx.log("command failed with code '{}'".format(proc.returncode))
				ctx.log("stderr is: {}".format(stderr))
				raise RuntimeError("Failed to execute command {0} (return code {1})".format(cmd, proc.returncode))
			else:
				break

		# If everything went well, end it
		break

	retval = {}
	retval['stdout'] = stdout
	retval['stderr'] = stderr
	retval['returncode'] = proc.returncode

	return retval

def killall_and_wait(name):
	process.shell_command(self.get_context(), "killall {}".format(name), ignoreResult=True)
	while True:
		pgrep_res = process.shell_command(self.get_context(), "pgrep {}".format(name), ignoreResult=True)
		if len(pgrep_res['stdout']) == 0:
			break
		time.sleep(1)

class Process:
	def __init__(self, ctx, module, name, args):
		self.ctx = ctx
		self._name = name
		self.args = args
		self.module = module
		self.process = None

	def start(self):
		log_dir = self.ctx.get_log_dir()
		stdout_file = os.path.join(log_dir, "{0}.stdout".format(self._name))
		stderr_file = os.path.join(log_dir, "{0}.stderr".format(self._name))

		stdout_hnd = open(stdout_file, "w")
		stderr_hnd = open(stderr_file, "w")

		self.ctx.log("running command line '{}'".format(self.args))

		self.process = subprocess.Popen(self.args, shell=True,
			stdin=None, stdout=stdout_hnd, stderr=stderr_hnd, close_fds=True)

		self.module.register_process(self)

	def stop(self):
		self.process.terminate()

	def is_alive(self):
		if self.process.poll() is None:
			return True
		else:
			return False

	def name(self):
		return self._name
