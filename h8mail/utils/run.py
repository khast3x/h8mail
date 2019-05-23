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
)
from .localsearch import local_search, local_search_single, local_to_targets
from .localgzipsearch import local_gzip_search, local_search_single_gzip
from .summary import print_summary


def print_results(results):

    for t in results:
        print()
        c.print_res_header(t.email)
        for i in range(len(t.data)):
            if len(t.data) == 1:
                print()
                c.info_news("No results founds")
                continue
            if len(t.data[i]) >= 2:  # Contains header + body data
                if "HIBP" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], "HIBP")
                if "HUNTER_PUB" in t.data[i][0]:
                    c.print_result(
                        t.email, str(t.data[i][1]) + " RELATED EMAILS", "HUNTERPUB"
                    )
                if "HUNTER_RELATED" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], "HUNTER_RELATED")
                if "SNUS" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], t.data[i][0])
                if "LOCAL" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], t.data[i][0])
                if "BC_PASS" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], t.data[i][0])
                if "LEAKLOOKUP_PUB" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], t.data[i][0])
                if "LEAKLKUP_PASS" in t.data[i][0]:
                    c.print_result(t.email, t.data[i][1], t.data[i][0])


def target_factory(targets, user_args):
    """
    Receives list of emails and user args. Fetchs API keys from config file using user_args path and cli keys.
    For each target, launch target.methods() associated to found config artifacts.
    Handles the hunter.io chase logic with counters from enumerate()
    """
    finished = []
    if user_args.config_file is not None or user_args.cli_apikeys is not None:
        api_keys = get_config_from_file(user_args)
    else:
        api_keys = None
    init_targets_len = len(targets)

    for counter, t in enumerate(targets):
        c.info_news("Target factory started for {target}".format(target=t))
        current_target = target(t)
        if not user_args.skip_defaults:
            current_target.get_hibp()
            current_target.get_hunterio_public()
        if api_keys is not None:
            c.info_news("Factory is calling API keys")
            if "hunterio" in api_keys:
                current_target.get_hunterio_private(api_keys["hunterio"])
                # If chase option. Check we're not chasing added target
                if user_args.chase_limit and counter < init_targets_len:
                    chase_limiter = 1
                    for i in range(len(current_target.data)):
                        if (
                            len(current_target.data[i]) >= 2  # Has header & data
                            and "HUNTER_RELATED" in current_target.data[i][0]
                            and chase_limiter <= user_args.chase_limit
                        ):
                            c.good_news(
                                "Adding {new_target} using HunterIO chase".format(
                                    new_target=current_target.data[i][1]
                                )
                            )
                            targets.append(current_target.data[i][1])
                            chase_limiter += 1

            if "snusbase_token" in api_keys:
                current_target.get_snusbase(
                    api_keys["snusbase_url"], api_keys["snusbase_token"]
                )
            if "leak-lookup_priv" in api_keys:
                current_target.get_leaklookup_priv(api_keys["leak-lookup_priv"])
            if "leak-lookup_pub" in api_keys:
                print("tototo")
                current_target.get_leaklookup_pub(api_keys["leak-lookup_pub"])
            if "weleakinfo_endpoint" in api_keys and "weleakinfo_key" in api_keys:
                from .helpers import weleakinfo_get_auth_token

                token = weleakinfo_get_auth_token(
                    api_keys["weleakinfo_endpoint"], api_keys["weleakinfo_key"]
                )
                current_target.get_weleakinfo(token)

        finished.append(current_target)
    return finished


def h8mail(user_args):
    """
    Handles most user arg logic. Creates a list() of targets from user input.
    Starts the target object factory loop; starts local searches after factory if in user inputs
    Prints results, saves to csv if in user inputs
    """
    targets = []
    start_time = time.time()
    c.good_news("Targets:")

    # Find targets in user input or file
    for arg in user_args.target_emails:
        user_stdin_target = fetch_emails(arg, user_args.loose)
        if user_stdin_target:
            targets.extend(user_stdin_target)
        elif os.path.isfile(arg):
            c.info_news("Reading from file " + arg)
            targets.extend(get_emails_from_file(arg, user_args.loose))
        else:
            c.bad_news("No targets found in user input")
            exit(1)

    c.info_news("Removing duplicates")
    targets = list(set(targets))
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
                breached_targets = local_to_targets(breached_targets, local_found)
    # Handle gzip search
    if user_args.local_gzip_src:
        for arg in user_args.local_gzip_src:
            res = find_files(arg, "gz")
            if user_args.single_file:
                local_found = local_search_single_gzip(res, targets)
            else:
                local_found = local_gzip_search(res, targets)
            if local_found is not None:
                breached_targets = local_to_targets(breached_targets, local_found)

    print_results(breached_targets)

    print_summary(start_time, breached_targets)
    if user_args.output_file:
        save_results_csv(user_args.output_file, breached_targets)


def main():
    # I REALLY want to make sure I don't get Python2 Issues on Github...

    parser = argparse.ArgumentParser(
        description="Email information and password lookup tool", prog="h8mail"
    )

    parser.add_argument(
        "-t",
        "--targets",
        required=True,
        dest="target_emails",
        help="Either string inputs or files. Supports email pattern matching from input or file, filepath globing and multiple arguments",
        nargs="+",
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
        help="Configuration file for API keys. Accepts keys from Snusbase, (WeLeakInfo, Citadel.pw), hunterio",
        nargs="+",
    )
    parser.add_argument(
        "-o", "--output", dest="output_file", help="File to write CSV output"
    )
    parser.add_argument(
        "-bc",
        "--breachcomp",
        dest="bc_path",
        help="Path to the breachcompilation torrent folder. Uses the query.sh script included in the torrent. https://ghostbin.com/paste/2cbdn",
    )
    parser.add_argument(
        "-sk",
        "--skip-defaults",
        dest="skip_defaults",
        help="Skips HaveIBeenPwned and HunterIO check. Ideal for local scans",
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
        help="Add related emails from HunterIO to ongoing target list. Define number of emails per target to chase. Requires hunter.io private API key",
        type=int,
        nargs="?",
    )

    user_args = parser.parse_args()
    print_banner("warn")
    print_banner("version")
    print_banner()
    h8mail(user_args)
