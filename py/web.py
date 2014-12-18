from abc import abstractmethod
import re
import router_module
import process
import config
import os

class WebHandler(object):
	@abstractmethod
	def handler(self, priv):
		pass

class WebMenuEntry(object):
	def __init__(self, category, name, path):
		self.category = category
		self.name = name
		self.path = path

	def get_urlized_name(self):
		retval = self.name
		retval = retval.lower()
		retval = re.sub('[^a-z]', '_', retval)

		return retval

class WebMenuModuleEntry(WebMenuEntry):
	def __init__(self, category, name, module, path):
		super(WebMenuModuleEntry, self).__init__(category, name, "/module/{0}/{1}".format(module, path))

class Web(router_module.RouterModule):
	
	menu = {
			"Monitoring" : {
				"Bandwidth chart": "#page_bandwidth_chart",
			},
			"Security" : {
				"Certificate Authority" : "#page_certificate_authority",
			},
			"Hack" : {
				"SSL Bump" : "#page_ssl_bump",
			},
		}

	modules = {}

	def brutal_stop(self):
		process.shell_command(self.get_context(), "killall apache2", ignoreResult=True)

	def start(self):
		conf = config.Config.get_config()

		static_dir = self.ctx.get_module_static_dir("web")

		apache_start = os.path.join(static_dir, "apache", "start")

		apache2_process = process.Process(
				self.get_context(),
				self,
				"apache2",
				"APACHE_BIND_ADDRESS={0} {1}".format(
					conf['lan_ip'],
					apache_start))
		apache2_process.start()


	@staticmethod
	def register_module_url(module, handler):
		Web.modules[module] = handler

	@staticmethod
	def module_url_handler(module, path):
		return Web.modules[module].handler(path)

	@staticmethod
	def add_menu_entry(entry):
		Web.menu[entry.category][entry.name] = entry

	@staticmethod
	def render_root_page():
		retval = ""
		retval += """
<!DOCTYPE html>
<html>

<head>
<link rel="stylesheet" type="text/css" href="style.css"/>

<link rel="stylesheet" href="//code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"/>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
<script src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/modules/exporting.js"></script>

<script>
$(document).ready(function(){	//executed after the page has loaded

    checkURL();	//check if the URL has a reference to a page and load it

    $('ul li a').click(function (e){	//traverse through all our navigation links..

            checkURL(this.hash);	//.. and assign them a new onclick event, using their own hash as a parameter (#page1 for example)

    });

    setInterval("checkURL()",250);	//check for a change in the URL every 250 ms to detect if the history buttons have been used

});

var lasturl="";	//here we store the current URL hash

function checkURL(hash)
{
    if(!hash) hash=window.location.hash;	//if no parameter is provided, use the hash value from the current address

    if(hash != lasturl)	// if the hash value has changed
    {
        lasturl=hash;	//update the current hash
        loadPage(hash);	// and load the new page
    }
}

var anchorToUrl = new Object();
"""
		for c,item_list in Web.menu.iteritems():
			for i,v in item_list.iteritems():
				if type(v) is str:
					continue
				retval += """anchorToUrl['{0}'] = '{1}'""".format(v.get_urlized_name(), v.path)

		retval += """

function loadPage(url)	//the function that loads pages via AJAX
{
    $(document).trigger("prechangepane");
    url=url.replace('#page_','');	//strip the #page part of the hash and leave only the page number

    if (url in anchorToUrl) {
        url = anchorToUrl[url];
    } else {
        url = "content_" + url
    }

    $('#loading').css('visibility','visible');	//show the rotating gif animation

    $.ajax({	//create an ajax request to load_page.php
        type: "GET",
        url: url,
        dataType: "html",	//expect html to be returned
        success: function(msg){

            if(parseInt(msg)!=0)	//if no errors
            {
                $('#pageContent').html(msg);	//load the returned html into pageContet
                $('#loading').css('visibility','hidden');	//and hide the rotating gif
            }
        }

    });

}
</script>
</head>

<body>
<ul id="vmenu">
"""
		for c,item_list in Web.menu.iteritems():
			retval += """<li class="menu_category">{0}</li>\n""".format(c)
			for i,v in item_list.iteritems():
				if type(v) is str:
					retval += """<li class="menu_item"><a href="{1}">{0}</a></li>""".format(i, v)
				else:
					retval += """<li class="menu_item"><a href="#page_{1}">{0}</a></li>""".format(i, v.get_urlized_name())

		retval += """
</ul>

<div id="pageContent"> <!-- this is where our AJAX-ed content goes -->
Hello, this is the default content
</div>

</div>

</body>
</html>
"""
		return retval
