#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from multiprocessing import Pool
from itertools import takewhile, repeat
from .classes import local_breach_target
from .colors import colors as c


def local_to_targets(targets, local_results):
    """
    Appends data from local_breach_target objects using existing list of targets.
    Finds corresponding email in dest object list, and adds data to the t.data object variable.
    Full output line is stored in t.data[1] and original found data in t.data[2]
    
    """
    for t in targets:
        for l in local_results:
            if l.email == t.email:
                t.data.append(
                    (
                        "LOCALSEARCH",
                        f"[{os.path.basename(l.filepath)}] Line {l.line}: {l.content}".strip(),
                        l.content.strip(),
                    )
                )
                t.pwned = True
    return targets


def raw_in_count(filename):
    """
    StackOverflow trick to rapidly count lines in big files.
    Returns total line number.
    """
    c.info_news("Identifying total line number...")
    f = open(filename, "rb")
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
    return sum(buf.count(b"\n") for buf in bufgen)


def worker(filepath, target_list):
    """
    Searches for every email from target_list in every line of filepath.
    Attempts to decode line using utf-8. If it fails, catch and use raw data
    """
    try:
        with open(filepath, "rb") as fp:
            found_list = []
            size = os.stat(filepath).st_size
            c.info_news(
                "Worker [{PID}] is searching for targets in {filepath} ({size} bytes)".format(
                    PID=os.getpid(), filepath=filepath, size=size
                )
            )
            for cnt, line in enumerate(fp):
                for t in target_list:
                    if t in str(line):
                        try:
                            decoded = str(line, "utf-8")
                            found_list.append(
                                local_breach_target(t, filepath, cnt, decoded)
                            )
                            c.good_news(
                                f"Found occurrence [{filepath}] Line {cnt}: {decoded}"
                            )
                        except Exception as e:
                            c.bad_news(
                                f"Got a decoding error line {cnt} - file: {filepath}"
                            )
                            c.good_news(
                                f"Found occurrence [{filepath}] Line {cnt}: {line}"
                            )
                            found_list.append(
                                local_breach_target(t, filepath, cnt, str(line))
                            )
        return found_list
    except Exception as e:
        c.bad_news("Something went wrong with worker")
        print(e)


def local_search(files_to_parse, target_list):
    pool = Pool()
    found_list = []
    async_results = [
        pool.apply_async(worker, args=(f, target_list))
        for i, f in enumerate(files_to_parse)
    ]
    for r in async_results:
        if r.get() is not None:
            found_list.extend(r.get())
    pool.close()
    pool.join()
    return found_list


import sys


def progress(count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", status))
    sys.stdout.write("\033[K")


sys.stdout.flush()


def local_search_single(files_to_parse, target_list):
    found_list = []
    for file_to_parse in files_to_parse:
        with open(file_to_parse, "rb") as fp:
            size = os.stat(file_to_parse).st_size
            lines_no = raw_in_count(file_to_parse)
            c.info_news(
                "Searching for targets in {file_to_parse} ({size} bytes, {lines_no} lines)".format(
                    file_to_parse=file_to_parse, size=size, lines_no=lines_no
                )
            )
            for cnt, line in enumerate(fp):
                lines_left = lines_no - cnt
                progress(
                    cnt, lines_no, f"{cnt} lines checked - {lines_left} lines left"
                )
                for t in target_list:
                    if t in str(line):
                        try:
                            decoded = str(line, "utf-8")
                            found_list.append(
                                local_breach_target(t, file_to_parse, cnt, decoded)
                            )
                            c.good_news(
                                f"Found occurrence [{file_to_parse}] Line {cnt}: {decoded}"
                            )
                        except Exception as e:
                            c.bad_news(
                                f"Got a decoding error line {cnt} - file: {file_to_parse}"
                            )
                            c.good_news(
                                f"Found occurrence [{file_to_parse}] Line {cnt}: {line}"
                            )
                            found_list.append(
                                local_breach_target(t, file_to_parse, cnt, str(line))
                            )
    return found_list
