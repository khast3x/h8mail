#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `h8mail` package."""


import unittest

from h8mail.utils import run
from h8mail.utils import classes
from h8mail.utils import helpers
import sys
import time


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
    target = classes.target("test@test.ca")
    target.get_emailrepio()
    target.get_hunterio_public()
    if helpers.check_scylla_online():
        target.get_scylla()
    run.print_results([target])
    run.print_summary(start_time, [target])
