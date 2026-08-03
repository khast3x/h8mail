#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `h8mail` package."""


import unittest
import tempfile
import os
import gzip
from h8mail.utils import run
from h8mail.utils import classes
from h8mail.utils import helpers
from h8mail.utils import localsearch
from h8mail.utils import localgzipsearch

def print_test_banner(testname):
    print("========================")
    print("========================")
    print("\tTESTING: "+testname)
    print("========================")
    print("========================")
    

class TestH8mail(unittest.TestCase):
    """Tests for `h8mail` package."""

    def write_text_file(self, filename, content):
        """Write content to a text file in temp_dir."""
        path = os.path.join(self.temp_path, filename)
        with open(path, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)
        return path
    
    def write_gzip_file(self, filename, content):
        """Write content to a gzip file in temp_dir."""
        path = os.path.join(self.temp_path, filename)
        with gzip.open(path, "wt", encoding="utf-8") as file_handle:
            file_handle.write(content)
        return path

    def setUp(self):
        """Generating local files with automatic cleanup (Python 3.10+)"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name
        print(f"Created Temp Dir: {self.temp_path}")
        print(f"Registering dir + content for auto cleanup: {self.temp_path}")
        
        self.addCleanup(self.temp_dir.cleanup)


        # --- Dummy Data ---
        emails = """
        john.smith@gmail.com
        test@example.com
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

        self.filetargets = self.write_text_file("test-emails.txt", emails)
        self.filetxt = self.write_text_file("test-creds.txt", creds)
                
        self.filegz = self.write_gzip_file("test-creds.txt.gz", creds)
            
        print(f"Test files generated in : {self.temp_path}")


    @unittest.skipUnless(
        os.getenv("RUN_INTEGRATION_TEST") == "1",
        "Skipping integration test by default. Set RUN_INTEGRATION_TEST=1 to run."
    )
    def test_000_simple_integration_test(self):
        """Simple integration test"""
        run.print_banner()
        print_test_banner("VANILLA")

        user_args = run.parse_args(["-t", "test@example.com"])
        run.h8mail(user_args)

    def test_001_cleartext_local_search_returns_exact_matches(self):
        """Clear-text searches return structured matches without network access."""
        results = localsearch.local_search_single(
            [self.filetxt],
            ["john.smith@gmail.com", "missing@example.com"],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].target, "john.smith@gmail.com")
        self.assertEqual(results[0].filepath, self.filetxt)
        self.assertEqual(results[0].line, 1)
        self.assertEqual(
            results[0].content.strip(),
            "john.smith@gmail.com:SecretPASS",
        )

    def test_002_gzip_local_search_returns_exact_matches(self):
        """Gzip searches return structured matches without network access."""
        results = localgzipsearch.local_search_single_gzip(
            [self.filegz],
            ["test@evilcorp.com", "missing@example.com"],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].target, "test@evilcorp.com")
        self.assertEqual(results[0].filepath, self.filegz)
        self.assertEqual(results[0].line, 4)
        self.assertEqual(
            results[0].content.strip(),
            "test@evilcorp.com:An0therSECRETpassw0rd",
        )

    def test_003_local_results_are_added_to_matching_targets_only(self):
        """Local results preserve their source and update only matching targets."""
        matched = classes.target("john.smith@gmail.com")
        unmatched = classes.target("missing@example.com")
        local_result = classes.local_breach_target(
            "john.smith@gmail.com",
            self.filetxt,
            1,
            "john.smith@gmail.com:SecretPASS\n",
        )
        user_args = run.parse_args(["-t", "john.smith@gmail.com", "-sk"])

        results = localsearch.local_to_targets(
            [matched, unmatched],
            [local_result],
            user_args,
        )

        self.assertIs(results[0], matched)
        self.assertEqual(matched.pwned, 1)
        self.assertEqual(unmatched.pwned, 0)
        self.assertEqual(
            matched.data[-1],
            (
                "LOCALSEARCH",
                "[test-creds.txt] Line 1: john.smith@gmail.com:SecretPASS",
                "john.smith@gmail.com:SecretPASS",
            ),
        )

    def test_004_parse_args_accepts_local_search_options(self) -> None:
        """Verify CLI argument parser correctly assigns local search flags."""
        arguments = run.parse_args(
            [
                "-t",
                "john.smith@gmail.com",
                "test@example.com",
                "-lb",
                "/tmp/synthetic-breach.txt",
                "-sk",
                "-sf",
            ]
        )

        self.assertEqual(
            arguments.user_targets,
            ["john.smith@gmail.com", "test@example.com"],
        )
        self.assertEqual(
            arguments.local_breach_src,
            ["/tmp/synthetic-breach.txt"],
        )
        self.assertTrue(arguments.skip_defaults)
        self.assertTrue(arguments.single_file)
        self.assertIsNone(arguments.user_urls)

    def test_005_parse_args_uses_safe_expected_defaults(self):
        """Verify CLI argument parser defaults to safe, expected values when given only a target."""
        arguments = run.parse_args(["-t", "john.smith@gmail.com"])
        self.assertFalse(arguments.skip_defaults)
        self.assertFalse(arguments.single_file)
        self.assertFalse(arguments.loose)
        self.assertFalse(arguments.debug)
        self.assertIsNone(arguments.output_file)
        self.assertIsNone(arguments.output_json)

    def test_006_parse_args_accepts_single_target(self) -> None:
        """Verify CLI argument parser correctly assigns a single email target."""
        arguments = run.parse_args(["-t", "john.smith@gmail.com"])

        self.assertEqual(arguments.user_targets, ["john.smith@gmail.com"])
        self.assertIsNone(arguments.local_breach_src)
        self.assertIsNone(arguments.user_urls)

    @unittest.skipUnless(
        os.getenv("RUN_INTEGRATION_TEST") == "1",
        "Skipping integration test by default. Set RUN_INTEGRATION_TEST=1 to run.",
    )
    def test_007_url(self):
        """Fetch targets from a live URL."""
        run.print_banner()
        print_test_banner("URL-RAW")
        user_args_lb = run.parse_args(["-u", "https://raw.githubusercontent.com/khast3x/h8mail/master/tests/test_email.txt"])
        run.h8mail(user_args_lb)
        run.print_banner()
        print_test_banner("URL-MESSY")
        user_args_lb = run.parse_args(["-u", "https://raw.githubusercontent.com/khast3x/h8mail/master/tests/test_email.txt"])
        run.h8mail(user_args_lb)
