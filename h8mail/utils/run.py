# -*- coding: utf-8 -*-
# Most imports are after python2/3 check further down
import configparser
import argparse
import os
import re
import time
import sys

from .breachcompilation import breachcomp_check
from .classes import target
from .colors import colors as c
from .helpers import (
    fetch_emails,
    find_files,
    get_config_from_file,
    get_emails_from_file,
    print_banner,
    save_results_csv,
    check_latest_version,
    check_scylla_online,
)
from .print_json import save_results_json
from .localsearch import local_search, local_search_single, local_to_targets
from .localgzipsearch import local_gzip_search, local_search_single_gzip
from .summary import print_summary
from .chase import chase
from .print_results import print_results
from .gen_config import gen_config_file
from .url import target_urls


def target_factory(targets, user_args):
    """
    Receives list of emails and user args. Fetchs API keys from config file using user_args path and cli keys.
    For each target, launch target.methods() associated to found config artifacts.
    Handles chase logic with counters from enumerate()
    """
    # Removing duplicates here to avoid dups from chasing
    targets = list(set(targets))

    finished = []
    if user_args.config_file is not None or user_args.cli_apikeys is not None:
        api_keys = get_config_from_file(user_args)
    else:
        api_keys = None
    init_targets_len = len(targets)

    query = "email"
    skip_default_queries = False
    if user_args.user_query is not None:
        query = user_args.user_query
        skip_default_queries = True  # custom query skips default query automatically

    scylla_up = False
    if user_args.skip_defaults is False:
        scylla_up = check_scylla_online()

    for counter, t in enumerate(targets):
        c.info_news("Target factory started for {target}".format(target=t))
        if user_args.debug:
            current_target = target(t, debug=True)
        else:
            current_target = target(t)
        if not skip_default_queries:
            if not user_args.skip_defaults:
                current_target.get_hunterio_public()
                ## emailrep seems to insta-block h8mail user agent without a key
                # if api_keys is None or "emailrep" not in api_keys:
                #     current_target.get_emailrepio()
                # elif (
                #     api_keys is not None and "emailrep" in api_keys and query == "email"
                # ):
                #     current_target.get_emailrepio(api_keys["emailrep"])

        if api_keys is not None:
            if (
                "breachdirectory_user" in api_keys
                and "breachdirectory_pass" in api_keys
            ):
                current_target.get_breachdirectory(
                    api_keys["breachdirectory_user"], api_keys["breachdirectory_pass"], query
                )
            if "hibp" in api_keys and query == "email":
                current_target.get_hibp3(api_keys["hibp"])
            if "emailrep" in api_keys and query == "email":
                current_target.get_emailrepio(api_keys["emailrep"])
            if "hunterio" in api_keys and query == "email":
                current_target.get_hunterio_private(api_keys["hunterio"])
            if "intelx_key" in api_keys:
                current_target.get_intelx(api_keys)
            if "snusbase_token" in api_keys:
                if "snusbase_url" in api_keys:
                    snusbase_url = api_keys["snusbase_url"]
                else:
                    snusbase_url = "http://api.snusbase.com/v3/search"
                current_target.get_snusbase(
                    snusbase_url, api_keys["snusbase_token"], query
                )
            if "leak-lookup_priv" in api_keys:
                current_target.get_leaklookup_priv(api_keys["leak-lookup_priv"], query)
            if "leak-lookup_pub" in api_keys and query == "email":
                current_target.get_leaklookup_pub(api_keys["leak-lookup_pub"])
            if "weleakinfo_pub" in api_keys and query == "email":
                current_target.get_weleakinfo_pub(api_keys["weleakinfo_pub"])
            if "weleakinfo_priv" in api_keys:
                current_target.get_weleakinfo_priv(api_keys["weleakinfo_priv"], query)
            if "dehashed_key" in api_keys:
                if "dehashed_email" in api_keys:
                    current_target.get_dehashed(
                        api_keys["dehashed_email"], api_keys["dehashed_key"], query
                    )
                else:
                    c.bad_news("Missing Dehashed email")
        if scylla_up:
            current_target.get_scylla(query)

        # Chasing
        if user_args.chase_limit and counter <= init_targets_len:
            user_args_force_email = user_args
            user_args_force_email.user_query = "email"
            user_args_force_email.chase_limit -= 1
            finished_chased = target_factory(
                chase(current_target, user_args), user_args_force_email
            )
            finished.extend((finished_chased))
        finished.append(current_target)
    return finished


def h8mail(user_args):
    """
    Handles most user arg logic. Creates a list() of targets from user input.
    Starts the target object factory loop; starts local searches after factory if in user inputs
    Prints results, saves to csv or JSON if in user inputs
    """

    if user_args.user_targets and user_args.user_urls:
        c.bad_news("Cannot use --url with --target. Use one or the other.")
        exit(1)

    if not user_args.user_targets and not user_args.user_urls:
        c.bad_news("Missing Target or URL")
        exit(1)

    start_time = time.time()

    import warnings

    warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    targets = []
    if user_args.user_urls:
        targets = target_urls(user_args)
        if len(targets) == 0:
            c.bad_news("No targets found in URLs. Quitting")
            exit(0)

    # If we found emails from URLs, `targets` array already has stuff
    if len(targets) != 0:
        if user_args.user_targets is None:
            user_args.user_targets = []
            user_args.user_targets.extend(targets)

    else:  # Find targets in user input or file
        if user_args.user_targets is not None:
            for arg in user_args.user_targets:
                user_stdin_target = fetch_emails(arg, user_args)
                if os.path.isfile(arg):
                    c.info_news("Reading from file " + arg)
                    targets.extend(get_emails_from_file(arg, user_args))
                elif user_stdin_target:
                    targets.extend(user_stdin_target)
                else:
                    c.bad_news("No targets found in user input. Quitting")
                    exit(0)

    c.info_news("Removing duplicates")
    targets = list(set(targets))

    c.good_news("Targets:")
    for t in targets:
        c.good_news(t)

    # Launch
    breached_targets = target_factory(targets, user_args)

    # These are not done inside the factory as the factory iterates over each target individually
    # The following functions perform line by line checks of all targets per line

    if user_args.bc_path:
        breached_targets = breachcomp_check(breached_targets, user_args.bc_path)

    local_found = None
    # Handle cleartext search
    if user_args.local_breach_src:
        for arg in user_args.local_breach_src:
            res = find_files(arg)
            if user_args.single_file:
                local_found = local_search_single(res, targets)
            else:
                local_found = local_search(res, targets)
            if local_found is not None:
                breached_targets = local_to_targets(
                    breached_targets, local_found, user_args
                )
    # Handle gzip search
    if user_args.local_gzip_src:
        for arg in user_args.local_gzip_src:
            res = find_files(arg, "gz")
            if user_args.single_file:
                local_found = local_search_single_gzip(res, targets)
            else:
                local_found = local_gzip_search(res, targets)
            if local_found is not None:
                breached_targets = local_to_targets(
                    breached_targets, local_found, user_args
                )

    print_results(breached_targets, user_args.hide)

    print_summary(start_time, breached_targets)
    if user_args.output_file:
        save_results_csv(user_args.output_file, breached_targets)
    if user_args.output_json:
        save_results_json(user_args.output_json, breached_targets)

def parse_args(args):
    """
    Seperate functions to make it easier to run tests
    Pass args as an array
    """
    parser = argparse.ArgumentParser(
        description="Email information and password lookup tool", prog="h8mail"
    )

    parser.add_argument(
        "-t",
        "--targets",
        dest="user_targets",
        help="Either string inputs or files. Supports email pattern matching from input or file, filepath globing and multiple arguments",
        nargs="+",
    )
    parser.add_argument(
        "-u",
        "--url",
        dest="user_urls",
        help="Either string inputs or files. Supports URL pattern matching from input or file, filepath globing and multiple arguments. Parse URLs page for emails. Requires http:// or https:// in URL.",
        nargs="+",
    )
    parser.add_argument(
        "-q",
        "--custom-query",
        dest="user_query",
        help='Perform a custom query. Supports username, password, ip, hash, domain. Performs an implicit "loose" search when searching locally',
    )
    parser.add_argument(
        "--loose",
        dest="loose",
        help="Allow loose search by disabling email pattern recognition. Use spaces as pattern seperators",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_file",
        help="Configuration file for API keys. Accepts keys from Snusbase, WeLeakInfo, Leak-Lookup, HaveIBeenPwned, Emailrep, Dehashed and hunterio",
        nargs="+",
    )
    parser.add_argument(
        "-o", "--output", dest="output_file", help="File to write CSV output"
    )
    parser.add_argument(
        "-j", "--json", dest="output_json", help="File to write JSON output"
    )
    parser.add_argument(
        "-bc",
        "--breachcomp",
        dest="bc_path",
        help="Path to the breachcompilation torrent folder. Uses the query.sh script included in the torrent",
    )
    parser.add_argument(
        "-sk",
        "--skip-defaults",
        dest="skip_defaults",
        help="Skips Scylla and HunterIO check. Ideal for local scans",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-k",
        "--apikey",
        dest="cli_apikeys",
        help='Pass config options. Supported format: "K=V,K=V"',
        nargs="+",
    )
    parser.add_argument(
        "-lb",
        "--local-breach",
        dest="local_breach_src",
        help="Local cleartext breaches to scan for targets. Uses multiprocesses, one separate process per file, on separate worker pool by arguments. Supports file or folder as input, and filepath globing",
        nargs="+",
    )
    parser.add_argument(
        "-gz",
        "--gzip",
        dest="local_gzip_src",
        help="Local tar.gz (gzip) compressed breaches to scans for targets. Uses multiprocesses, one separate process per file. Supports file or folder as input, and filepath globing. Looks for 'gz' in filename",
        nargs="+",
    )
    parser.add_argument(
        "-sf",
        "--single-file",
        dest="single_file",
        help="If breach contains big cleartext or tar.gz files, set this flag to view the progress bar. Disables concurrent file searching for stability",
        action="store_true",
        default=False,
    ),
    parser.add_argument(
        "-ch",
        "--chase",
        dest="chase_limit",
        help="Add related emails from hunter.io to ongoing target list. Define number of emails per target to chase. Requires hunter.io private API key if used without power-chase",
        type=int,
        nargs="?",
    ),
    parser.add_argument(
        "--power-chase",
        dest="power_chase",
        help="Add related emails from ALL API services to ongoing target list. Use with --chase",
        action="store_true",
        default=False,
    ),
    parser.add_argument(
        "--hide",
        dest="hide",
        help="Only shows the first 4 characters of found passwords to output. Ideal for demonstrations",
        action="store_true",
        default=False,
    ),
    parser.add_argument(
        "--debug",
        dest="debug",
        help="Print request debug information",
        action="store_true",
        default=False,
    ),
    parser.add_argument(
        "--gen-config",
        "-g",
        dest="gen_config",
        help="Generates a configuration file template in the current working directory & exits. Will overwrite existing h8mail_config.ini file",
        action="store_true",
        default=False,
    ),

    return parser.parse_args(args)


def main():

    print_banner("warn")
    print_banner("version")
    print_banner()
    check_latest_version()
    user_args = parse_args(sys.argv[1:])
    if user_args.gen_config:
        gen_config_file()
        exit(0)
    h8mail(user_args)
