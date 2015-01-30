#!/usr/bin/python

import cherrypy
import os
import json
import time
import subprocess
from abc import abstractmethod
import imp
import sys
from execution_context import ExecutionContext
from web import Web
from mod_python import apache

scriptDir = os.path.dirname(os.path.realpath(__file__))
publicDataDir = os.path.join(scriptDir, "data_public")
loaded_modules = {}

config = {
	'squid_prefix': '/home/pmf/inst/squid',
}

def getConfig(key):
	global config
	return config[key]

def split_path(req, path):
	retval = []
	while True:
		(head, tail) = os.path.split(path)
		retval.insert(0, tail)

		if head == "" or head == "/":
			break

		path = head

	return retval

#class Router(object):
#	staticDataDir = os.path.join(
#		scriptDir,
#		"static")
#
#	class ModuleHandlerClass():
#		def __init__(self, router):
#			self.router = router
#
#		def default(self, module, path):
#			return self.router.module_handler(module, path)
#
#		default.exposed = True
#
#	def __init__(self):
#		self.svcSslBump = SslBumpService()
#		self.exectxSslBump = ExecutionContext("ssl_bump")
#
#	def _cp_dispatch(self, vpath):
#		if vpath[0] == "module":
#			vpath.pop(0)
#			cherrypy.request.params['module'] = vpath.pop(0)
#			cherrypy.request.params['path'] = "/".join(vpath)
#			vpath[:] = []
#			return self.ModuleHandlerClass(self)
#		else:
#			return None
#
#	def default(self):
#		print cherrypy.url()
#		return Web.render_root_page()
#	default.exposed = True
#
#	def netstats(self):
#		content = ""
#		jsonObj = {}
#		with open("/sys/class/net/eth1/statistics/rx_bytes", 'r') as content_file:
#			content = int(content_file.read())
#		jsonObj["date"] = time.time()
#		jsonObj["stat"] = content
#
#		return json.dumps(jsonObj)
#	netstats.exposed = True
#
#	def contrib(self):
#		pass
#	contrib._cp_config = {
#		'tools.staticdir.on': True,
#		'tools.staticdir.dir': os.path.join(staticDataDir, "contrib"),
#		'tools.staticdir.index': 'index.htm'
#	}
#	contrib.exposed = True
#
#	def data_public(self):
#		pass
#	data_public._cp_config = {
#		'tools.staticdir.on': True,
#		'tools.staticdir.dir': publicDataDir,
#		'tools.staticdir.content_types': {'der': 'application/x-x509-ca-cert'},
#	}
#	data_public.exposed = True
#
#	def chart(self):
#		return renderChartPage()
#	chart.exposed = True
#
#	def content_bandwidth_chart(self):
#		return contentBandwidthChart()
#	content_bandwidth_chart.exposed = True
#
#	def content_certificate_authority(self):
#		return contentCertificateAuthority()
#	content_certificate_authority.exposed = True
#
#	def content_ssl_bump(self):
#		return contentSslBump(self)
#	content_ssl_bump.exposed = True
#
#	def style_css(self):
#		cherrypy.response.headers['Content-Type'] = 'text/css'
#		return getStylesheet()
#	style_css.exposed = True
#
#	def ca_auth_create(self, c, st, l, o, cn):
#		caAuthCreate(c, st, l, o, cn)
#	ca_auth_create.exposed = True
#
#	def service_start(self, svc):
#		self.serviceStart(svc)
#	service_start.exposed = True
#
#	def service_stop(self, svc):
#		self.serviceStop(svc)
#	service_stop.exposed = True
#
#	def service_status(self, svc):
#		self.serviceStatus(svc)
#	service_status.exposed = True
#
#
#	def serviceStart(self, svc):
#		self.svcSslBump.start(self.exectxSslBump)
#	def serviceStop(self, svc):
#		self.svcSslBump.stop(self.exectxSslBump)
#	def serviceStatus(self, svc):
#		self.svcSslBump.status(self.exectxSslBump)
#
#	def module_handler(self, module, path):
#		return Web.module_url_handler(module, path)
#
class Service:
	@abstractmethod
	def name(self):
		pass

	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def stop(self):
		pass

	@abstractmethod
	def status(self):
		pass

class SslBumpService(Service):
	squidExecutable = os.path.join(getConfig("squid_prefix"), "sbin/squid")
	sslCrtdExecutable = os.path.join(getConfig("squid_prefix"), "libexec/ssl_crtd")

	def __init__(self):
		# Path to the squid.conf file
		self.configFilePath = ""
		# Path to the ssl certificate database
		self.ssl_db_dir = ""
		self.daemon = None

	def name(self):
		return "ssl_bump"

	def initializeConfig(self, exectx):
		dir = exectx.getTempDir()
		self.configFilePath = os.path.join(dir, "squid.conf")
		self.ssl_db_dir = os.path.join(dir, "ssl_db")

		# Initialize ssl db dir
		if runCmd([SslBumpService.sslCrtdExecutable, '-c', '-s', self.ssl_db_dir]) != 0:
			raise RuntimeError("Failed to initialize config")

		self.writeSquidConfig(self.configFilePath)


	def start(self, exectx):
		self.initializeConfig(exectx)

		cmd = [SslBumpService.squidExecutable, "-f", self.configFilePath, "-N"]
		self.daemon = exectx.startDaemon("squid", cmd)

	def stop(self):
		exectx.stopDaemon("squid")

	def status(self):
		if not self.daemon:
			return False
		if self.daemon.poll() == None:
			return True
		else:
			return False

	def writeSquidConfig(self, filename):
		text = """
http_port 192.168.1.1:3128 ssl-bump generate-host-certificates=on dynamic_cert_mem_cache_size=4MB cert={combined_certificate}

always_direct allow all
ssl_bump server-first all
# the following two options are unsafe and not always necessary:
#sslproxy_cert_error deny all
#sslproxy_flags DONT_VERIFY_PEER

sslcrtd_program {ssl_crtd_executable} -s {ssl_db_dir} -M 4MB
sslcrtd_children 5

http_access allow all

access_log stdio:/tmp/access.log all
""".format(combined_certificate=caAuthCombinedPath, ssl_db_dir=self.ssl_db_dir, ssl_crtd_executable=SslBumpService.sslCrtdExecutable)
		with open(filename, 'w') as f:
			f.write(text)


caAuthKeyPath = os.path.join(scriptDir, "data", "root-ca.key")
caAuthCrtPath = os.path.join(scriptDir, "data_public", "root-ca.crt")
caAuthCrtDerPath = os.path.join(scriptDir, "data_public", "root-ca.der")
caAuthCombinedPath = os.path.join(scriptDir, "data", "root-ca.combined.pem")

def runCmd(cmd):
	ExecutionContext.run_cmd(cmd)

def mkdirsForFile(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

def fileText(f):
	with open(f, 'r') as content_file:
		content = content_file.read()

	return content

def caAuthCreate(c, st, l, o, cn):
#	mkdirsForFile(caAuthKeyPath)
#	mkdirsForFile(caAuthCrtPath)
#
#	cmd = [
#		"openssl",
#		"req",
#		"-new",
#		"-newkey",
#		"rsa:1024",
#		"-x509",
#		"-days",
#		"3650",
#		"-subj",
#		"/C={0}/ST={1}/L={2}/O={3}/CN={4}".format(c, st, l, o, cn), # FIXME injection
#		"-keyout",
#		"{0}".format(caAuthKeyPath),
#		"-out",
#		"{0}".format(caAuthCrtPath) ]



	mkdirsForFile(caAuthKeyPath)

	# Create key
	cmd = [
		"openssl",
		"genrsa",
		"-out",
		"{0}".format(caAuthKeyPath),
		"2048" ]
	cherrypy.log(str(cmd))
	runCmd(cmd)

	mkdirsForFile(caAuthCrtPath)

	# Self-sign key
	cmd = [
		"openssl",
		"req",
		"-new",
		"-x509",
		"-days",
		"3650",
		"-subj",
		"/C={0}/ST={1}/L={2}/O={3}/CN={4}".format(c, st, l, o, cn),
		"-key",
		"{0}".format(caAuthKeyPath),
		"-out",
		"{0}".format(caAuthCrtPath) ]

	cherrypy.log(str(cmd))
	runCmd(cmd)

	mkdirsForFile(caAuthCrtDerPath)

	# Export to DER format for web browsers
	cmd = [
		"openssl",
		"x509",
		"-in",
		"{0}".format(caAuthCrtPath),
		"-outform",
		"DER",
		"-out",
		"{0}".format(caAuthCrtDerPath) ]

	cherrypy.log(str(cmd))
	runCmd(cmd)

	# Make combined PEM private key and certificate, for Squid SSL bump
	mkdirsForFile(caAuthCombinedPath)

	privateKey = fileText(caAuthKeyPath)
	certificate = fileText(caAuthCrtPath)

	with open(caAuthCombinedPath, 'w') as f:
		f.write(privateKey)
		f.write(certificate)

def getStylesheet():
	return """
body {
   font-family: helvetica;
}

ul#vmenu {
   margin: 0;
   padding: 0;
   list-style: none;
   float: left;

}

ul#vmenu a:link {
    text-decoration:none;
    color: black;
}
ul#vmenu a:visited {
    text-decoration:none;
    color: black;
}
ul#vmenu a:hover {
    text-decoration:none;
    color: black;
}
ul#vmenu a:active {
    text-decoration:none;
    color: black;
}

ul#vmenu li.menu_category {
   margin: 0;
   padding: 0;
   list-style: none;
   font-weight: bold;
   margin-top: 1em;
}

ul#vmenu li.menu_item {
   margin: 0;
   padding-left: 10;
   list-style: none;
   font-size: 12px;
}

div#pageContent {
   float: left;
   margin-top: 30px;
   margin-left: 30px;
}

"""


def contentCertificateAuthority():
	page = """

<script>
function submitForm()
{
	$.get("ca_auth_create?" + $('#ca_form').serialize());
}
</script>

<div>Download local certificate authority <a href="data_public/root-ca.crt">[PEM]</a> <a href="data_public/root-ca.der">[DER]</a></div>

<h2>Create certificate authority</h2>
<form id="ca_form">
<table>
  <tr><td>Country (2 letter code):</td><td><input name="c" type="text"/></td></tr>
  <tr><td>State/Province:</td><td><input name="st" type="text"/></td></tr>
  <tr><td>Locality (city):</td><td><input name="l" type="text"/></td></tr>
  <tr><td>Organization (company):</td><td><input name="o" type="text"/></td></tr>
  <tr><td>Common name (hostname):</td><td><input name="cn" type="text"/></td></tr>
</table>
</form>
<button onclick="submitForm()">Create...</button>
"""
	return page

def serviceHtmlControlUI(svc):
	url = "/service_start?svc=ssl_bump"
	text = """
<script>
  $(function() {{
    $( "button" )
      .button()
      .click(function( event ) {{
	$.post("{url}", function (data) {{ }});
        event.preventDefault();
      }});
  }});
</script>
<div>{svc_name} [{status}] <button>start</button></div>
""".format(svc_name=svc.name(), status=svc.status(), url=url)
	return text

def contentSslBump(router):
	page = serviceHtmlControlUI(router.svcSslBump)
	return page

def contentBandwidthChart():
	page = """

<div id="container"></div>
<script>

$(function () {
    var lastTimestampSec;
    var lastTransferredBytes;
    var lastSet = false;
    var pointCount = 0;

    var intervalHandler;

    var chart = $('#container').highcharts({
        chart: {
            reflow: false,
            events: {
                load: function() {
                    // set up the updating of the chart each second
                    var series = this.series[0];
                    intervalHandler = setInterval(function() {
                        $.ajax({
                            url: "/netstats",
			})
                            .done(function(data) {
				jsonObj = JSON.parse(data);
                                var timestampSec = jsonObj.date;
                                var transferredBytes = jsonObj.stat;
				if (!lastSet) {
					lastTimestampSec = timestampSec;
					lastTransferredBytes = transferredBytes;
					lastSet = true;
					return;
				}

				dy = transferredBytes - lastTransferredBytes;
				dx = timestampSec - lastTimestampSec;
				val = dy/dx;

				lastTransferredBytes = transferredBytes;
				lastTimestampSec = timestampSec;
				var evictOldestPoint = ++pointCount > 100;
                                series.addPoint([timestampSec*1000, val], true, evictOldestPoint);
                            });
                    }, 1000);
                }
            }
        },
        title: {
            text: 'Bandwidth usage over time'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Bandwidth (bytes/s)'
            },
            min: 0,
        },
        legend: {
            enabled: false,
        },
        tooltip: {
            valueDecimals: 0,
            valueSuffix: " bytes/s",
        },

        series: [{
            type: "area",
	    name: "Bandwidth",
            data: [],
        }],
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },
                    lineWidth: 1,
                    marker: {
                        enabled: false
                    },
                    shadow: false,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                }
            },
    });

    $(document).on("prechangepane", function(){
       clearInterval(intervalHandler);
    });

    function chartResize() {
        var width = $(window).width() - 200;
        var height = $(window).height() - 60;
        $("#container").css("width", width);
        $("#container").css("height", height);
        $('#container').highcharts().setSize(width,height);
    }

    $(window).bind("resize", chartResize);
});

</script>

"""
	return page

def handler(req):
	web = Web()
	load_modules(web, req)
	#raise RuntimeError("heha-1! have {0} entries".format(str(Web.menu["Monitoring"])))

	path_components = split_path(req, req.uri)

	req.content_type = "text/html"

	if path_components[0] == "":
		req.write(web.render_root_page(req))
	elif req.uri == "/style.css":
		req.content_type = "text/css"
		req.write(getStylesheet())
	elif req.uri == "/content_bandwidth_chart":
		req.write(contentBandwidthChart())
	elif path_components[0] == "module":
		text = web.module_url_handler(path_components[1], "/".join(path_components[2:]))
		req.write(text)

	elif req.uri == "/netstats":
		#req.content_type = "text/json"
		content = ""
		jsonObj = {}
		with open("/sys/class/net/eth1/statistics/rx_bytes", 'r') as content_file:
			content = int(content_file.read())
		jsonObj["date"] = time.time()
		jsonObj["stat"] = content

		req.write(json.dumps(jsonObj))

	else:
		req.write(str(path_components))

	return apache.OK

def load_modules(web, req):
	module_dir = os.path.join(scriptDir, "module")
	ls = os.listdir(module_dir)
	sys.path.append(scriptDir)
	for f in ls:
		full_path = os.path.join(module_dir, f)
		mod_name,file_ext = os.path.splitext(os.path.split(f)[-1])
		if file_ext != ".py":
			continue
		(file, pathname, description) = imp.find_module(mod_name, [module_dir])
		mod = imp.load_module(mod_name, file, pathname, description)
		class_ = getattr(mod, mod_name)
		instance = class_(web, ExecutionContext(mod_name), req)
		global loaded_modules
		loaded_modules[mod_name] = instance

#load_modules()
