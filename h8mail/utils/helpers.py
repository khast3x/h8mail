#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from .colors import colors as c
import configparser
import csv
import os
import glob


def find_files(to_parse, pattern=""):
    """
    Returns list of files from t_parse filepath.
    Supports using globing (*) in filepaths.
    Can check for patterns such as 'gz'.
    """
    allfiles = []

    if "*" in to_parse:
        glob_result = glob.glob(to_parse)
        for g in glob_result:
            allfiles.append(g)
            c.info_news("Using file {}".format(g))
    if os.path.isfile(to_parse):
        if pattern in to_parse:
            c.info_news("Using file {}".format(to_parse))
            allfiles.append(to_parse)
    elif os.path.isdir(to_parse):
        for root, _, filenames in os.walk(to_parse):
            for filename in filenames:
                if pattern in filename:
                    c.info_news("Using file {}".format(os.path.join(root, filename)))
                    allfiles.append(os.path.join(root, filename))
    return allfiles


def print_banner(b_type="intro"):
    if "intro" in b_type:
        banner = """
	._____. ._____.     ;___________;
	| ._. | | ._. |     ; h8mail.py ;
	| !_| |_|_|_! |     ;-----------;
	!___| |_______!  Heartfelt Email OSINT
	.___|_|_| |___.   Use responsibly etc
	| ._____| |_. | ;____________________;
	| !_! | | !_! | ; github.com/khast3x ;
	!_____! !_____! ;--------------------;
	"""
        print(c.bold, c.fg.lightblue, banner, c.reset)
    elif "warn" in b_type:
        print(
            c.fg.pink,
            "\th8mail is free & open-source. Please report scammers.\n\n",
            c.reset,
        )
    elif "version" in b_type:
        print("\t", c.bold, c.fg.lightblue, "Version 2.0 - 'Birthday Update'", c.reset)


def fetch_emails(target, loose=False):
    """
    Returns a list of emails found in 'target'.
    Can be loosy to skip email pattern search.
    """
    if loose:
        t = target.split(" ")
        print(t)
        return t
    e = re.findall(r"[\w\.-]+@[\w\.-]+", target)
    if e:
        print(", ".join(e), c.reset)
        return e
    return None


def get_emails_from_file(targets_file, loose=False):
    """
    For each line in file, check for emails using fetch_emails().
    Returns list of emails.
    """
    email_obj_list = []
    try:
        target_fd = open(targets_file).readlines()
        for line in target_fd:
            e = fetch_emails(line)
            if e is None:
                continue
            else:
                email_obj_list.extend(e)
        return email_obj_list
    except Exception as ex:
        c.bad_news("Problems occurred while trying to get emails from file")
        print(ex)


def get_config_from_file(user_args):
    """
    Read config in file. If keys are passed using CLI, add them to the configparser object.
    Returns a configparser object already set to "DEFAULT" section.
    """

    try:
        config = configparser.ConfigParser()
        # Config file
        if user_args.config_file:
            for counter, config_file in enumerate(user_args.config_file):
                config_file = user_args.config_file[counter]
                config.read(config_file)
        # Use -k option
        if user_args.cli_apikeys:
            if config.has_section("h8mail") is False:
                config.add_section("h8mail")
            for counter, user_key in enumerate(user_args.cli_apikeys):
                user_cli_keys = user_args.cli_apikeys[counter].split(",")
                for user_key in user_cli_keys:
                    if user_key and "=" in user_key:
                        config.set(
                            "h8mail",
                            user_key.split("=", maxsplit=1)[0].strip(),
                            user_key.split("=", maxsplit=1)[1].strip(),
                        )
            for k in config["h8mail"]:
                if len((config["h8mail"][k])) != 0:
                    c.good_news(f"Found {k} configuration key")
        return config["h8mail"]
    except Exception as ex:
        c.bad_news("Problems occurred while trying to get configuration file")
        print(ex)


def save_results_csv(dest_csv, target_obj_list):
    """
    Outputs CSV from target object list.
    Dumps the target.data object variable into CSV file.
    """
    with open(dest_csv, "w", newline="") as csvfile:
        try:
            writer = csv.writer(csvfile)

            writer.writerow(["Target", "Type", "Data"])
            c.good_news("Writing to CSV")
            for t in target_obj_list:
                for i in range(len(t.data)):
                    if len(t.data[i]) == 2:  # Contains data header + body
                        writer.writerow([t.email, t.data[i][0], t.data[i][1]])
        except Exception as ex:
            c.bad_news("Error writing to csv")
            print(ex)


def weleakinfo_get_auth_token(endpoint, apikey):
    """
    WeLeakInfo requires getting a "session key" for querying the API
    We reproduce request header as in the target class
    Since this function will only be called when user has a key, I'd like to keep imports as local as possible
    """
    import requests
    import sys
    import platform

    headers = {
        "User-Agent": "h8mail-v.2.0-OSINT-and-Education-Tool (PythonVersion={pyver}; Platform={platfrm})".format(
            pyver=sys.version.split(" ")[0], platfrm=platform.platform().split("-")[0]
        )
    }
    data = {"key": apikey}
    try:
        response = requests.request(
            url=endpoint,
            headers=headers,
            method="POST",
            timeout=10,
            allow_redirects=True,
            data=data,
        )

        if response.status_code == 200:
            if "true" in response["Success"] and len(response["Message"]) != 0:
                return response["Message"]
        else:
            print(response.status_code)
            print(response)
    except Exception as ex:
        c.bad_news("Error getting WeLeakInfo authentication token")
        print(ex)
