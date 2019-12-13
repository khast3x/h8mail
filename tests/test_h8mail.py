#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `h8mail` package."""


import unittest
import sys
import time
import tempfile
import shutil
import contextlib
import os
import tarfile
import argparse
from h8mail.utils import run
from h8mail.utils import classes
from h8mail.utils import helpers
from h8mail.utils import localsearch
from h8mail.utils import localgzipsearch


@contextlib.contextmanager
def gen_arparse():
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
        help="Configuration file for API keys. Accepts keys from Snusbase, WeLeakInfo, Leak-Lookup, HaveIBeenPwned and hunterio",
        nargs="+",
    )
    parser.add_argument(
        "-o", "--output", dest="output_file", help="File to write CSV output"
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
        help="Add related emails from hunter.io to ongoing target list. Define number of emails per target to chase. Requires hunter.io private API key",
        type=int,
        nargs="?",
    ),
    parser.add_argument(
        "--power-chase",
        dest="power_chase",
        help="Add related emails from ALL API services to ongoing target list. Use with --chase. Requires a private API key",
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
    )
    # user_args = parser.parse_args()
    # yield user_args


@contextlib.contextmanager
def make_temp_directory():
    emails = """
    john.smith@gmail.com
    john.smith@gmail.com
    fijsdhkfnhqsdkf
    fdqfqsdff
    test@evilcorp.com
    notfound@email.com
    """
    creds = """
    john.smith@gmail.com:SecretPASS
    bloblfd
    fjsdkf,ds
    test@evilcorp.com:An0therSECRETpassw0rd
    ddqsdqs
    """
    temp_dir = tempfile.mkdtemp()
    try:
        fd_creds = open(os.path.join(temp_dir, "test-creds.txt"), "w")
        fd_creds.write(creds)
        fd_creds.close()
        fd_emails = open(os.path.join(temp_dir, "test-emails.txt"), "w")
        fd_emails.write(emails)
        tar = tarfile.open(os.path.join(temp_dir, "test-creds.tar"), "w")
        tar.add(os.path.join(temp_dir, "test-creds.txt"))
        tar.close()
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


class TestH8mail(unittest.TestCase):
    """Tests for `h8mail` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_simple(self):
        """Test something."""

    run.print_banner()
    start_time = time.time()
    # target = classes.target("test@test.ca")
    # target.get_emailrepio()
    # target.get_hunterio_public()
    # if helpers.check_scylla_online():
    #     target.get_scylla()
    # run.print_results([target])
    # run.print_summary(start_time, [target])

    def test_002(self):
        with make_temp_directory() as temp_dir:
            with gen_arparse() as user_sssargs:
                filetargets = os.path.join(temp_dir, "test-emails.txt")
                filetxt = os.path.join(temp_dir, "test-creds.txt")
                filegz = os.path.join(temp_dir, "test-creds.gz")
                run.print_banner()
                user_args.user_targets = filetargets
                # user_args.local_breach_src = filetxt
                # user_args.local_gzip_src = filegz
                # run.h8mail(user_args)

