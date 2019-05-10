import sys


def print_results(results):
    for t in results:
        print()
        c.print_res_header(c, t.email)
        for i in range(len(t.data)):
            if len(t.data) == 1:
                print()
                c.info_news(c, "No results founds")
                continue
            if len(t.data[i]) == 2:  # Contains data header + body
                if "HIBP" in t.data[i][0]:
                    c.print_result(c, t.email, t.data[i][1], "HIBP")
                if "HUNTER_PUB" in t.data[i][0]:
                    c.print_result(
                        c, t.email, str(t.data[i][1]) + " RELATED EMAILS", "HUNTERPUB"
                    )
                if "HUNTER_RELATED" in t.data[i][0]:
                    c.print_result(c, t.email, t.data[i][1], "HUNTER_RELATED")
                if "SNUS" in t.data[i][0]:
                    c.print_result(c, t.email, t.data[i][1], t.data[i][0])
                if "LOCAL" in t.data[i][0]:
                    c.print_result(c, t.email, t.data[i][1], t.data[i][0])
                if "BC_PASS" in t.data[i][0]:
                    c.print_result(c, t.email, t.data[i][1], t.data[i][0])


def target_factory(targets, api_keys, user_args):
    finished = []

    for t in targets:
        c.info_news(c, "Looking up {target}".format(target=t))
        current_target = target(t)
        if not user_args.skip_defaults:
            current_target.get_hibp()
            current_target.get_hunterio_public()
        if len(api_keys["DEFAULT"]["hunterio"]) != 0:
            current_target.get_hunterio_private(api_keys["DEFAULT"]["hunterio"])
        if len(api_keys["DEFAULT"]["snusbase_token"]) != 0:
            current_target.get_snusbase(
                api_keys["DEFAULT"]["snusbase_url"],
                api_keys["DEFAULT"]["snusbase_token"],
            )
        finished.append(current_target)

    return finished


def h8mail(user_args):
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
        c.bad_news(c, "No targets found in user input")

    # Launch
    breached_targets = target_factory(targets, api_keys, user_args)

    # These are not done inside the factory as the factory iterates over each target individually
    # The following functions perform line by line checks of all target per line

    if user_args.bc_path:
        breached_targets = breachcomp_check(breached_targets, user_args.bc_path)

    if user_args.local_breach_src:
        res = find_files(user_args.local_breach_src)
        if user_args.single_file:
            local_found = local_search_single(res, targets)
        else:
            local_found = local_search(res, targets)

    if user_args.local_gzip_src:
        res = find_files(user_args.local_gzip_src)
        if user_args.single_file:
            local_found = local_search_single_gzip(res, targets)
        else:
            local_found = local_gzip_search(res, targets)

    breached_targets = local_to_targets(breached_targets, local_found)
    print_results(breached_targets)
    
    if user_args.output_file:
        save_results_csv(user_args.output_file, breached_targets)


def main(user_args):
    h8mail(user_args)


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        sys.stdout.write(
            "\n/!\\ h8mail requires Python 3+. Try running h8mail with python3 /!\\\neg: python3 h8mail.py --help\n\n"
        )
        sys.exit(1)

    # I REALLY want to make sure I don't get Python2 Issues on Github...
    import configparser
    import argparse
    import os
    import re

    from utils.breachcompilation import breachcomp_check
    from utils.classes import target
    from utils.colors import colors as c
    from utils.helpers import (
        fetch_emails,
        find_files,
        get_config_from_file,
        get_emails_from_file,
        print_banner,
        save_results_csv,
    )
    from utils.localsearch import local_search, local_search_single, local_to_targets
    from utils.localgzipsearch import local_gzip_search, local_search_single_gzip

    parser = argparse.ArgumentParser(
        description="Email information and password lookup tool"
    )

    parser.add_argument(
        "-t",
        "--targets",
        required=True,
        dest="target_emails",
        help="Either emails or file",
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config_file",
        default="config.ini",
        help="Configuration file for API keys",
    )
    parser.add_argument(
        "-o", "--output", dest="output_file", help="File to write output"
    )
    parser.add_argument(
        "-bc",
        "--breachcomp",
        dest="bc_path",
        help="Path to the breachcompilation Torrent. Uses the query.sh script included in the torrent. https://ghostbin.com/paste/2cbdn",
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
        help='Pass config options. Format is "K:V,K:V"',
    )
    parser.add_argument(
        "-lb",
        "--local-breach",
        dest="local_breach_src",
        help="Local cleartext breaches to scan for targets. Uses multiprocesses, one separate process per file. Supports file or folder as input",
    )
    parser.add_argument(
        "-sf",
        "--single-file",
        dest="single_file",
        help="If breach contains big cleartext or tar.gz files, set this flag to view the progress bar. Disables concurrent file searching for stability",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-gz",
        "--gzip",
        dest="local_gzip_src",
        help="Local tar.gz (gzip) compressed breaches to scans for targets. Uses multiprocesses, one separate process per file. Supports file or folder as input",
    )

    args = parser.parse_args()
    print_banner("warn")
    print_banner()
    main(args)
    c.good_news(c, "Done")
