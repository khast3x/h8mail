#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from .colors import colors as c
import configparser
import csv
import os
import glob
from .version import __version__
import requests
import json


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
	._____. ._____.     ;____________;
	| ._. | | ._. |     ;   h8mail   ;
	| !_| |_|_|_! |     ;------------;
	!___| |_______!  Heartfelt Email OSINT
	.___|_|_| |___.    Use responsibly
	| ._____| |_. | ;____________________;
	| !_! | | !_! | ; github.com/khast3x ;
	!_____! !_____! ;--------------------;
	"""
        # print(c.bold, c.fg.pink, banner, c.reset)
        banner_tab = banner.splitlines()
        code = 17
        for b in banner_tab:
            clr = "\u001b[38;5;" + str(code) + "m "
            print(c.bold + clr + b + c.reset)
            code += 3
    elif "warn" in b_type:
        print(
            c.fg.green,
            "\th8mail is free & open-source. Please report scammers.\n\n",
            c.reset,
        )
    elif "version" in b_type:
        print(
            "\t",
            c.fg.lightgrey,
            "Version " + __version__ + ' - "ECHO MIKE" ',
            c.reset,
        )


def fetch_emails(target, user_args):
    """
    Returns a list of emails found in 'target'.
    Can be loosy to skip email pattern search.
    """
    if user_args.loose or user_args.user_query is not None:
        t = target.split(" ")
        print(t)
        return t
    e = re.findall(r"[\w\.-]+@[\w\.-]+", target)
    if e:
        print(", ".join(e), c.reset)
        return e
    return None


def get_emails_from_file(targets_file, user_args):
    """
    For each line in file, check for emails using fetch_emails().
    Returns list of emails.
    """
    email_obj_list = []
    try:
        target_fd = open(targets_file).readlines()
        print(targets_file)
        for line in target_fd:
            e = fetch_emails(line, user_args)
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
                        writer.writerow([t.target, t.data[i][0], t.data[i][1]])
        except Exception as ex:
            c.bad_news("Error writing to csv")
            print(ex)


def check_latest_version():
    """
    Fetches local version and compares it to github api tag version
    """
    response = requests.request(
        url="https://api.github.com/repos/khast3x/h8mail/releases/latest", method="GET"
    )
    data = response.json()
    latest = data["tag_name"]
    if __version__ == data["tag_name"]:
        c.good_news("h8mail is up to date")
    else:
        c.bad_news(
            "Not running latest h8mail version. [Current: {current} | Latest: {latest}]".format(
                current=__version__, latest=latest
            )
        )

def check_scylla_online():
    """
    Checks if scylla.sh is online
    """
    # Supress SSL Warning on UI
    try:
        requests.packages.urllib3.disable_warnings()
        re = requests.head(
            url="https://scylla.sh", verify=False
        )
        if re.status_code == 200:
            c.good_news("scylla.sh is up")
            return True
        return False
    except Exception:
        c.info_news("scylla.sh is down, skipping")