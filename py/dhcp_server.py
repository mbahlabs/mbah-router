import config_file_out
import process
import config
import router_module
import subprocess

class DhcpServer(router_module.RouterModule):
	def __init__(self, ctx):
		self.config_file = config_file_out.ConfigFileOut(ctx, "dhcpd.conf")
		
		preamble = """
subnet 192.168.1.0 netmask 255.255.255.0 {
	option routers                  192.168.1.1;
	option subnet-mask              255.255.255.0;

#	option domain-name              "example.com";
	option domain-name-servers       8.8.8.8, 8.8.4.4;

#	option time-offset              -18000;     # Eastern Standard Time

	range 192.168.1.100 192.168.1.200;

"""

		self.config_file.append(preamble)

		conf = config.Config.get_config()

		for h in conf['static_hosts']:
			frag = ("\thost {name} {{\n" +
				"\t\thardware ethernet {mac};\n" +
				"\t\tfixed-address {ip};\n" +
				"\t}}\n").format(**h)
			self.config_file.append(frag)

		self.config_file.append("}\n")

		router_module.RouterModule.__init__(self, ctx)

	def brutal_stop(self):
		process.shell_command(self.get_context(), "killall dhcpd", ignoreResult=True)

	def start(self):
		conf = config.Config.get_config()
		self.dhcpd_process = process.Process(self.get_context(), self, "dhcpd", "dhcpd -f -cf {1} {0}".format(conf["lan_if"], self.config_file.get_location()))
		self.dhcpd_process.start()
