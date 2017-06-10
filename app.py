from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response
from woocommerce import API

# Falsk app should start in global layout
app = Flask(__name__)

wcapi = API(
	url = "https://dev.i-spy360.mu/woocommerce-chatbot/",
	consumer_key = "ck_b1d5aede2d327d994f3abac95945de0d3881fd9e",
	consumer_secret = "cs_980d7219d925bbd2ed75faafbd74ec59695153ed",
	wp_api = True,
	version = "wc/v2"
)

@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)
	
	print("Request:")
	print(json.dumps(req, indent=4))
	
	res = processRequest(req)
	
	res = json.dumps(res, indent=4)
	
	print("res:")
	print(res)
	
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	
	return r

def processRequest(req):
	
	if req.get("result").get("action") != "retrieveProduct":
		return {}
	
	data = makeJson(req)
	res = makeWebHookResult(data)
	print("res in processRequest")
	print(res)
	
	return res
	
def makeJson(req):
	result = req.get("result")
	parameters = result.get("parameters")
	goods = parameters.get("goods")
	
	if goods is None:
		return {}
	print("goods")
	print(type(goods))
	productResult = "products/" + goods
	data = wcapi.get(productResult).json()
	
	return data
	
def makeWebHookResult(data):
	name = data.get('name')
	if name is None:
		return {}
	
	permalink = data.get('permalink')
	if permalink is None:
		return {}
	
	price = data.get('price')
	if price is None:
		return {}
	
	speech = "We have " + data.get('name') + " and The price is $" + data.get('price') + " and The link to it is " + data.get('permalink')
	
	print("Responses")
	print(speech)
	
	
	return {
		"speech": speech,
		"displayText": speech,
		"source": "apiai-woocommerce"
	}

	
if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))
	
	print("Starting app on port %d" % port)
	
	app.run(debug=False, port=port, host='0.0.0.0')
