from module import Module
import os
from execution_context import ExecutionContext
import re
import time
from web import Web
from web import WebMenuModuleEntry
from web import WebHandler
import cherrypy


class ConnectionQualityWebHandler(WebHandler):
	def __init__(self, module, ping_csv_path):
		self.module = module
		self.ping_csv_path= ping_csv_path

	def handler(self, path):
		if path == "ping.csv":
			cherrypy.response.headers['Content-Type'] = "text/csv"
			with open(self.ping_csv_path, 'r') as content_file:
				# Seek to end of file
				content_file.seek(0, 2)
				# Get file size
				file_size = content_file.tell()
				# Rewind
				target_location = file_size - 1000000
				if target_location < 0:
					target_location = 0
				content_file.seek(target_location, 0)
				# Skip the partial line we are on
				content_file.readline()
				# Read the rest
				content = content_file.read()
			return content
		elif path == "panel.html":
			return self.module.panel_html()
		else:
			return None


class ConnectionQuality(Module):
	def __init__(self, web, exectx, req):
		super(ConnectionQuality, self).__init__(exectx)

		#dir = exectx.get_permanent_storage_dir()
		dir = "/home/router/mbah-router/storage/pinger"
		path = os.path.join(dir, "ping.csv")
		self.ping_csv_path = os.path.join(dir, "ping.csv")

		self.web_handler = ConnectionQualityWebHandler(self, self.ping_csv_path)

		entry = WebMenuModuleEntry("Monitoring", "Connection Quality", "connection_quality", "panel.html")
		web.add_menu_entry(entry)

		web.register_module_url("connection_quality", self.web_handler)
		#self.start_daemon()

	def panel_html(self):
		retval = '''
<script>
$(function () {
        $('#container').highcharts({
            chart: {
		type: 'scatter',
                zoomType: 'x',
            },
            title: {
                text: 'Percentage dropped packets in a ping test'
            },
            subtitle: {
                //text: 'Irregular time data in Highcharts JS'
            },
            xAxis: {
                type: 'datetime',
            },
            yAxis: {
                title: {
                    text: 'Probes lost (%)'
                },
                min: 0,
		max: 100
            },
            legend: {
                enabled: false,
            },
            tooltip: {
                formatter: function() {
                        return '<b>'+ this.series.name +'</b><br/>'+
                        Highcharts.dateFormat('%Y/%m/%d %H:%M:%S', this.x) +': '+ this.y +'% probes lost';
                },
		    valueDecimals: 0,
		    valueSuffix: "% lost",
            },

            series: [{
                name: "Packets lost",
                turboThreshold: 150000,
                color: 'rgba(223, 83, 83, .1)',
                data: (function() {

			var dataout = [];
			data = $.ajax({async: false, url: "/module/connection_quality/ping.csv"}).responseText;
                        lines = data.split("\\n");

			var xsum = 0;
			var ysum = 0;
			var points = 0;

                        for (i = 0; i < lines.length; ++i) {
                            l = lines[i];
                            fields = l.split(",");
                            if (fields.length < 3) {
                                continue;
                            }

                            probeCount = parseInt(fields[2]);
                            failedProbes = parseInt(fields[3]);
                            x = fields[0]*1000;
                            y = failedProbes;

                            xsum += x;
                            ysum += y;
                            points++;
                            if (points == 5) {
                                x = xsum / points;
                                y = ysum / points;
				xsum = 0;
				ysum = 0;
				points = 0;
                            } else {
				continue;
			    }

                            if (y == 0) {
                                color = 'rgba(0, 0, 255, .1)'
                            } else {
                                color = 'rgba(255, 0, 0, .1)'
                            }

                            dataout.push({
                                x: x,
                                y: y,
                                color: color
                            });
                        }
			return dataout;

                })()
            }]
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

<div id="container" style="min-width: 500px; height: 400px; margin: 0 auto"></div>
'''
		return retval


	def start_daemon(self):
		result = os.fork()
		if result != 0:
			# inside parent
			return

		# inside child

		self.daemon()

	def daemon(self):
		exectx = self.get_exectx()

		f = open(self.ping_csv_path, "a")

		while 1:
			(time_ms, probes, successes) = self.ping()
			f.write("{0},{1},{2}\n".format(int(time_ms), probes, successes))
			f.flush()
			time.sleep(60)

	def ping(self):
		cmd = ['ping', '-q', '-c', '50', '-i', '0.2', 'www.google.com']
		(result, stdout, stderr) = ExecutionContext.run_cmd_output(cmd)
		# FIXME handle error
		lines = stdout.split('\n')
		for l in lines:
			if l.find("transmitted") == -1:
				continue
			numbers = re.split('[^0-9]+', l)
			break

		print 'Got {0} pings back out of {1} ({2})'.format(numbers[1], numbers[0], numbers)
		return (time.time()*1000, numbers[1], numbers[0])
