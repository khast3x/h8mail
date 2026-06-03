#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Packaging tests for h8mail."""

import runpy
import unittest
from pathlib import Path
from unittest.mock import patch


class TestPackaging(unittest.TestCase):
    def test_root_tests_package_is_not_installed(self):
        captured = {}

        def fake_setup(**kwargs):
            captured.update(kwargs)

        setup_path = Path(__file__).resolve().parents[1] / "setup.py"
        with patch("setuptools.setup", fake_setup):
            runpy.run_path(str(setup_path), run_name="__main__")

        self.assertIn("h8mail", captured["packages"])
        self.assertNotIn("tests", captured["packages"])


if __name__ == "__main__":
    unittest.main()
