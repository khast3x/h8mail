#!/usr/bin/env python
import re
from utils.colors import colors as c
import configparser
import csv
import os

def find_files(targetdir):
	allfiles = []
	for root, _, filenames in os.walk(targetdir):
		for filename in filenames:
			c.info_news(c, "Using file {}".format(os.path.join(root,filename)))
			allfiles.append(os.path.join(root,filename))
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
		print(c.bold, c.fg.red, banner, c.reset)
	elif "warn" in b_type:
		print(c.fg.pink, "\tIf you paid for this software you got scammed\n\n", c.reset)
	

def fetch_emails(target):
	e = re.findall(r"[\w\.-]+@[\w\.-]+", target)
	if e:
		print(c.fg.green, ','.join(e), c.reset)
		return e
	return None


def get_emails_from_file(targets_file):
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
		c.bad_news(c, "Problems occurred while trying to get emails from file")
		print(ex)


def get_config_from_file(user_args):
	try:
		config_file = user_args.config_file
		config = configparser.ConfigParser()
		config.read(config_file)
		c.info_news(c, "Correctly read config file")

		if user_args.cli_apikeys:
			user_cli_keys = user_args.cli_apikeys.split(",")
			for user_key in user_cli_keys:
				if user_key:
					config.set("DEFAULT", user_key.split(":", maxsplit=1)[0], user_key.split(":", maxsplit=1)[1])
		return config
	except Exception as ex:
		c.bad_news(c, "Problems occurred while trying to get configuration file")
		print(ex)


def save_results_csv(dest_csv, target_obj_list):
	with open(dest_csv, 'w', newline='') as csvfile:
		try:
			writer = csv.writer(csvfile)

			writer.writerow(["Target", "Type", "Data"])
			c.good_news(c, "Writing to CSV")
			for t in target_obj_list:
				for i in range(len(t.data)):
					if len(t.data[i]) == 2: # Contains data header + body
						writer.writerow([t.email, t.data[i][0], t.data[i][1]])
		except Exception as ex:
			c.bad_news(c, "Error writing to csv")
			print(ex)