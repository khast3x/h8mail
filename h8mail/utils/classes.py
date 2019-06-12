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
    local_to_targets() tranforms to target object
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
	Found data is stored in self.data. Each method increments self.pwned when data is found.
	"""

    def __init__(self, email):
        self.headers = {
            "User-Agent": "h8mail-v.2.2-OSINT-and-Education-Tool (PythonVersion={pyver}; Platform={platfrm})".format(
                pyver=sys.version.split(" ")[0],
                platfrm=platform.platform().split("-")[0],
            )
        }
        self.email = email
        self.pwned = 0
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
        try:
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
                data = response.json()
                for d in data:  # Returned type is a dict of Name : Service
                    for _, ser in d.items():
                        self.data.append(("HIBP", ser))
                        self.pwned += 1

                c.good_news(
                    "Found {num} breaches for {target} using HIBP".format(
                        num=len(self.data) - 1, target=self.email
                    )
                )
                self.get_hibp_pastes()

            elif response.status_code == 404:
                c.info_news("No breaches found for {} using HIBP".format(self.email))
            else:
                c.bad_news(
                    "HIBP: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.email
                    )
                )
        except Exception as ex:
            c.bad_news("HIBP error: " + self.email)
            print(ex)

    def get_hibp_pastes(self):
        try:
            sleep(1.3)
            url = "https://haveibeenpwned.com/api/v2/pasteaccount/{}".format(self.email)
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact HIBP PASTE for " + self.email)
                print(response.status_code)
                print(response)
                return

            if response.status_code == 200:

                data = response.json()
                for d in data:  # Returned type is a dict of Name : Service
                    self.pwned += 1
                    if "Pastebin" in d["Source"]:
                        self.data.append(
                            ("HIBP_PASTE", "https://pastebin.com/" + d["Id"])
                        )
                    else:
                        self.data.append(("HIBP_PASTE", d["Id"]))

                c.good_news(
                    "Found {num} pastes for {target} using HIBP".format(
                        num=len(data), target=self.email
                    )
                )

            elif response.status_code == 404:
                c.info_news(
                    "No pastes found for {} using HIBP PASTE".format(self.email)
                )
            else:
                c.bad_news(
                    "HIBP PASTE: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.email
                    )
                )
        except Exception as ex:
            c.bad_news("HIBP PASTE error: " + self.email)
            print(ex)

    def get_emailrepio(self):
        try:
            url = "https://emailrep.io/{}".format(self.email)
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact emailrep for " + self.email)
                print(response.status_code)
                print(response)
                return

            if response.status_code == 200:
                data = response.json()
                if "never" in data["details"]["last_seen"]:
                    return
                self.data.append(("EMAILREP_LASTSN", data["details"]["last_seen"]))
                self.pwned += 1
                if len(data["details"]["profiles"]) != 0:
                    for profile in data["details"]["profiles"]:
                        self.data.append(("EMAILREP_SOCIAL", profile))
                        self.pwned += 1
                c.good_news("Found additional data with emailrep.io")

            elif response.status_code == 404:
                c.info_news("No data found for {} using emailrep.io".format(self.email))
            else:
                c.bad_news(
                    "emailrep.io: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.email
                    )
                )
        except Exception as ex:
            c.bad_news("emailrep.io error: " + self.email)
            print(ex)

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
                b_counter += 1
                if self.pwned is not 0:
                    self.pwned += 1
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
                    self.pwned += 1
                if result["hash"]:
                    if result["salt"]:
                        self.data.append(
                            (
                                "SNUS_HASH_SALT",
                                result["hash"].strip() + " : " + result["salt"].strip(),
                            )
                        )
                        self.pwned += 1
                    else:
                        self.data.append(("SNUS_HASH", result["hash"]))
                        self.pwned += 1
                if result["username"]:
                    self.data.append(("SNUS_USERNAME", result["username"]))
                if result["lastip"]:
                    self.data.append(("SNUS_LASTIP", result["lastip"]))
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
                    self.pwned += 1
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
                            if "plaintext" in d:
                                self.pwned += 1
                                self.data.append(("LKLP_HASH", d["password"]))
                                b_counter += 1
                            else:
                                self.pwned += 1
                                self.data.append(("LKLP_PASSWORD", d["password"]))
                                b_counter += 1
                        if "username" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_USERNAME", d["username"]))
                        if "ipaddress" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_LASTIP", d["ipaddress"]))

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

    def get_weleakinfo_priv(self, api_key):
        try:
            url = "https://api.weleakinfo.com/v3/search"
            self.headers.update({"Authorization": "Bearer " + api_key})
            self.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

            payload = {"type": "email", "query": self.email}
            req = self.make_request(url, meth="POST", data=payload)
            response = req.json()
            if req.status_code == 400:
                c.bad_news(
                    f"Got WLI API response code {req.status_code}: Invalid search type provided"
                )
                return
            elif req.status_code != 200:
                c.bad_news(f"Got WLI API response code {req.status_code}")
                return
            if req.status_code == 200:
                if response["Success"] is False:
                    c.bad_news(response["Message"])
                    return
                c.good_news(
                    "Found {num} entries for {target} using WeLeakInfo (private)".format(
                        num=response["Total"], target=self.email
                    )
                )
                self.data.append(("WLI_TOTAL", response["Total"]))
                if response["Total"] == 0:
                    return
                for result in response["Data"]:
                    if "Password" in result:
                        self.data.append(("WLI_PASSWORD", result["Password"]))
                        self.pwned += 1
                    if "Hash" in result:
                        self.data.append(("WLI_HASH", result["Hash"]))
                        self.pwned += 1
                    if "Username" in result:
                        self.data.append(("WLI_USERNAME", result["Username"]))
        except Exception as ex:
            c.bad_news("WeLeakInfo priv error with {target}".format(target=self.email))
            print(ex)

    def get_weleakinfo_pub(self, api_key):
        try:
            url = "https://api.weleakinfo.com/v3/public/email/{query}".format(
                query=self.email
            )
            self.headers.update({"Authorization": "Bearer " + api_key})
            req = self.make_request(url)
            response = req.json()
            if req.status_code != 200:
                c.bad_news(f"Got WLI API response code {req.status_code}")
                return
            else:
                c.good_news(
                    "Found {num} entries for {target} using WeLeakInfo (public)".format(
                        num=response["Total"], target=self.email
                    )
                )
                if response["Success"] is False:
                    c.bad_news(response["Message"])
                    return
                self.data.append(("WLI_PUB_TOTAL", response["Total"]))
                if response["Total"] == 0:
                    return
                for name, data in response["Data"].items():
                    self.data.append(("WLI_PUB_SRC", name + " (" + str(data) + ")"))
        except Exception as ex:
            c.bad_news("WeLeakInfo pub error with {target}".format(target=self.email))
            print(ex)

