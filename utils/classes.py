#!/usr/bin/env python
from time import sleep
from utils.colors import colors as c
import requests
import json
import socket

class target():
	def __init__(self, email):
		self.headers = {
			'User-Agent': 'h8mail-v.1.0 OSINT and Education Tool'}
		self.email = email
		self.pwnd = False
		self.data = [()]

	def make_request(self, url, meth="GET", timeout=30, redirs=True, data=None, params=None):
		try:
			response = requests.request(url=url, headers=self.headers, method=meth, timeout=timeout, allow_redirects=redirs, data=data, params=params)
			if response.status_code == 404:
				print("Got a 404, retrying just to be sure")
				response = requests.request(url=url, headers=self.headers, method=meth, timeout=timeout, allow_redirects=redirs, data=data, params=params)
				# print(response.content)
				# print("---")
				# print(response.raw)
		except Exception as ex:
			c.bad_news(c, "Request could not be made for "+ self.email)
			print(ex)
			print(response)
		if response.status_code == 429:
			c.info_news(c, "Reached RATE LIMIT, sleeping")
			sleep(2.5)

		return response

	def get_hibp(self):
		sleep(1.3)
		url = "https://haveibeenpwned.com/api/v2/breachedaccount/{}?truncateResponse=true".format(self.email)
		response = self.make_request(url)
		if response.status_code not in [200, 404]:
			c.bad_news(c, "Could not contact HIBP for " + self.email)
			print(response.status_code)
			return

		if response.status_code == 200:
			self.pwnd = True
			data = response.json()
			for d in data:  # Returned type is a dict of Name : Service
				for _, ser in d.items():
					self.data.append(("HIBP_PWNED_SRC", ser))
			
			c.good_news(c, "Found {num} breaches for {target}".format(num=len(self.data)-1, target=self.email))

		elif response.status_code == 404:
			c.info_news(c, "No breaches found for {} using HIBP".format(self.email))
			self.pwnd = False
		else:
			c.bad_news(c, "HIBP: got API response code {code} for {target}".format(code=response.status_code, target=self.email))
			self.pwnd = False

	
	def get_hunterio_public(self):
		try:
			target_domain = self.email.split("@")[1]
			url = "https://api.hunter.io/v2/email-count?domain={}".format(target_domain)
			req = self.make_request(url)
			response = req.json()
			if response["data"]["total"] != 0:
				self.data.append(("HUNTER_PUB", response["data"]["total"]))
		except Exception as ex:
			c.bad_news(c, "HunterIO (pubic API) error: " + self.email)
			print(ex)

	# def get_hunterio_private(self, api_key):
	# 	try:
	# 		ui.debug(self.email, "Getting HunterIO private data on domain")
	# 		url = "https://api.hunter.io/v2/domain-search?domain={target}&api_key={key}".format(target=self.hostname, key=api_key)
	# 		req = self.make_request(url, cf=True)
	# 		response = req.json()
	# 		for e in response["data"]["emails"]:
	# 			self.hunterio_mails.append(e["value"])
	# 	except Exception as ex:
	# 		ui.warning(ui.yellow, "HunterIO (private API) error:", self.email, ex, url)

	# def get_snusbase(self, api_url, api_key):
	# 	try:
	# 		ui.debug(self.email, "Getting snusbase data")
	# 		url = api_url
	# 		self.headers.update({"Authorization": api_key})
	# 		payload = {"type": "email", "term": self.email}
	# 		req = self.make_request(url, cf=False, meth="POST", data=payload)
	# 		response = req.json()
	# 		for result in response["result"]:
	# 			if result["password"]:
	# 				ui.debug(self.email, ":", result["password"])
	# 				self.snusbase_passw.append(result["password"])
	# 			if result["hash"]:
	# 				ui.debug(self.email, ": hash found")
	# 				self.snusbase_hash_salt.update({result["hash"]: result["salt"]})
	# 			if result["tablenr"]:
	# 				if result["tablenr"] not in self.services["snusbase"]:
	# 					self.services["snusbase"].append(result["tablenr"])


	# 	except Exception as ex:
	# 		ui.warning(ui.yellow, "Snusbase error:", self.email, ex)

	# def get_proxies(self):
	# 	import proxify
	# 	proxies = proxify.get(20)
	# 	proto = "http"
	# 	self.proxies = zip(proto, proxies)  # Should make a dict of {"http":"http://ip:port"} UNTESTED
