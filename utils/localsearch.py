#!/usr/bin/env python

import os
from multiprocessing import Pool
from utils.classes import local_breach_target
from utils.colors import colors as c

def local_to_targets(targets, local_results):
    for t in targets:
        for l in local_results:
            if l.email == t.email:
                t.data.append(("LOCALSEARCH", f"[{l.filepath}] Line {l.line}: {l.content}"))
    return targets

def worker(filepath, target_list):
    with open(filepath, "r") as fp:
        found_list = []
        c.info_news(c, f"Searching file {filepath}")
        for cnt, line in enumerate(fp):
            for t in target_list:
                if t in line:
                    found_list.append(local_breach_target(t, filepath, cnt, line))
                    c.good_news(c, f"Found occurrence [{filepath}] Line {cnt}: {line}")
    return found_list

def local_search(files_to_parse ,target_list):
    pool = Pool()
    found_list = []
    for f in files_to_parse:
        async_results = pool.apply_async(worker, args=(f, target_list))
        found_list.extend(async_results.get())
    # for i in found_list:
    #     i.dump()
    pool.close()
    pool.join()
    return found_list
