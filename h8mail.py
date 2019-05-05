import argparse
import re
import os
import configparser
from utils.colors import colors as c
from utils.classes import target
from utils.helpers import print_banner, fetch_emails, get_config_from_file, get_emails_from_file, save_results_csv


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
				print()
				c.info_news(c, "No results founds")
				continue
			if len(t.data[i]) == 2: # Contains data header + body
				if "HIBP" in t.data[i][0]:
					c.print_result(c, t.email, t.data[i][1], "HIBP")
				if "HUNTER_PUB" in t.data[i][0]:
					c.print_result(c, t.email, str(t.data[i][1]) + " RELATED EMAILS", "HUNTERPUB")
				if "HUNTER_RELATED" in t.data[i][0]:
					c.print_result(c, t.email, t.data[i][1], "HUNTER_RELATED")
				if "SNUS" in t.data[i][0]:
					c.print_result(c, t.email, t.data[i][1], t.data[i][0])




def target_factory(targets, api_keys):
	finished = []

	for t in targets:
		c.info_news(c, "Looking up {target}".format(target=t))
		current_target = target(t)
		current_target.get_hibp()
		current_target.get_hunterio_public()
		if len(api_keys['DEFAULT']['hunterio']) != 0:
			current_target.get_hunterio_private(api_keys['DEFAULT']['hunterio'])
		if len(api_keys['DEFAULT']['snusbase_token']) != 0:
			current_target.get_snusbase(api_keys['DEFAULT']['snusbase_url'], api_keys['DEFAULT']['snusbase_token'])
		finished.append(current_target)

	return finished




def main(user_args):
	targets = []
	api_keys = get_config_from_file(user_args)
	c.good_news(c, "Targets:")
	user_stdin_target = fetch_emails(args.target_emails)

	if user_stdin_target:
		targets.extend(user_stdin_target)
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
	print_banner("warn")
	print_banner()
	main(args)
	c.good_news(c, "Done")