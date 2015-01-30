from mod_python import apache
import os

def handler(req):
	req.content_type = "text/plain"
	path = os.path.basename(req.filename)
	req.write(path)

	return apache.OK
