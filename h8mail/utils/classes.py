#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from .colors import colors as c
import requests
import json
import socket
import sys
import platform
from .version import __version__


class local_breach_target:
    """
	Class is called when performing local file search.
	This class is meant to store found data, to be later appended to the existing target objects.
    local_to_targets() tranforms to target object
	Used by both cleartext and gzip search
	"""

    def __init__(self, target_data, fp, ln, content):
        self.target = target_data
        self.filepath = fp
        self.line = ln
        self.content = content

    def dump(self):
        print("Email: {}".format(self.target))
        print("Path: {}".format(self.filepath))
        print("Line: {}".format(self.line))
        print("Content: {}".format(self.content))
        print()


class target:
    """
	Main class used to create and follow breach data.
	Found data is stored in self.data. Each method increments self.pwned when data is found.
	"""

    def __init__(self, target_data, debug=False):
        self.headers = {
            "User-Agent": "h8mail-v.{h8ver}-OSINT-and-Education-Tool (PythonVersion={pyver}; Platform={platfrm})".format(
                h8ver=__version__,
                pyver=sys.version.split(" ")[0],
                platfrm=platform.platform().split("-")[0],
            )
        }
        self.target = target_data
        self.pwned = 0
        self.data = [()]
        self.debug = debug
        if debug:
            print(
                c.fg.red,
                "DEBUG: Created target object for {}".format(self.target),
                c.reset,
            )

    def not_exists(self, pattern):
        for d in self.data:
            if len(d) >= 2:
                if d[1] == pattern:
                    return False
        return True

    def make_request(
        self, url, meth="GET", timeout=10, redirs=True, data=None, params=None, verify=True
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
                verify=verify,
            )
            # response = requests.request(url="http://127.0.0.1:8000", headers=self.headers, method=meth, timeout=timeout, allow_redirects=redirs, data=data, params=params)
            if self.debug:
                c.debug_news("DEBUG: Sent the following---------------------")
                print(self.headers)
                print(url, meth, data, params)
                c.debug_news("DEBUG: Received the following---------------------")
                c.debug_news(response.url)
                c.debug_news("DEBUG: RESPONSE HEADER---------------------")
                print(
                    "\n".join(
                        "{}: {}".format(k, v) for k, v in response.headers.items()
                    )
                )
                c.debug_news("DEBUG: RESPONSE BODY---------------------")
                print(response.content)
                # print(response)
        except Exception as ex:
            c.bad_news("Request could not be made for " + self.target)
            print(url)
            print(ex)
            print(response)
        return response

    # Deprecated
    def get_hibp(self):
        try:
            sleep(1.3)
            c.info_news(c.bold + "HIBP free tier will stop working on the 2019/08/18")
            c.info_news(
                c.bold
                + "You can already use a purchased API key using h8mail (config file)"
                + c.reset
            )
            url = "https://haveibeenpwned.com/api/v2/breachedaccount/{}?truncateResponse=true".format(
                self.target
            )
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact HIBP for " + self.target)
                print(response.status_code)
                return

            if response.status_code == 200:
                data = response.json()
                for d in data:  # Returned type is a dict of Name : Service
                    for _, ser in d.items():
                        self.data.append(("HIBP", ser))
                        self.pwned += 1

                c.good_news(
                    "Found {num} breaches for {target} using HIBP".format(
                        num=len(self.data) - 1, target=self.target
                    )
                )
                self.get_hibp_pastes()

            elif response.status_code == 404:
                c.info_news("No breaches found for {} using HIBP".format(self.target))
            else:
                c.bad_news(
                    "HIBP: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.target
                    )
                )
        except Exception as ex:
            c.bad_news("HIBP error: " + self.target)
            print(ex)

    # Deprecated
    def get_hibp_pastes(self):
        try:
            sleep(1.3)
            url = "https://haveibeenpwned.com/api/v2/pasteaccount/{}".format(
                self.target
            )
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact HIBP PASTE for " + self.target)
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
                        num=len(data), target=self.target
                    )
                )

            elif response.status_code == 404:
                c.info_news(
                    "No pastes found for {} using HIBP PASTE".format(self.target)
                )
            else:
                c.bad_news(
                    "HIBP PASTE: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.target
                    )
                )
        except Exception as ex:
            c.bad_news("HIBP PASTE error: " + self.target)
            print(ex)

    # New HIBP API
    def get_hibp3(self, api_key):
        try:
            sleep(1.3)
            url = "https://haveibeenpwned.com/api/v3/breachedaccount/{}".format(
                self.target
            )
            self.headers.update({"hibp-api-key": api_key})
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact HIBP v3 for " + self.target)
                print(response.status_code)
                return

            if response.status_code == 200:
                data = response.json()
                for d in data:  # Returned type is a dict of Name : Service
                    for _, ser in d.items():
                        self.data.append(("HIBP3", ser))
                        self.pwned += 1

                c.good_news(
                    "Found {num} breaches for {target} using HIBP v3".format(
                        num=len(self.data) - 1, target=self.target
                    )
                )
                self.get_hibp3_pastes()
                self.headers.popitem()
            elif response.status_code == 404:
                c.info_news(
                    "No breaches found for {} using HIBP v3".format(self.target)
                )
            else:
                c.bad_news(
                    "HIBP v3: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.target
                    )
                )
        except Exception as e:
            c.bad_news("haveibeenpwned v3: " + self.target)
            print(e)

    # New HIBP API
    def get_hibp3_pastes(self):
        try:
            sleep(1.3)
            url = "https://haveibeenpwned.com/api/v3/pasteaccount/{}".format(
                self.target
            )
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact HIBP PASTE for " + self.target)
                print(response.status_code)
                print(response)
                return

            if response.status_code == 200:

                data = response.json()
                for d in data:  # Returned type is a dict of Name : Service
                    self.pwned += 1
                    if "Pastebin" in d["Source"]:
                        self.data.append(
                            ("HIBP3_PASTE", "https://pastebin.com/" + d["Id"])
                        )
                    else:
                        self.data.append(("HIBP3_PASTE", d["Id"]))

                c.good_news(
                    "Found {num} pastes for {target} using HIBP v3 Pastes".format(
                        num=len(data), target=self.target
                    )
                )

            elif response.status_code == 404:
                c.info_news(
                    "No pastes found for {} using HIBP v3 PASTE".format(self.target)
                )
            else:
                c.bad_news(
                    "HIBP v3 PASTE: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.target
                    )
                )
        except Exception as ex:
            c.bad_news("HIBP v3 PASTE error: " + self.target)
            print(ex)

    def get_emailrepio(self):
        try:
            sleep(0.5)
            url = "https://emailrep.io/{}".format(self.target)
            response = self.make_request(url)
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact emailrep for " + self.target)
                print(response.status_code)
                print(response)
                return

            if response.status_code == 200:
                data = response.json()
                if data["details"]["credentials_leaked"] is True:
                    self.pwned += int(data["references"])  # or inc num references
                    if data["references"] == 1:
                        self.data.append(("EMAILREP_LEAKS", "{} leaked credential".format(data["references"])))
                    else:
                        self.data.append(("EMAILREP_LEAKS", "{} leaked credentials".format(data["references"])))
                    c.good_news(
                        "Found {num} breaches for {target} using emailrep.io".format(
                            num=data["references"], target=self.target
                        )
                    )
                if "never" in data["details"]["last_seen"]:
                    return
                self.data.append(("EMAILREP_LASTSN", data["details"]["last_seen"]))
                if len(data["details"]["profiles"]) != 0:
                    for profile in data["details"]["profiles"]:
                        self.data.append(("EMAILREP_SOCIAL", profile))
                c.good_news("Found social profils")

            elif response.status_code == 404:
                c.info_news(
                    "No data found for {} using emailrep.io".format(self.target)
                )
            else:
                c.bad_news(
                    "emailrep.io: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.target
                    )
                )
        except Exception as ex:
            c.bad_news("emailrep.io error: " + self.target)
            print(ex)

    def get_scylla(self, user_query="email"):
        try:
            sleep(0.5)
            self.headers.update({"Accept": "application/json"})
            if user_query == "email":
                uri_scylla = 'Email: "' + self.target + '"'
            elif user_query == "password":
                uri_scylla = 'Password: "' + self.target + '"'
            elif user_query == "username":
                uri_scylla = 'User: "' + self.target + '"'
            elif user_query == "ip":
                uri_scylla = 'IP: "' + self.target + '"'
            elif user_query == "hash":
                uri_scylla = 'Hash: "' + self.target + '"'
            elif user_query == "domain":
                uri_scylla = 'Email: "*@' + self.target + '"'
            url = "https://scylla.sh/search?q={}".format(
                requests.utils.requote_uri(uri_scylla)
            )
            response = self.make_request(url, verify=False)
            self.headers.popitem()
            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact scylla.sh for " + self.target)
                print(response.status_code)
                print(response)
                return
            data = response.json()
            for d in data:
                for field, k in d["_source"].items():
                    if "User" in field and k is not None:
                        self.data.append(("SCYLLA_USERNAME", k))
                        self.pwned += 1
                    if "Email" in field and k is not None and user_query is not "email":
                        self.data.append(("SCYLLA_EMAIL", k))
                        self.pwned += 1
                    if "Password" in field and k is not None:
                        self.data.append(("SCYLLA_PASSWORD", k))
                        self.pwned += 1
                    if "PassHash" in field and k is not None:
                        self.data.append(("SCYLLA_HASH", k))
                        self.pwned += 1
                    if "PassSalt" in field and k is not None:
                        self.data.append(("SCYLLA_HASHSALT", k))
                        self.pwned += 1
                    if "IP" in field and k is not None:
                        self.data.append(("SCYLLA_LASTIP", k))
                        self.pwned += 1
                    if "Domain" in field and k is not None:
                        self.data.append(("SCYLLA_SOURCE", k))
                        self.pwned += 1
        except Exception as ex:
            c.bad_news("scylla.sh error: " + self.target)
            print(ex)

    def get_hunterio_public(self):
        try:
            target_domain = self.target.split("@")[1]
            url = "https://api.hunter.io/v2/email-count?domain={}".format(target_domain)
            req = self.make_request(url)
            response = req.json()
            if response["data"]["total"] != 0:
                self.data.append(("HUNTER_PUB", response["data"]["total"]))
            c.good_news(
                "Found {num} related emails for {target} using hunter.io (public)".format(
                    num=response["data"]["total"], target=self.target
                )
            )
        except Exception as ex:
            c.bad_news("hunter.io (pubic API) error: " + self.target)
            print(ex)

    def get_hunterio_private(self, api_key):
        try:
            target_domain = self.target.split("@")[1]
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
                "Found {num} related emails for {target} using hunter.io (private)".format(
                    num=b_counter, target=self.target
                )
            )
        except Exception as ex:
            c.bad_news(
                "hunter.io (private API) error for {target}:".format(target=self.target)
            )
            print(ex)

    def get_snusbase(self, api_url, api_key, user_query):
        try:
            if user_query == "ip":
                user_query = "lastip"
            if user_query in ["domain"]:
                c.bad_news(
                    "Snusbase does not support {} search (yet)".format(user_query)
                )
                return
            url = api_url
            self.headers.update({"Authorization": api_key})
            payload = {"type": user_query, "term": self.target}
            req = self.make_request(url, meth="POST", data=payload)
            self.headers.popitem()
            response = req.json()
            c.good_news(
                "Found {num} entries for {target} using Snusbase".format(
                    num=len(response["result"]), target=self.target
                )
            )
            for result in response["result"]:
                if result["username"]:
                    self.data.append(("SNUS_USERNAME", result["username"]))
                if result["email"] and self.not_exists(result["email"]):
                    self.data.append(("SNUS_RELATED", result["email"].strip()))
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
                if result["lastip"]:
                    self.data.append(("SNUS_LASTIP", result["lastip"]))
                if result["tablenr"] and self.not_exists(result["tablenr"]):
                    self.data.append(("SNUS_SOURCE", result["tablenr"]))

        except Exception as ex:
            c.bad_news("Snusbase error with {target}".format(target=self.target))
            print(ex)

    def get_leaklookup_pub(self, api_key):
        try:
            url = "https://leak-lookup.com/api/search"
            payload = {"key": api_key, "type": "email_address", "query": self.target}
            req = self.make_request(url, meth="POST", data=payload, timeout=20)
            response = req.json()
            if "false" in response["error"] and len(response["message"]) != 0:
                c.good_news(
                    "Found {num} entries for {target} using LeakLookup (public)".format(
                        num=len(response["message"]), target=self.target
                    )
                )
                for result in response["message"]:
                    self.pwned += 1
                    self.data.append(("LEAKLOOKUP_PUB", result))
            if "false" in response["error"] and len(response["message"]) == 0:
                c.info_news(
                    "No breaches found for {} using Leak-lookup (public)".format(
                        self.target
                    )
                )

        except Exception as ex:
            c.bad_news(
                "Leak-lookup error with {target} (public)".format(target=self.target)
            )
            print(ex)

    def get_leaklookup_priv(self, api_key, user_query):
        try:
            if user_query == "ip":
                user_query = "ipadress"
            if user_query in ["hash"]:
                c.bad_news(
                    "Leaklookup does not support {} search (yet)".format(user_query)
                )
                return
            url = "https://leak-lookup.com/api/search"
            payload = {"key": api_key, "type": user_query, "query": self.target}
            req = self.make_request(url, meth="POST", data=payload, timeout=30)
            response = req.json()
            if "false" in response["error"] and len(response["message"]) != 0:
                b_counter = 0
                for db, data in response["message"].items():
                    if self.not_exists(db):
                        self.data.append(("LKLP_SOURCE", db))
                    for d in data:
                        if "username" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_USERNAME", d["username"]))
                        if "ipaddress" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_LASTIP", d["ipaddress"]))
                        if "email_address" in d.keys() and self.not_exists(
                            d["email_address"]
                        ):
                            self.data.append(
                                ("LKLP_RELATED", d["email_address"].strip())
                            )
                        if "password" in d.keys():
                            if "plaintext" in d:
                                self.pwned += 1
                                self.data.append(("LKLP_HASH", d["password"]))
                                b_counter += 1
                            else:
                                self.pwned += 1
                                self.data.append(("LKLP_PASSWORD", d["password"]))
                                b_counter += 1

                c.good_news(
                    "Found {num} entries for {target} using LeakLookup (private)".format(
                        num=b_counter, target=self.target
                    )
                )

            if "false" in response["error"] and len(response["message"]) == 0:
                c.info_news(
                    "No breaches found for {} using Leak-lookup (private)".format(
                        self.target
                    )
                )
        except Exception as ex:
            c.bad_news(
                "Leak-lookup error with {target} (private)".format(target=self.target)
            )
            print(ex)

    def get_weleakinfo_priv(self, api_key, user_query):
        try:
            sleep(0.4)
            url = "https://api.weleakinfo.com/v3/search"
            self.headers.update({"Authorization": "Bearer " + api_key})
            self.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

            payload = {"type": user_query, "query": self.target}
            req = self.make_request(url, meth="POST", data=payload, timeout=30)
            self.headers.popitem()
            self.headers.popitem()
            response = req.json()
            if req.status_code == 400:
                c.bad_news(
                    f"Got WLI API response code {req.status_code}: Invalid search type provided"
                )
                return
            elif req.status_code != 200:
                c.bad_news(f"Got WLI API response code {req.status_code} (private)")
                return
            if req.status_code == 200:
                if response["Success"] is False:
                    c.bad_news(
                        "WeLeakInfo (private) error response {}".format(
                            response["Message"]
                        )
                    )
                    return
                c.good_news(
                    "Found {num} entries for {target} using WeLeakInfo (private)".format(
                        num=response["Total"], target=self.target
                    )
                )
                self.data.append(("WLI_TOTAL", response["Total"]))
                if response["Total"] == 0:
                    return
                for result in response["Data"]:
                    if "Username" in result:
                        self.data.append(("WLI_USERNAME", result["Username"]))
                    if "Email" in result and self.not_exists(result["Email"]):
                        self.data.append(("WLI_RELATED", result["Email"].strip()))
                    if "Password" in result:
                        self.data.append(("WLI_PASSWORD", result["Password"]))
                        self.pwned += 1
                    if "Hash" in result:
                        self.data.append(("WLI_HASH", result["Hash"]))
                        self.pwned += 1
                    if "Database" in result and self.not_exists(result["Database"]):
                        self.data.append(("WLI_SOURCE", result["Database"]))
        except Exception as ex:
            c.bad_news(
                "WeLeakInfo error with {target} (private)".format(target=self.target)
            )
            print(ex)

    def get_weleakinfo_pub(self, api_key):
        try:
            url = "https://api.weleakinfo.com/v3/public/email/{query}".format(
                query=self.target
            )
            self.headers.update({"Authorization": "Bearer " + api_key})
            req = self.make_request(url, timeout=30)
            self.headers.popitem()
            response = req.json()
            if req.status_code != 200:
                c.bad_news(f"Got WLI API response code {req.status_code} (public)")
                return
            else:
                c.good_news(
                    "Found {num} entries for {target} using WeLeakInfo (public)".format(
                        num=response["Total"], target=self.target
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
            c.bad_news(
                "WeLeakInfo error with {target} (public)".format(target=self.target)
            )
            print(ex)
