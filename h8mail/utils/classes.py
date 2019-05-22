#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from .colors import colors as c
import requests
import json
import socket
import sys
import platform


class local_breach_target:
    """
	Class is called when performing local file search.
	This class is meant to store found data, to be later appended to the existing target objects.
	Used by both cleartext and gzip search
	"""

    def __init__(self, email, fp, ln, content):
        self.email = email
        self.filepath = fp
        self.line = ln
        self.content = content

    def dump(self):
        print("Email: {}".format(self.email))
        print("Path: {}".format(self.filepath))
        print("Line: {}".format(self.line))
        print("Content: {}".format(self.content))


class target:
    """
	Main class used to create and follow breach data.
	Found data is stored in self.data. Each method switches self.pwned to True when data is found.
	"""

    def __init__(self, email):
        self.headers = {
            "User-Agent": "h8mail-v.2.0-OSINT-and-Education-Tool (PythonVersion={pyver}; Platform={platfrm})".format(
                pyver=sys.version.split(" ")[0],
                platfrm=platform.platform().split("-")[0],
            )
        }
        self.email = email
        self.pwned = False
        self.data = [()]

    def make_request(
        self, url, meth="GET", timeout=10, redirs=True, data=None, params=None
    ):
        try:
            response = requests.request(
                url=url,
                headers=self.headers,
                method=meth,
                timeout=timeout,
                allow_redirects=redirs,
                data=data,
                params=params,
            )
            # response = requests.request(url="http://127.0.0.1:8000", headers=self.headers, method=meth, timeout=timeout, allow_redirects=redirs, data=data, params=params)
            if response.status_code == 429:
                c.info_news(
                    "Reached RATE LIMIT for {src}, sleeping".format(src=response.url)
                )
                sleep(2.5)
        except Exception as ex:
            c.bad_news("Request could not be made for " + self.email)
            print(ex)
            print(response)
        return response

    def get_hibp(self):
        sleep(1.3)
        url = "https://haveibeenpwned.com/api/v2/breachedaccount/{}?truncateResponse=true".format(
            self.email
        )
        response = self.make_request(url)
        if response.status_code not in [200, 404]:
            c.bad_news("Could not contact HIBP for " + self.email)
            print(response.status_code)
            print(response)
            return

        if response.status_code == 200:
            self.pwned = True
            data = response.json()
            for d in data:  # Returned type is a dict of Name : Service
                for _, ser in d.items():
                    self.data.append(("HIBP_PWNED_SRC", ser))

            c.good_news(
                "Found {num} breaches for {target} using HIBP".format(
                    num=len(self.data) - 1, target=self.email
                )
            )

        elif response.status_code == 404:
            c.info_news("No breaches found for {} using HIBP".format(self.email))
            self.pwnd = False
        else:
            c.bad_news(
                "HIBP: got API response code {code} for {target}".format(
                    code=response.status_code, target=self.email
                )
            )
            self.pwnd = False

    def get_hunterio_public(self):
        try:
            target_domain = self.email.split("@")[1]
            url = "https://api.hunter.io/v2/email-count?domain={}".format(target_domain)
            req = self.make_request(url)
            response = req.json()
            if response["data"]["total"] != 0:
                self.data.append(("HUNTER_PUB", response["data"]["total"]))
            c.good_news(
                "Found {num} related emails for {target} using Hunter.IO".format(
                    num=response["data"]["total"], target=self.email
                )
            )
        except Exception as ex:
            c.bad_news("HunterIO (pubic API) error: " + self.email)
            print(ex)

    def get_hunterio_private(self, api_key):
        try:
            target_domain = self.email.split("@")[1]
            url = "https://api.hunter.io/v2/domain-search?domain={target}&api_key={key}".format(
                target=target_domain, key=api_key
            )
            req = self.make_request(url)
            response = req.json()
            b_counter = 0
            for e in response["data"]["emails"]:
                self.data.append(("HUNTER_RELATED", e["value"]))
                self.pwned = True
                b_counter += 1
            c.good_news(
                "Found {num} related emails for {target} using Hunter.IO (private)".format(
                    num=b_counter, target=self.email
                )
            )
        except Exception as ex:
            c.bad_news(
                "HunterIO (private API) error for {target}:".format(target=self.email)
            )
            print(ex)

    def get_snusbase(self, api_url, api_key):
        try:
            url = api_url
            self.headers.update({"Authorization": api_key})
            payload = {"type": "email", "term": self.email}
            req = self.make_request(url, meth="POST", data=payload)
            response = req.json()
            c.good_news(
                "Found {num} entries for {target} using Snusbase".format(
                    num=len(response["result"]), target=self.email
                )
            )
            for result in response["result"]:
                if result["password"]:
                    self.data.append(("SNUS_PASSWORD", result["password"]))
                    self.pwned = True
                if result["hash"]:
                    if result["salt"]:
                        self.data.append(
                            (
                                "SNUS_HASH_SALT",
                                result["hash"].strip() + " : " + result["salt"].strip(),
                            )
                        )
                        self.pwned = True
                    else:
                        self.data.append(("SNUS_HASH", result["hash"]))
                        self.pwned = True
        except Exception as ex:
            c.bad_news("Snusbase error with {target}".format(target=self.email))
            print(ex)

    def get_leaklookup_pub(self, api_key):
        try:
            url = "https://leak-lookup.com/api/search"
            payload = {"key": api_key, "type": "email_address", "query": self.email}
            req = self.make_request(url, meth="POST", data=payload, timeout=20)
            response = req.json()
            if "false" in response["error"] and len(response["message"]) != 0:
                c.good_news(
                    "Found {num} entries for {target} using LeakLookup".format(
                        num=len(response["message"]), target=self.email
                    )
                )
                for result in response["message"]:
                    self.pwned = True
                    self.data.append(("LEAKLOOKUP_PUB", result))
            if "false" in response["error"] and len(response["message"]) == 0:
                c.info_news(
                    "No breaches found for {} using Leak-lookup (pub)".format(
                        self.email
                    )
                )

        except Exception as ex:
            c.bad_news("Leak-lookup error with {target}".format(target=self.email))
            print(ex)

    def get_leaklookup_priv(self, api_key):
        try:
            url = "https://leak-lookup.com/api/search"
            payload = {"key": api_key, "type": "email_address", "query": self.email}
            req = self.make_request(url, meth="POST", data=payload, timeout=30)
            response = req.json()

            if "false" in response["error"] and len(response["message"]) != 0:
                b_counter = 0
                for _, data in response["message"].items():
                    for d in data:
                        if "password" in d.keys():
                            self.pwned = True
                            self.data.append(("LEAKLKUP_PASS", d["password"]))
                            b_counter += 1
                c.good_news(
                    "Found {num} entries for {target} using LeakLookup".format(
                        num=b_counter, target=self.email
                    )
                )

            if "false" in response["error"] and len(response["message"]) == 0:
                c.info_news(
                    "No breaches found for {} using Leak-lookup (priv)".format(
                        self.email
                    )
                )
        except Exception as ex:
            c.bad_news("Leak-lookup error with {target}".format(target=self.email))
            print(ex)

    def get_weleakinfo(self, auth_token):
        """
        Requires getting the temp key using the helpers.get_wli_key() beforehand
        API is currently is version bump
        """
        try:
            print("test_wli")

        except Exception as ex:
            c.bad_news("WeLeakInfo error with {target}".format(target=self.email))
            print(ex)
