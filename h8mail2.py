import argparse
import re
import os
import configparser
import csv
from utils.colors import colors as c
from utils.classes import target

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


def fetch_emails(target):
	e = re.findall(r"[\w\.-]+@[\w\.-]+", target)
	if e:
		c.info_news(c, e[0])
		return e[0]
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
				email_obj_list.append(e)
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
					# c.info_news(c, "Added", user_key.split(":", maxsplit=1)[0], config.get('DEFAULT', option=user_key.split(":")[0]))

		return config
	except Exception as ex:
		c.bad_news(c, "Problems occurred while trying to get configuration file")
		print(ex)


def save_results_csv(dest_csv, target_obj_list):
	with open(dest_csv, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)

		writer.writerow(["email", "breached", "num services", "hibp_services", "weleakinfo_services","snusbase_services", "ip", "ports", "rev_dns", "related_emails", "snusbase_passwords", "snusbase_hash/salt", "breachcompilation_passwords"])
		print("* Writing to CSV\n")
		for target in target_obj_list:
			try:
				writer.writerow([target.email, target.pwnd, len(target.services["hibp"]), target.services["hibp"], target.services["weleakinfo"],target.services["snusbase"],target.ip, target.rev_ports, target.rev_dns, target.related_emails, target.snusbase_passw, target.snusbase_hash_salt, target.breachcomp_passw])
			except Exception as ex:
				c.bad_news(c, "Error writing to csv")
				print(ex)


def breachcomp_check(targets, breachcomp_path):
	# https://gist.github.com/scottlinux/9a3b11257ac575e4f71de811322ce6b3
	try:
		import subprocess
		query_bin = os.path.join(breachcomp_path, "query.sh")
		subprocess.call(["chmod", "+x", query_bin])
		for t in targets:
				procfd = subprocess.run([query_bin, t.email], stdout=subprocess.PIPE)
				output = procfd.stdout.decode("utf-8")
				if len(output) != 0:
					t.pwnd = True
					split_output = output.split("\n")
					for line in split_output:
						if line:
							t.breachcomp_passw.append(line.split(":")[1])
		return targets
	except Exception as ex:
			c.bad_news(c, "Breach compilation")
			print(ex)



def print_results(results):
	for t in results:
		print()
		c.print_res_header(c, t.email)
		for i in range(len(t.data)):
			if len(t.data) == 1:
				c.info_news(c, "No results founds")
				continue
			if len(t.data[i]) == 2: # Contains data header + body
				if "HIBP" in t.data[i][0]:
					c.print_result(c, t.email, t.data[i][1], "HIBP")
				if "HUNTER_PUB" in t.data[i][0]:
					c.print_result(c, t.email, str(t.data[i][1]) + " RELATED EMAILS", "HUNTERPUB")
				if "HUNTER_PRIV" in t.data[i][0]:
					c.print_result(c, t.email, str(t.data[i][1]) + " RELATED", "HUNTERPRIV")
				if "SNUS" in t.data[i][0]:
					c.print_result(c, t.email, t.data[i][1], t.data[i][0])




def target_factory(targets, api_keys):
	finished = []

	for t in targets:
		c.info_news(c, "Looking up {target}".format(target=t))
		current_target = target(t)
		# current_target.get_hibp()
		current_target.get_hunterio_public()
		current_target.get_hunterio_private(api_keys['DEFAULT']['hunterio'])
		current_target.get_snusbase(api_keys['DEFAULT']['snusbase_url'], api_keys['DEFAULT']['snusbase_token'])
		finished.append(current_target)

	return finished




def main(user_args):
	targets = []
	api_keys = get_config_from_file(user_args)
	c.good_news(c, "Targets:")
	user_stdin_target = fetch_emails(args.target_emails)

	if user_stdin_target:
		targets.append(user_stdin_target)
	elif os.path.isfile(user_args.target_emails):
		c.info_news(c, "Reading from file " + user_args.target_emails)
		targets.extend(get_emails_from_file(user_args.target_emails))
	else:
		c.bad_news(c, "No targets found")

# Launch
	if not user_args.run_local:
		breached_targets = target_factory(targets, api_keys)
	elif user_args.run_local:
		breached_targets = [target(t) for t in targets]
	if user_args.bc_path:
		breached_targets = breachcomp_check(breached_targets, user_args.bc_path)
	print_results(breached_targets)
	if user_args.output_file:
		save_results_csv(user_args.output_file, breached_targets)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Email information and password finding tool")

	parser.add_argument("-t", "--targets", required=True, dest="target_emails",
						help="Either single email, or file (one email per line). REGEXP")

	parser.add_argument("-c", "--config", dest="config_file", default="config.ini",
						help="Configuration file for API keys")
	parser.add_argument("-o", "--output", dest="output_file", help="File to write output")
	parser.add_argument("-bc", "--breachcomp", dest="bc_path", help="Path to the breachcompilation Torrent. https://ghostbin.com/paste/2cbdn")

	parser.add_argument("-v", "--verbose", dest="verbosity", help="Show debug information", action="store_true",
						default=False)
	parser.add_argument("-l", "--local", dest="run_local", help="Run local actions only", action="store_true", default=False)
	parser.add_argument("-k", "--apikey", dest="cli_apikeys", help="Pass config options. Format is \"K:V,K:V\"")


	args = parser.parse_args()
	print_banner()
	main(args)
	c.good_news(c, "Done")