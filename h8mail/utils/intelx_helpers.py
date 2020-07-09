#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .intelx import intelx as i
from time import sleep
from .colors import colors as c


def intelx_getsearch(target, intelx, maxfile):

    c.info_news("[" + target + "]>[intelx.io]")
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
    c.info_news("[" + target + "]>[intelx.io] Search in progress (" + str(maxfile) + " results max)")
    search = intelx.search(
        target,
        buckets=["leaks.public", "leaks.private", "pastes"],
        maxresults=maxfile,
        media=24,
    )
    c.good_news("[" + target + "]>[intelx.io] Search returned the following files:\n")
    for record in search["records"]:
        c.good_news("Name: " + record["name"])
        c.good_news("Bucket: " + record["bucket"])
        c.good_news(
            "Size: " + "{:,.0f}".format(record["size"] / float(1 << 20)) + " MB"
        )
        c.info_news("SID: " + record["storageid"])
        print("------")
    return search
