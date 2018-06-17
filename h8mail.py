import argparse
import re
import os
import ui
import configparser
import csv
from classes import Target


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
		ui.info(ui.darkred, banner)


def fetch_emails(target):
	e = re.findall(r"[\w\.-]+@[\w\.-]+", target)
	if e:
		ui.info_2(e[0])
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
		ui.fatal("Problems occurred while trying to get emails from file", ex)


def get_config_from_file(user_args):
	try:
		config_file = user_args.config_file
		config = configparser.ConfigParser()
		config.read(config_file)
		ui.debug(ui.check, "Correctly read config file")

		if user_args.cli_apikeys:
			user_cli_keys = user_args.cli_apikeys.split(",")
			for user_key in user_cli_keys:
				if user_key:
					config.set("DEFAULT", user_key.split(":", maxsplit=1)[0], user_key.split(":", maxsplit=1)[1])
					ui.debug("Added", user_key.split(":", maxsplit=1)[0], config.get('DEFAULT', option=user_key.split(":")[0]))

		return config
	except Exception as ex:
		ui.fatal("Problems occurred while trying to get configuration file", ex)


def save_results_csv(dest_csv, target_obj_list):
	with open(dest_csv, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)

		writer.writerow(["email", "breached", "num services", "hibp_services", "weleakinfo_services","snusbase_services", "ip", "ports", "rev_dns", "related_emails", "snusbase_passwords", "snusbase_hash/salt", "breachcompilation_passwords"])
		print("* Writing to CSV\n")
		for target in target_obj_list:
			try:
				writer.writerow([target.email, target.pwnd, len(target.services["hibp"]), target.services["hibp"], target.services["weleakinfo"],target.services["snusbase"],target.ip, target.rev_ports, target.rev_dns, target.related_emails, target.snusbase_passw, target.snusbase_hash_salt, target.breachcomp_passw])
			except Exception as ex:
				ui.warning("Error writing to csv", ex)


def print_results(target_objs):
	for target in target_objs:
		ui.info_section("\n", ui.bold, "Result", ui.reset, ui.yellow, target.email)
		if target.pwnd:
			ui.info_2("breached", ui.check)
			ui.info(ui.teal, "---")
			ui.info("Breaches found", ui.darkred, "HIBP:", ui.teal, len(target.services["hibp"]))
			if target.services["weleakinfo"]:
				ui.info("Breaches found", ui.darkred, "WeLeakInfo:", ui.teal, len(target.services["weleakinfo"]))
			if target.services["snusbase"]:
				ui.info("Breaches found", ui.darkred, "Snusbase:", ui.teal, len(target.services["snusbase"]))
			if target.breachcomp_passw:
				ui.info("Breaches found", ui.darkred, "breachcompilation:", ui.teal, len(target.breachcomp_passw))

			ui.debug("Breaches/Dumps HIBP:", ui.lightgray, target.services["hibp"])
			ui.debug("Breaches/Dumps WeLeakInfo:", ui.lightgray, target.services["weleakinfo"])
			ui.debug("Breaches/Dumps Snusbase:", ui.lightgray, target.services["snusbase"])

		else:
			ui.info_2("not breached", ui.cross)

		if target.related_emails:
			ui.info("Related emails found", ui.darkred, "hunter.io:", ui.teal, target.related_emails)
			ui.info(ui.teal, "---")

		ui.info("Target hostname:", ui.teal, target.hostname)
		if target.ip:
			ui.info("Target domain IP:", ui.teal, target.ip)
		if target.rev_dns:
			ui.info("Target reverse DNS:", ui.teal, target.rev_dns)
		if target.rev_ports:
			ui.info("Open ports:", ui.teal, *target.rev_ports)

		if len(target.hunterio_mails) != 0:
			ui.info(ui.teal, "---")
			ui.info(ui.check, ui.darkred, "hunter.io", ui.reset, "best related emails:", ui.lightgray, "\n", target.hunterio_mails)

		if target.snusbase_passw:
			ui.info(ui.teal, "---")
			ui.info(ui.check, ui.darkred, "Snusbase:", ui.reset, "Passwords found", ui.teal, len(target.snusbase_passw))
		if target.snusbase_hash_salt:
			ui.info(ui.check, ui.darkred, "Snusbase:", ui.reset, "Hash/salts found", ui.teal, len(target.snusbase_hash_salt))
		if target.snusbase_hash_salt:
			ui.info(ui.darkred, "Snusbase", ui.reset, "passwords:", ui.teal, target.snusbase_passw)
		if target.snusbase_hash_salt:
			ui.info(ui.darkred, "Snusbase", ui.reset, "hash/salt:", ui.lightgray, target.snusbase_hash_salt)
		ui.info("\n")
		if target.breachcomp_passw:
			ui.info(ui.teal, "---")
			ui.info(ui.darkred, "breachcompilation", ui.reset, "passwords:", ui.teal, ui.teal, *target.breachcomp_passw)
			ui.info("-------------------------------")


def target_factory(targets, api_keys):
	target_objs = []
	domains = []
	ui.info_section("\n", ui.darkteal, "Lookup Status")
	for t in targets:
		ui.info_progress("=>> {}".format(t), len(target_objs)+1, len(targets))
		if t.split("@")[1] not in domains:
			domains.append(t.split("@")[1])  # todo remove redundant shodan calls
		current_target = Target(t)
		# Shodan
		if len(current_target.ip) != 0:
			current_target.get_shodan(api_keys['DEFAULT']['shodan'])
		# HaveIBeenPwned
		current_target.get_hibp()
		# WeLeakInfo Public API
		# current_target.get_weleakinfo_public()  # Currently offline
		# Hunter.io Public + Private API
		current_target.get_hunterio_public()
		if len(api_keys['DEFAULT']['hunterio']) != 0:
			current_target.get_hunterio_private((api_keys['DEFAULT']['hunterio']))

		# Snusbase API
		if len(api_keys['DEFAULT']['snusbase_token']) != 0:
			current_target.get_snusbase(api_keys['DEFAULT']['snusbase_url'], api_keys['DEFAULT']['snusbase_token'])
		ui.dot(last=True)

		target_objs.append(current_target)
	ui.info("\n")
	return target_objs


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
			ui.warning("Breach compilation", ex)


def main(user_args):
	targets = []
	api_keys = get_config_from_file(user_args)
	ui.info_section("\n", ui.darkteal, "Targets")
	user_stdin_target = fetch_emails(args.target_emails)

	if user_stdin_target:
		targets.append(user_stdin_target)
	elif os.path.isfile(user_args.target_emails):
		ui.debug(ui.darkgray, "Reading from file", user_args.target_emails)
		targets.extend(get_emails_from_file(user_args.target_emails))
	else:
		ui.warning("No targets found")

# Launch
	if not user_args.run_local:
		breached_targets = target_factory(targets, api_keys)
	elif user_args.run_local:
		breached_targets = [Target(t) for t in targets]
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
	ui.setup(verbose=args.verbosity)  # Show debug messages if -v True
	print_banner()
	main(args)
	ui.info("\n", ui.check, "Done")
