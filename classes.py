#!/usr/bin/env python
from time import sleep

import requests
import ui
import json
import socket


class Target():
	def __init__(self, email):
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136'}
		self.email = email
		self.pwnd = ""
		self.breachcomp_passw = []
		self.snusbase_passw = []
		self.snusbase_hash_salt = {}
		self.hostname = self.email.split("@")[1]
		self.rev_dns = []
		self.rev_ports = []
		self.related_emails = []
		self.hunterio_mails = []
		self.services = {"hibp": [], "weleakinfo": []}  # todo snusbase services + print
		self.ip = ""


	def make_request(self, url, cf=False, meth="GET", timeout=30, redirs=True, data=None, params=None):
		if cf is False:
			try:
				response = requests.request(url=url, headers=self.headers, method=meth, timeout=timeout, allow_redirects=redirs, data=data, params=params)
				ui.debug(ui.purple, "REQUEST", response.url, ui.bold, response.status_code)

			except Exception as ex:
				ui.error("Request could not be made for", self.email, ex)
		else:  # cf is True
			try:
				import cfscrape
				scraper = cfscrape.create_scraper()
				response = scraper.get(url)
			except Exception as ex:
				ui.error("Cloudflare bypass request could not be made for", self.email, ex)

		if response.status_code == 429:
			ui.warning("Reached RATE LIMIT, sleeping", ui.purple, self.email)
			sleep(2.5)
		return response

	def get_shodan(self, api_key):
		try:
			self.ip = socket.gethostbyname(self.hostname)
		except Exception as ex:
			ui.debug("Could not fetch host IP address", self.hostname, ex)

		if len(api_key) == 0:
			ui.debug(self.email, "Setting default Shodan API KEY")
			api_key = "UNmOjxeFS2mPA3kmzm1sZwC0XjaTTksy"  # From Infoga tool
		try:
			url = "https://api.shodan.io/shodan/host/{target}?key={key}".format(
				target=self.ip, key=api_key)
			response = self.make_request(url)
			data = json.loads(response.text)
			self.rev_ports.extend(data["ports"])
			self.rev_dns.extend(data["hostnames"])
		except Exception as ex:
			ui.warning(ui.yellow, "Shodan error for:", self.email, ex)

	def get_hibp(self):
		sleep(1.3)
		url = "https://haveibeenpwned.com/api/v2/breachedaccount/{}?truncateResponse=true".format(self.email)
		response = self.make_request(url)
		if response.status_code not in [200, 404]:
			ui.warning("Retrying HIBP with CF bypass for", self.email)
			response = self.make_request(url, cf=True)
			if response.status_code not in [200, 404]:
				ui.warning("Could not contact HIBP using CF bypass for", self.email )
				return

		if response.status_code == 200:
			self.pwnd = True
			data = response.json()
			for d in data:  # Returned type is a dict of Name : Service
				for name, ser in d.items():
					self.services["hibp"].append(ser)
			ui.debug(self.services["hibp"])

		elif response.status_code == 404:
			ui.debug(ui.bold, "HIBP:", ui.reset, ui.cross, "No breaches found for {}".format(self.email))
			self.pwnd = False
		else:
			ui.warning("HIBP: got API response code", response.status_code, "for", self.email)
			self.pwnd = False

		ui.debug(ui.bold, "HIBP:", ui.reset, "{} breaches found for {}".format(len(self.services["hibp"]), self.email))

	def get_weleakinfo_public(self):
		try:
			url = "https://api.weleakinfo.com/v2/public/email/{}".format(self.email)
			req = self.make_request(url, cf=True)
			response = req.json()
			if type(response["Unique"]) == str:  # if no breach returns an int(0) else str('X Websites')
				for d in response["Data"]:
					self.services["weleakinfo"].append(d)
				ui.debug(ui.bold, "WeLeakInfo:", ui.reset, "{} breaches found for {}".format(len(self.services["weleakinfo"]), self.email))
			else:
				ui.debug(ui.bold, "WeLeakInfo:", ui.reset, ui.cross, "No breaches found for {}".format(self.email))
				return
		except Exception as ex:
			ui.warning(ui.yellow, "WeLeakInfo (pubic API) error:", self.email, ex)

	def get_hunterio_public(self):
		try:
			ui.debug(self.email, "Getting HunterIO public data on domain")
			url = "https://api.hunter.io/v2/email-count?domain={}".format(self.hostname)
			req = self.make_request(url, cf=True)
			response = req.json()
			if response["data"]["total"] != 0:
				self.related_emails = response["data"]["total"]
		except Exception as ex:
			ui.warning(ui.yellow, "HunterIO (pubic API) error:", self.email, ex)

	def get_hunterio_private(self, api_key):
		try:
			ui.debug(self.email, "Getting HunterIO private data on domain")
			url = "https://api.hunter.io/v2/domain-search?domain={target}&api_key={key}".format(target=self.hostname, key=api_key)
			req = self.make_request(url, cf=True)
			response = req.json()
			for e in response["data"]["emails"]:
				self.hunterio_mails.append(e["value"])
		except Exception as ex:
			ui.warning(ui.yellow, "HunterIO (private API) error:", self.email, ex, url)

	def get_snusbase(self, api_url, api_key):
		try:
			ui.debug(self.email, "Getting snusbase data")
			url = api_url
			self.headers.update({"Authorization": api_key})
			payload = {"type": "email", "term": self.email}
			req = self.make_request(url, cf=False, meth="POST", data=payload)
			response = req.json()
			for result in response["result"]:
				if result["password"]:
					ui.debug(self.email, ":", result["password"])
					self.snusbase_passw.append(result["password"])
				if result["hash"]:
					ui.debug(self.email, ": hash found")
					self.snusbase_hash_salt.update({result["hash"]: result["salt"]})

		except Exception as ex:
			ui.warning(ui.yellow, "Snusbase error:", self.email, ex)

	# def get_proxies(self):
	# 	import proxify
	# 	proxies = proxify.get(20)
	# 	proto = "http"
	# 	self.proxies = zip(proto, proxies)  # Should make a dict of {"http":"http://ip:port"} UNTESTED
