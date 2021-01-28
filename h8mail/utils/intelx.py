#!/usr/bin/env python3

import requests
import time
import json
import sys
import re

class intelx:

	# API_ROOT = 'https://public.intelx.io'
	API_ROOT = ''
	API_KEY  = ''
	USER_AGENT = ''

	# If an API key isn't supplied, it will use the free API key (limited functionality)
	def __init__(self, key="01a61412-7629-4288-b18a-b287266f2798", ua='IX-Python/0.5'):
		"""
		Initialize API by setting the API key.
		"""
		if key == "01a61412-7629-4288-b18a-b287266f2798" or key == "ac572eea-3902-4e9a-972d-f5996d76174c":
			self.API_ROOT 	= "https://public.intelx.io"
		else:
			self.API_ROOT 	= "https://2.intelx.io"

		self.API_KEY = key
		self.USER_AGENT = ua

	def get_error(self, code):
		"""
		Get error string by respective HTTP response code.
		"""
		if code == 200:
			return "200 | Success"
		if code == 204:
			return "204 | No Content"
		if code == 400:
			return "400 | Bad Request"
		if code == 401:
			return "401 | Unauthorized"
		if code == 402:
			return "402 | Payment required."
		if code == 404:
			return "404 | Not Found"

	def cleanup_treeview(self, treeview):
		"""
		Cleans up treeview output from the API.
		"""
		lines = []
		for line in treeview.split("\r\n"):
			if '<a href' not in line:
				lines.append(line)
		return lines
	
	def GET_CAPABILITIES(self):
		"""
		Return a JSON object with the current user's API capabilities
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(f"{self.API_ROOT}/authenticate/info", headers=h)
		return r.json()

	def FILE_PREVIEW(self, ctype, mediatype, format, sid, bucket='', e=0, lines=8):
		"""
		Show a preview of a file's contents based on its storageid (sid).
		format option:
		- 0: Text
		- 1: Picture
		"""
		r = requests.get(f"{self.API_ROOT}/file/preview?c={ctype}&m={mediatype}&f={format}&sid={sid}&b={bucket}&e={e}&l={lines}&k={self.API_KEY}")
		return r.text

	def FILE_VIEW(self, ctype, mediatype, sid, bucket='',escape=0):
		"""
		Show a file's contents based on its storageid (sid), convert to text where necessary.

		format option:
		- 0: textview of content
		- 1: hex view of content
		- 2: auto detect hex view or text view
		- 3: picture view
		- 4: not supported
		- 5: html inline view (sanitized)
		- 6: text view of pdf
		- 7: text view of html
		- 8: text view of word file
		"""
		format = 0
		if(mediatype==23 or mediatype==9):	# HTML
			format = 7
		elif(mediatype==15):				# PDF
			format = 6
		elif(mediatype==16):				# Word
			format = 8
		elif(mediatype==18):				# PowerPoint
			format = 10
		elif(mediatype==25):				# Ebook
			format = 11
		elif(mediatype==17):				# Excel
			format = 9
		elif(ctype==1):						# Text
			format = 0
		else:
			format = 1
		r = requests.get(f"{self.API_ROOT}/file/view?f={format}&storageid={sid}&bucket={bucket}&escape={escape}&k={self.API_KEY}")
		return r.text
	
	def FILE_READ(self, id, type=0, bucket="", filename=""):
		"""
		Read a file's raw contents. Use this for direct data download.

		id option:
		- Specifies the item's system ID to read.

		type option:
		- Specifies content disposition or not.
		- 0: No content disposition. Returns raw binary file.
		- 1: Content disposition. May fix line endings to CR LF for text files.

		bucket option:
		- Optional bucket value.

		name option:
		- Specify the name to save the file as (e.g document.pdf).
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(f"{self.API_ROOT}/file/read?type={type}&systemid={id}&bucket={bucket}", headers=h, stream=True)
		with open(f"{filename}", "wb") as f:
			f.write(r.content)
			f.close()
		return True

	def FILE_TREE_VIEW(self, sid):
		"""
		Show a treeview of an item that has multiple files/folders
		"""
		try:
			r = requests.get(f"{self.API_ROOT}/file/view?f=12&storageid={sid}&k={self.API_KEY}", timeout=5)
			if "Could not generate" in r.text:
				return False
			return r.text
		except:
			return False

	def INTEL_SEARCH(self, term, maxresults=100, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0, terminate=[]):
		"""
		Initialize an intelligent search and return the ID of the task/search for further processing.

		maxresults option:
		- Tells how many results to query maximum per bucket.
		- Example: maxresults=100

		buckets option:
		- Specify the buckets to search
		- Example: buckets=[]
		- Example: buckets=['pastes', 'darknet.i2p']

		timeout option:
		- Set a timeout value for the search.
		- Example: timeout=5

		datefrom option:
		- Set a starting date to begin the search from.
		- Example: 2020-01-01 00:00:00
		- Example: 2020-01-01 12:00:00

		dateto option:
		- Set an ending date to finish the search from.
		- Example: 2020-02-02 23:59:59
		- Example: 2020-02-02 00:00:00

		sort option:
		- Define the way to sort search results.
		- 0: No sorting.
		- 1: X-Score ASC. Least relevant items first.
		- 2: X-Score DESC. Most relevant items first.
		- 3: Date ASC. Oldest items first.
		- 4: Date DESC. Newest items first.

		media option:
		- Define the type of media to search for.
		- 0: Not set. (All media types)
		- 1: Paste document
		- 2: Paste User
		- 3: Forum
		- 4: Forum Board
		- 5: Forum Thread
		- 6: Forum Post
		- 7: Forum User
		- 8: Screenshot of a Website
		- 9: HTML copy of a website.
		- 10: Invalid, do not use.
		- 11: Invalid, do not use.
		- 12: Invalid, do not use.
		- 13: Tweet
		- 14: URL, high-level item having HTML copies as linked sub-items
		- 15: PDF document
		- 16: Word document
		- 17: Excel document
		- 18: Powerpoint document
		- 19: Picture
		- 20: Audio file
		- 21: Video file
		- 22: Container files including ZIP, RAR, TAR and others
		- 23: HTML file
		- 24: Text file

		The term must be a strong selector. These selector types are currently supported:
		- Email address
		- Domain, including wildcards like *.example.com
		- URL
		- IPv4 & IPv6
		- CIDRv4 & CIDRv6
		- Phone Number
		- Bitcoin Address
		- MAC Address
		- IPFS Hash
		- UUID
		- Storage ID
		- System ID
		- Simhash
		- Credit card number
		- IBAN

		Soft selectors (generic terms) are not supported!
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		p = {
			"term": term,
			"buckets": buckets,
			"lookuplevel": 0,
			"maxresults": maxresults,
			"timeout": timeout,
			"datefrom": datefrom,
			"dateto": dateto,
			"sort": sort,
			"media": media,
			"terminate": terminate
		}
		r = requests.post(self.API_ROOT + '/intelligent/search', headers=h, json=p)
		if r.status_code == 200:
			return r.json()['id']
		else:
			return r.status_code

	def INTEL_SEARCH_RESULT(self, id, limit):
		"""
		Return results from an initialized search based on its ID

		status (results status):
		- 0: Sucess with results.
		- 1: No more results available.
		- 2: Search ID not found.
		- 3: No results yet, but keep trying.

		type (low-level data type of result):
		- 0: Binary/unspecified
		- 1: Plain text
		- 2: Picture
		- 3: Video
		- 4: Audio
		- 5: Document file
		- 6: Executable file
		- 7: Container
		- 1001: User
		- 1002: Leak
		- 1004: URL
		- 1005: Forum

		media (high-level data type):
		- 0: Invalid
		- 1: Paste document
		- 2: Paste user
		- 3: Forum
		- 4: Forum Board
		- 5: Forum Thread
		- 6: Forum Post
		- 7: Forum User
		- 8: Screenshot of a website
		- 9: HTML copy of a website
		- 10: Invalid, do not use.
		- 11: Invalid, do not use.
		- 12: Invalid, do not use.
		- 13: Tweet
		- 14: URL, high-level item having HTML copies as linked sub-items.
		- 15: PDF Document
		- 16: Word document
		- 17: Excel document
		- 18: Powerpoint document
		- 19: Picture
		- 20: Audio file
		- 21: Video file
		- 22: Container files
		- 23: HTML file
		- 24: Text file

		added:
		- When the item was indexed.

		date:
		- The date of the original record if available.

		name:
		- Name of title

		description:
		- Typically not used

		xscore:
		- Relevancy score, between 0-100

		simhash:
		- Similarity hash, depending on the content type

		bucket:
		- The bucket in which the result was found.

		keyvalues:
		- Not used

		tags:
		- Additional information on the item

		relations:
		- Identifiers of related items

		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(self.API_ROOT + f'/intelligent/search/result?id={id}&limit={limit}', headers=h)
		if(r.status_code == 200):
			return r.json()
		else:
			return r.status_code

	def INTEL_TERMINATE_SEARCH(self, uuid):
		"""
		Terminate a previously initialized search based on its UUID.
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(self.API_ROOT + f'/intelligent/search/terminate?id={uuid}', headers=h)
		if(r.status_code == 200):
			return True
		else:
			return r.status_code
	
	def PHONEBOOK_SEARCH(self, term, maxresults=100, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0, terminate=[], target=0):
		"""
		Initialize a phonebook search and return the ID of the task/search for further processing
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		p = {
			"term": term,
			"buckets": buckets,
			"lookuplevel": 0,
			"maxresults": maxresults,
			"timeout": timeout,
			"datefrom": datefrom,
			"dateto": dateto,
			"sort": sort,
			"media": media,
			"terminate": terminate,
			"target": target
		}
		r = requests.post(self.API_ROOT + '/phonebook/search', headers=h, json=p)
		if r.status_code == 200:
			return r.json()['id']
		else:
			return r.status_code

	def PHONEBOOK_SEARCH_RESULT(self, id, limit=1000, offset=-1):
		"""
		Fetch results from a phonebook search based on ID.
		offset:
		- Do not use. If omitted (default), each call will get the next available results.
		___________________________________________
		RETURN VALUES
		status (results status):
		- 0: Sucess with results.
		- 1: No more results available.
		- 2: Search ID not found.
		- 3: No results yet, but keep trying.
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(self.API_ROOT + f'/phonebook/search/result?id={id}&limit={limit}&offset={offset}', headers=h)
		if(r.status_code == 200):
			return r.json()
		else:
			return r.status_code

	def query_results(self, id, limit):
		"""
		Query the results from an intelligent search.
		Meant for usage within loops.
		"""
		results = self.INTEL_SEARCH_RESULT(id, limit)
		return results

	def query_pb_results(self, id, limit):
		"""
		Query the results fom a phonebook search.
		Meant for usage within loops.
		"""
		results = self.PHONEBOOK_SEARCH_RESULT(id, limit)
		return results

	def search(self, term, maxresults=100, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0, terminate=[]):
		"""
		Conduct a simple search based on a search term.
		Other arguments have default values set, however they can be overridden to complete an advanced search.
		
		maxresults option:
		- Tells how many results to query maximum per bucket.
		- Example: maxresults=100

		buckets option:
		- Specify the buckets to search
		- Example: buckets=[]
		- Example: buckets=['pastes', 'darknet.i2p']

		timeout option:
		- Set a timeout value for the search.
		- Example: timeout=5

		datefrom option:
		- Set a starting date to begin the search from.
		- Example: 2020-01-01 00:00:00
		- Example: 2020-01-01 12:00:00

		dateto option:
		- Set an ending date to finish the search from.
		- Example: 2020-02-02 23:59:59
		- Example: 2020-02-02 00:00:00

		sort option:
		- Define the way to sort search results.
		- 0: No sorting.
		- 1: X-Score ASC. Least relevant items first.
		- 2: X-Score DESC. Most relevant items first.
		- 3: Date ASC. Oldest items first.
		- 4: Date DESC. Newest items first.

		media option:
		- Define the type of media to search for.
		- 0: Not set. (All media types)
		- 1: Paste document
		- 2: Paste User
		- 3: Forum
		- 4: Forum Board
		- 5: Forum Thread
		- 6: Forum Post
		- 7: Forum User
		- 8: Screenshot of a Website
		- 9: HTML copy of a website.
		- 10: Invalid, do not use.
		- 11: Invalid, do not use.
		- 12: Invalid, do not use.
		- 13: Tweet
		- 14: URL, high-level item having HTML copies as linked sub-items
		- 15: PDF document
		- 16: Word document
		- 17: Excel document
		- 18: Powerpoint document
		- 19: Picture
		- 20: Audio file
		- 21: Video file
		- 22: Container files including ZIP, RAR, TAR and others
		- 23: HTML file
		- 24: Text file

		The term must be a strong selector. These selector types are currently supported:
		- Email address
		- Domain, including wildcards like *.example.com
		- URL
		- IPv4 & IPv6
		- CIDRv4 & CIDRv6
		- Phone Number
		- Bitcoin Address
		- MAC Address
		- IPFS Hash
		- UUID
		- Storage ID
		- System ID
		- Simhash
		- Credit card number
		- IBAN

		Soft selectors (generic terms) are not supported!
		
		"""
		results = []
		done = False
		search_id = self.INTEL_SEARCH(term, maxresults, buckets, timeout, datefrom, dateto, sort, media, terminate)
		if(len(str(search_id)) <= 3):
			print(f"[!] intelx.INTEL_SEARCH() Received {self.get_error(search_id)}")
			sys.exit()
		while done == False:
			time.sleep(1) # lets give the backend a chance to aggregate our data
			r = self.query_results(search_id, maxresults)
			for a in r['records']:
				results.append(a)
			maxresults -= len(r['records'])
			if(r['status'] == 1 or r['status'] == 2 or maxresults <= 0):
				if(maxresults <= 0):
					self.INTEL_TERMINATE_SEARCH(search_id)
				done = True
		return {'records': results}

	def phonebooksearch(self, term, maxresults=1000, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0, terminate=[], target=0):
		"""
		Conduct a phonebook search based on a search term.
		Other arguments have default values set, however they can be overridden to complete an advanced search.
		"""
		results = []
		done = False
		search_id = self.PHONEBOOK_SEARCH(term, maxresults, buckets, timeout, datefrom, dateto, sort, media, terminate, target)
		if(len(str(search_id)) <= 3):
			print(f"[!] intelx.PHONEBOOK_SEARCH() Received {self.get_error(search_id)}")
			sys.exit()
		while done == False:
			time.sleep(1) # lets give the backend a chance to aggregate our data
			r = self.query_pb_results(search_id, maxresults)
			results.append(r)
			maxresults -= len(r['selectors'])
			if(r['status'] == 1 or r['status'] == 2 or maxresults <= 0):
				if(maxresults <= 0):
					self.INTEL_TERMINATE_SEARCH(search_id)
				done = True
		return results

	def stats(self, search):
		stats = {}
		for record in search['records']:
			if record['bucket'] not in stats:
				stats[record['bucket']] = 1
			else:
				stats[record['bucket']] += 1
		return json.dumps(stats)
