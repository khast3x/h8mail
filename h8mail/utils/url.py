#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import requests

from .colors import colors as c
from .version import __version__
from .helpers import get_emails_from_file

def fetch_urls(target):
    """
    Returns a list of URLs found in 'target'.
    """
    # https://www.geeksforgeeks.org/python-check-url-string/
    e = re.findall(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        target,
    )
    if e:
        # print(", ".join(e), c.reset)
        return e
    return None


def get_urls_from_file(targets_file):
    """
    For each line in file, check for URLs using fetch_urls()(todo).
    Returns list of URLs.
    """
    email_obj_list = []
    c.info_news("Parsing urls from " + targets_file)
    try:
        target_fd = open(targets_file).readlines()
        for line in target_fd:
            e = fetch_urls(line)
            if e is None:
                continue
            else:
                email_obj_list.extend(e)
        return email_obj_list
    except Exception as ex:
        c.bad_news("Problems occurred while trying to get URLs from file")
        print(ex)



def worker_url(url, tmpdir):
    """
    Fetches the URL without the h8mail UA
    Saves result to tempdir
    """
    paramsUA = {"User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/71.0"}
    try:
        r = requests.get(url, params = paramsUA, allow_redirects=True)
        # use r.text and save to tempfile
        fname = url + ".html"
        fname = fname.replace("/", "")
        dest = os.path.join(tmpdir, fname)
        if r.status_code == 200:
            fd = open(dest, "w")
            fd.write(r.text)
            fd.close()
            c.good_news("Fetched URL " + url + " (" + tmpdir + ")")

        return dest
    except Exception as ex:
        c.bad_news("URL fetch worker error:")
        print(ex)


def target_urls(user_args, tmpdir):
    """
    For each user input with --url, check if its a file.
    If yes open and parse each line with regexp, else parse the input with regexp directly.
    Uses a temp dir to download & parse html pages from URLs.
    Returns list of email targets
    """
    try:
        c.info_news("Starting URL fetch")
        urls = []
        emails = []
        for arg in user_args.user_urls:
            if os.path.isfile(arg):
                e = get_urls_from_file(arg)
            else:
                e = fetch_urls(arg)
            if e is None:
                continue
            else:
                urls.extend(e)
        
        for url in urls:
            tmpfile = worker_url(url, tmpdir)
            e = get_emails_from_file(tmpfile, user_args)
            if e is None:
                continue
            else:
                emails.extend(e)

        return emails
    except Exception as ex:
        c.bad_news("URL fetch error:")
        print(ex)

