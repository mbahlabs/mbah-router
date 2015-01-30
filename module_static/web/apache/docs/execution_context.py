import tempfile
import subprocess
import os

class ExecutionContext(object):
	@staticmethod
	def get_app_root():
		return os.path.dirname(os.path.realpath(__file__))

	def __init__(self, label):
		self.label = label
		self.daemonProcesses = {}

	def label(self):
		return self.label

	def getTempDir(self):
		return tempfile.mkdtemp(suffix='', prefix='tmp-{0}'.format(self.label), dir="/tmp")

	def startDaemon(self, name, cmd):
		print "About to run " + str(cmd)
		p = subprocess.Popen(cmd)
		self.daemonProcesses[name] = p
		return p

	def stopDaemon(self, name):
		p = self.daemonProcesses[name]
		p.terminate()

	def get_permanent_storage_dir(self):
		retval = os.path.join(ExecutionContext.get_app_root(), "data", "module", self.label.lower())
		# Make sure dir exists
		if not os.path.isdir(retval):
			os.makedirs(retval)
		return retval

	@staticmethod
	def run_cmd_output(cmd):
		print "About to run command: {0}".format(cmd)
		p = subprocess.Popen(cmd, stdin=open("/dev/null", "r"), stdout=subprocess.PIPE)
		(out,err) = p.communicate()

		print str(err)

		return (p.returncode, out, err)

	@staticmethod
	def run_cmd(cmd):
		(code, out, err) = run_cmd_output(cmd)
		return code
