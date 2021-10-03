#!/usr/bin/env python
from .intelx import intelx as i
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
        print(f"Email: {self.target}")
        print(f"Path: {self.filepath}")
        print(f"Line: {self.line}")
        print(f"Content: {self.content}")
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
                f"DEBUG: Created target object for {self.target}",
                c.reset,
            )

    def not_exists(self, pattern):
        for d in self.data:
            if len(d) >= 2:
                if d[1] == pattern:
                    return False
        return True

    def make_request(
        self,
        url,
        meth="GET",
        timeout=20,
        redirs=True,
        data=None,
        params=None,
        verify=True,
        auth=None,
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
                auth=auth,
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
                        f"{k}: {v}" for k, v in response.headers.items()
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

    # New HIBP API
    def get_hibp3(self, api_key):
        try:
            c.info_news("[" + self.target + "]>[hibp]")
            sleep(1.3)
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{self.target}"
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
                    f"No breaches found for {self.target} using HIBP v3"
                )

            else:
                c.bad_news(
                    f"HIBP v3: got API response code {response.status_code} for {self.target}"
                )

        except Exception as e:
            c.bad_news("haveibeenpwned v3: " + self.target)
            print(e)

    # New HIBP API
    def get_hibp3_pastes(self):
        try:
            c.info_news("[" + self.target + "]>[hibp-paste]")
            sleep(1.3)
            url = f"https://haveibeenpwned.com/api/v3/pasteaccount/{self.target}"

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
                    f"No pastes found for {self.target} using HIBP v3 PASTE"
                )
            else:
                c.bad_news(
                    f"HIBP v3 PASTE: got API response code {response.status_code} for {self.target}"
                )

        except Exception as ex:
            c.bad_news("HIBP v3 PASTE error: " + self.target)
            print(ex)

    def get_intelx(self, api_keys):
        try:
            intel_files = []
            intelx = i(key=api_keys["intelx_key"], ua="h8mail-v.{h8ver}-OSINT-and-Education-Tool (PythonVersion={pyver}; Platform={platfrm})".format(
                h8ver=__version__,
                pyver=sys.version.split(" ")[0],
                platfrm=platform.platform().split("-")[0],
            ))
            from .intelx_helpers import intelx_getsearch
            from .localsearch import local_search
            from os import remove, fspath

            maxfile = 10
            if api_keys["intelx_maxfile"]:
                maxfile = int(api_keys["intelx_maxfile"])
            search = intelx_getsearch(self.target, intelx, maxfile)
            if self.debug:
                import json

                print(json.dumps(search, indent=4))

            for record in search["records"]:
                filename = record["systemid"].strip() + ".txt"
                intel_files.append(filename)
                if record["media"] != 24:
                    c.info_news(
                        "Skipping {name}, not text ({type})".format(
                            type=record["mediah"], name=record["name"]
                        )
                    )
                    continue
                c.good_news(
                    "["
                    + self.target
                    + "]>[intelx.io] Fetching "
                    + record["name"]
                    + " as file "
                    + filename
                    + " ("
                    + "{:,.0f}".format(record["size"] / float(1 << 20))
                    + " MB)"
                )
                intelx.FILE_READ(record["systemid"], 0, record["bucket"], filename)
                found_list = local_search([filename], [self.target])
                for f in found_list:
                    self.pwned += 1
                    self.data.append(
                        (
                            "INTELX.IO",
                            "{name} | Line: {line} - {content}".format(
                                name=record["name"].strip(),
                                line=f.line,
                                content=" ".join(f.content.split()),
                            ),
                        )
                    )
                # print(contents) # Contains search data
            for file in intel_files:
                try:
                    if self.debug:
                        c.info_news(
                            "["
                            + self.target
                            + f"]>[intelx.io] [DEBUG] Keeping {file}"
                        )
                    else:
                        c.info_news(
                            "["
                            + self.target
                            + f"]>[intelx.io] Removing {file}"
                        )
                        remove(file)
                except Exception as ex:
                    c.bad_news("intelx.io cleanup error: " + self.target)
                    print(ex)

        except Exception as ex:
            c.bad_news("intelx.io error: " + self.target)
            print(ex)

    def get_emailrepio(self, api_key=""):
        try:
            sleep(0.5)
            if len(api_key) != 0:
                self.headers.update({"Key": api_key})
                c.info_news("[" + self.target + "]>[emailrep.io+key]")
            else:
                c.info_news("[" + self.target + "]>[emailrep.io]")
            url = f"https://emailrep.io/{self.target}"
            response = self.make_request(url)
            if response.status_code not in [200, 404, 429]:
                c.bad_news("Could not contact emailrep for " + self.target)
                print(response.status_code)
                print(response)
                return

            if response.status_code == 429:
                c.info_news(
                    "[warning] Is your emailrep key working? Get a free API key here: https://bit.ly/3b1e7Pw"
                )
            elif response.status_code == 404:
                c.info_news(
                    f"No data found for {self.target} using emailrep.io"
                )
            elif response.status_code == 200:
                data = response.json()

                self.data.append(
                    (
                        "EMAILREP_INFO",
                        "Reputation: {rep} | Deliverable: {deli}".format(
                            rep=data["reputation"].capitalize(),
                            deli=data["details"]["deliverable"],
                        ),
                    )
                )

                if data["details"]["credentials_leaked"] is True:
                    self.pwned += int(data["references"])  # or inc num references
                    if data["references"] == 1:
                        self.data.append(
                            (
                                "EMAILREP_LEAKS",
                                f"{data['references']} leaked credential",
                            )
                        )
                    else:
                        self.data.append(
                            (
                                "EMAILREP_LEAKS",
                                "{} leaked credentials".format(data["references"]),
                            )
                        )
                    c.good_news(
                        "Found {num} breaches for {target} using emailrep.io".format(
                            num=data["references"], target=self.target
                        )
                    )
                if len(data["details"]["profiles"]) != 0:
                    for profile in data["details"]["profiles"]:
                        self.data.append(("EMAILREP_SOCIAL", profile.capitalize()))
                c.good_news(
                    "Found {num} social profiles linked to {target} using emailrep.io".format(
                        num=len(data["details"]["profiles"]), target=self.target
                    )
                )
                if "never" in data["details"]["last_seen"]:
                    return
                self.data.append(("EMAILREP_1ST_SN", data["details"]["first_seen"]))
                c.good_news(
                    "{target} was first seen on the {data}".format(
                        data=data["details"]["first_seen"], target=self.target
                    )
                )
                self.data.append(("EMAILREP_LASTSN", data["details"]["last_seen"]))
                c.good_news(
                    "{target} was last seen on the {data}".format(
                        data=data["details"]["last_seen"], target=self.target
                    )
                )
            else:
                c.bad_news(
                    "emailrep.io: got API response code {code} for {target}".format(
                        code=response.status_code, target=self.target
                    )
                )
            if len(api_key) != 0:
                self.headers.popitem()
        except Exception as ex:
            c.bad_news("emailrep.io error: " + self.target)
            print(ex)

    def get_scylla(self, user_query="email"):
        try:
            c.info_news("[" + self.target + "]>[scylla.so]")
            sleep(0.5)
            self.headers.update({"Accept": "application/json"})
            if user_query == "email":
                uri_scylla = 'email: "' + self.target + '"'
            elif user_query == "password":
                uri_scylla = 'password: "' + self.target + '"'
            elif user_query == "username":
                uri_scylla = 'name: "' + self.target + '"'
            elif user_query == "ip":
                uri_scylla = 'ip: "' + self.target + '"'
            elif user_query == "hash":
                uri_scylla = 'passhash: "' + self.target + '"'
            elif user_query == "domain":
                uri_scylla = 'email: "*@' + self.target + '"'
            url = "https://scylla.so/search?q={}".format(
                requests.utils.requote_uri(uri_scylla)
            )

            # https://github.com/khast3x/h8mail/issues/64
            response = self.make_request(
                url,
                verify=False,
                # auth=requests.auth.HTTPBasicAuth("sammy", "BasicPassword!"),
            )
            self.headers.popitem()

            if response.status_code not in [200, 404]:
                c.bad_news("Could not contact scylla.so for " + self.target)
                print(response.status_code)
                print(response)
                return
            data = response.json()
            total = 0
            for d in data:
                for field, k in d["fields"].items():
                    if k is not None:
                        total += 1
            c.good_news(
                "Found {num} entries for {target} using scylla.so ".format(
                    num=total, target=self.target
                )
            )
            for d in data:
                for field, k in d["fields"].items():
                    if "name" in field and k is not None:
                        self.data.append(("SCYLLA_USERNAME", k))
                        self.pwned += 1
                    elif (
                        "email" in field and k is not None and user_query != "email"
                    ):
                        self.data.append(("SCYLLA_EMAIL", k))
                        self.pwned += 1
                    elif "password" in field and k is not None:
                        self.data.append(("SCYLLA_PASSWORD", k))
                        self.pwned += 1
                    elif "passhash" in field and k is not None:
                        self.data.append(("SCYLLA_HASH", k))
                        self.pwned += 1
                    elif "passsalt" in field and k is not None:
                        self.data.append(("SCYLLA_HASHSALT", k))
                        self.pwned += 1
                    elif "ip" in field and k is not None:
                        self.data.append(("SCYLLA_LASTIP", k))
                        self.pwned += 1
                    if "domain" in field and k is not None:
                        self.data.append(("SCYLLA_SOURCE", k))
                        self.pwned += 1
                    else:
                        self.data.append(("SCYLLA_SOURCE", "N/A"))
        except Exception as ex:
            c.bad_news("scylla.so error: " + self.target)
            print(ex)

    def get_hunterio_public(self):
        try:
            c.info_news("[" + self.target + "]>[hunter.io public]")
            target_domain = self.target.split("@")[1]
            url = f"https://api.hunter.io/v2/email-count?domain={target_domain}"
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
            c.bad_news("hunter.io (public API) error: " + self.target)
            print(ex)

    def get_hunterio_private(self, api_key):
        try:
            c.info_news("[" + self.target + "]>[hunter.io private]")
            target_domain = self.target.split("@")[1]
            url = f"https://api.hunter.io/v2/domain-search?domain={target_domain}&api_key={api_key}"
            req = self.make_request(url)
            response = req.json()
            b_counter = 0
            for e in response["data"]["emails"]:
                self.data.append(("HUNTER_RELATED", e["value"]))
                b_counter += 1
                if self.pwned != 0:
                    self.pwned += 1
            c.good_news(
                "Found {num} related emails for {target} using hunter.io (private)".format(
                    num=b_counter, target=self.target
                )
            )
        except Exception as ex:
            c.bad_news(
                f"hunter.io (private API) error for {self.target}:"
            )
            print(ex)

    def get_snusbase(self, api_url, api_key, user_query):
        try:
            if user_query == "ip":
                user_query = "lastip"
            if user_query == "domain":
                payload = {"type": "email", "term": "%@" + self.target, "wildcard": "true"}
            # elif user_query == "hash": If we want hash to search for password instead of reverse searching emails from the hash
            #     payload = {"hash": self.target}
            #     api_url = "https://api.snusbase.com/v3/hash"
            else:
                payload = {"type": user_query, "term": self.target}
            c.info_news("[" + self.target + "]>[snusbase]")
            url = api_url
            self.headers.update({"authorization": api_key})
            # payload = {"type": user_query, "term": self.target}
            req = self.make_request(url, meth="POST", data=payload)
            self.headers.popitem()
            response = req.json()
            if "error" in response:
                c.bad_news("[snusbase]> " + response["error"])
                c.bad_news("[snusbase]> " +  response["reason"])
                return 1
            if "size" in response:
                c.good_news(
                    "Found {num} entries for {target} using Snusbase".format(
                        num=response["size"], target=self.target
                    )
                )
                for result in response["results"]:
                    if "email" in result and self.not_exists(result["email"]):
                        self.data.append(("SNUS_RELATED", result["email"].strip()))
                    if "username" in result:
                        self.data.append(("SNUS_USERNAME", result["username"]))
                        self.pwned += 1
                    if "password" in result:
                        self.data.append(("SNUS_PASSWORD", result["password"]))
                        self.pwned += 1
                    if "hash" in result:
                        if "salt" in result:
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
                    if "lastip" in result:
                        self.data.append(("SNUS_LASTIP", result["lastip"]))
                        self.pwned += 1
                    if "name" in result:
                        self.data.append(("SNUS_NAME", result["name"]))
                        self.pwned += 1
                    if "db" in result and self.not_exists(result["db"]):
                        self.data.append(("SNUS_SOURCE", result["db"]))
                    else:
                        self.data.append(("SNUS_SOURCE", "N/A"))
        except Exception as ex:
            c.bad_news(f"Snusbase error with {self.target}")
            print(ex)

    def get_leaklookup_pub(self, api_key):
        try:
            c.info_news("[" + self.target + "]>[leaklookup public]")
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
                    f"No breaches found for {self.target} using Leak-lookup (public)"
                )

        except Exception as ex:
            c.bad_news(
                f"Leak-lookup error with {self.target} (public)"
            )
            print(ex)

    def get_leaklookup_priv(self, api_key, user_query):
        try:
            if user_query == "ip":
                user_query = "ipadress"
            if user_query in ["hash"]:
                c.bad_news(
                    f"Leaklookup does not support {user_query} search (yet)"
                )
                return
            c.info_news("[" + self.target + "]>[leaklookup private]")
            url = "https://leak-lookup.com/api/search"
            payload = {"key": api_key, "type": user_query, "query": self.target}
            req = self.make_request(url, meth="POST", data=payload, timeout=60)
            response = req.json()
            if "false" in response["error"] and len(response["message"]) != 0:
                b_counter = 0
                for db, data in response["message"].items():
                    for d in data:
                        if "username" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_USERNAME", d["username"]))
                        if "email_address" in d.keys() and self.not_exists(
                            d["email_address"]
                        ):
                            self.data.append(
                                ("LKLP_RELATED", d["email_address"].strip())
                            )
                        if "password" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_PASSWORD", d["password"]))
                            b_counter += 1
                        if "hash" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_HASH", d["password"]))
                            b_counter += 1
                        if "ipaddress" in d.keys():
                            self.pwned += 1
                            self.data.append(("LKLP_LASTIP", d["ipaddress"]))
                            for tag in [
                                "address",
                                "address1",
                                "address2",
                                "country",
                                "zip",
                                "zipcode",
                                "postcode",
                                "state",
                            ]:
                                if tag in d.keys():
                                    self.pwned += 1
                                    self.data.append(
                                        ("LKLP_GEO", d[tag] + " (type: " + tag + ")")
                                    )
                            for tag in [
                                "firstname",
                                "middlename",
                                "lastname",
                                "mobile",
                                "number",
                                "userid",
                            ]:
                                if tag in d.keys():
                                    self.pwned += 1
                                    self.data.append(
                                        ("LKLP_ID", d[tag] + " (type: " + tag + ")")
                                    )
                    if self.not_exists(db):
                        self.data.append(("LKLP_SOURCE", db))

                c.good_news(
                    "Found {num} entries for {target} using LeakLookup (private)".format(
                        num=b_counter, target=self.target
                    )
                )

            if "false" in response["error"] and len(response["message"]) == 0:
                c.info_news(
                    f"No breaches found for {self.target} using Leak-lookup (private)"
                )
        except Exception as ex:
            c.bad_news(
                f"Leak-lookup error with {self.target} (private)"
            )
            print(ex)

    def get_weleakinfo_priv(self, api_key, user_query):
        try:
            c.info_news("[" + self.target + "]>[weleakinfo priv]")
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
                        f"WeLeakInfo (private) error response {response['Message']}"
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
                    else:
                        self.data.append(("WLI_SOURCE", "N/A"))
        except Exception as ex:
            c.bad_news(
                f"WeLeakInfo error with {self.target} (private)"
            )
            print(ex)

    def get_weleakinfo_pub(self, api_key):
        try:
            c.info_news("[" + self.target + "]>[weleakinfo public]")
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
                f"WeLeakInfo error with {self.target} (public)"
            )
            print(ex)

    def get_dehashed(self, api_email, api_key, user_query):
        try:
            if user_query == "hash":
                user_query == "hashed_password"
            if user_query == "ip":
                user_query == "ip_address"

            c.info_news("[" + self.target + "]>[dehashed]")
            url = "https://api.dehashed.com/search?query="
            if user_query == "domain":
                search_query = "email" + ":" + '"*@' + self.target + '"'
            else:
                search_query = user_query + ":" + '"' + self.target + '"'
            self.headers.update({"Accept": "application/json"})
            req = self.make_request(
                url + search_query, meth="GET", timeout=60, auth=(api_email, api_key)
            )
            if req.status_code == 200:
                response = req.json()
                if response["total"] is not None:
                    c.good_news(
                        "Found {num} entries for {target} using Dehashed.com".format(
                            num=str(response["total"]), target=self.target
                        )
                    )

                for result in response["entries"]:
                    if (
                        "username" in result
                        and result["username"] is not None
                        and len(result["username"].strip()) > 0
                    ):
                        self.data.append(("DHASHD_USERNAME", result["username"]))
                    if (
                        "email" in result
                        and self.not_exists(result["email"])
                        and result["email"] is not None
                        and len(result["email"].strip()) > 0
                    ):
                        self.data.append(("DHASHD_RELATED", result["email"].strip()))
                    if (
                        "password" in result
                        and result["password"] is not None
                        and len(result["password"].strip()) > 0
                    ):
                        self.data.append(("DHASHD_PASSWORD", result["password"]))
                        self.pwned += 1
                    if (
                        "hashed_password" in result
                        and result["hashed_password"] is not None
                        and len(result["hashed_password"].strip()) > 0
                    ):
                        self.data.append(("DHASHD_HASH", result["hashed_password"]))
                        self.pwned += 1
                    for tag in ["name", "vin", "address", "phone"]:
                        if (
                            tag in result
                            and result[tag] is not None
                            and len(result[tag].strip()) > 0
                        ):
                            self.data.append(
                                ("DHASHD_ID", result[tag] + " (type: " + tag + ")")
                            )
                            self.pwned += 1
                    # Documentation and JSON are not synced, using both source keys
                    if "obtained_from" in result and self.not_exists(
                        result["obtained_from"]
                    ):
                        self.data.append(("DHASHD_SOURCE", result["obtained_from"]))
                    elif "database_name" in result and self.not_exists(
                        result["database_name"]
                    ):
                        self.data.append(("DHASHD_SOURCE", result["database_name"]))
                    else:
                        self.data.append(("DHASHD_SOURCE", "N/A"))
                if response["balance"] is not None:
                    self.data.append(
                        (
                            "DHASHD_CREDITS",
                            str(response["balance"]) + " DEHASHED CREDITS REMAINING",
                        )
                    )
            else:
                c.bad_news("Dehashed error: status code " + str(req.status_code))
            self.headers.popitem()
        except Exception as ex:
            c.bad_news(f"Dehashed error with {self.target}")
            print(ex)
    
    def get_breachdirectory(self, user, passw, user_query):
        # Todo: implement password source search when email has answer
        c.info_news("[" + self.target + "]>[breachdirectory.org]")
        if user_query not in ["email", "username", "password", "domain"]:
            c.bad_news("Breachdirectory does not support this option")
            exit(1)
        mode = "pastes"
        url = "https://breachdirectory.org/api/index?username={user}&password={passw}&func={mode}&term={target}".format(user=user, passw=passw, mode=mode, target=self.target)
        try:
            req = self.make_request(
                    url, timeout=60
                )
            if req.status_code == 200:
                    response = req.json()
                    if response["data"] is not None:
                        for result in response["data"]:
                            if "email" in result and "email" not in user_query:
                                self.data.append(("BREACHDR_EMAIL", result["email"]))
                            if "password" in result:
                                self.data.append(("BREACHDR_PASS", result["password"]))
                            if "hash" in result:
                                self.data.append(("BREACHDR_HASH", result["hash"]))
                            if "source" in result:
                                self.data.append(("BREACHDR_SOURCE", result["source"]))
                                self.pwned += 1
                            else:
                                self.data.append(("BREACHDR_SOURCE", "N/A"))
                    # Follow up with an aggregated leak sources query
                    url_src = "https://breachdirectory.org/api/index?username={user}&password={passw}&func={mode}&term={target}".format(user=user, passw=passw, mode="sources", target=self.target)
                    req = self.make_request(
                        url_src, timeout=60
                    )
                    if req.status_code == 200:
                        response = req.json()
                        if response["sources"] is not None:
                            for result in response["sources"]:
                                self.data.append(("BREACHDR_EXTSRC", result))
                    ## If using the 'auto' mode instead of pastes
                    #     c.good_news(
                    #         "Found {num} entries for {target} using breachdirectory.org".format(
                    #             num=str(response["found"]), target=self.target
                    #         )
                    #     )

                    # for result in response["result"]:
                    #     if result["has_password"] is True:
                    #         self.data.append(("BREACHDR_PASS", result["password"]))
                    #         self.data.append(("BREACHDR_MD5", result["md5"]))
                    #         if result["sources"] == "Unverified":
                    #             source = result["sources"]
                    #         elif len(result["sources"]) > 1:
                    #             source = ", ".join(result["sources"])
                    #         else:
                    #             source = result["sources"][0]
                    #         self.data.append(("BREACHDR_SOURCE", source))
                    #         self.pwned += 1
        except Exception as ex:
            c.bad_news(f"Breachdirectory error with {self.target}")
            print(ex)
