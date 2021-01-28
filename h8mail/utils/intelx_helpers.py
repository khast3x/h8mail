#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .intelx import intelx as i
from time import sleep
from .colors import colors as c


def intelx_getsearch(target, intelx, maxfile):

    c.info_news("[" + target + "]>[intelx.io] Starting search")
    cap = intelx.GET_CAPABILITIES()
    # print(cap["buckets"])
    # import json
    # print(json.dumps(cap, indent=4))
    c.info_news(
        "["
        + target
        + "]>[intelx.io] Search credits remaining : {creds}".format(
            creds=cap["paths"]["/intelligent/search"]["Credit"]
        )
    )
    available_buckets = []
    desired_buckets=["leaks.public", "leaks.private", "pastes", "darknet"],
    for b in cap["buckets"]:
        if any(b in d for d in desired_buckets):
            available_buckets.append(b)
    c.info_news("[" + target + "]>[intelx.io] Available buckets for h8mail:")
    print(available_buckets)
    c.info_news("[" + target + "]>[intelx.io] Search in progress (max results : "+ str(maxfile) + ")")
    search = intelx.search(
        target,
        buckets=available_buckets,
        maxresults=maxfile,
        media=24,
    )
    c.good_news("[" + target + "]>[intelx.io] Search returned the following files :")
    for record in search["records"]:
        c.good_news("Name: " + record["name"])
        c.good_news("Bucket: " + record["bucket"])
        c.good_news(
            "Size: " + "{:,.0f}".format(record["size"] / float(1 << 20)) + " MB"
        )
        c.info_news("Storage ID: " + record["storageid"])
        print("----------")
    return search
