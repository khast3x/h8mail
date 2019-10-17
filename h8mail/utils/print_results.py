# -*- coding: utf-8 -*-
from .colors import colors as c
from time import sleep

def print_results(results, hide=False):

    for t in results:
        print()
        c.print_res_header(t.target)
        for i in range(len(t.data)):
            sleep(0.001)
            if len(t.data) == 1:
                print()
                c.info_news("No results founds")
                continue
            if len(t.data[i]) >= 2:  # Contains header + body data
                if hide:
                    if "PASS" in t.data[i][0]:
                        c.print_result(
                            t.target, t.data[i][1][:4] + "********", t.data[i][0]
                        )
                        continue
                    if "LOCAL" in t.data[i][0]:
                        c.print_result(
                            t.target, t.data[i][1][:-5] + "********", t.data[i][0]
                        )
                        continue
                if "HIBP" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "HUNTER_PUB" in t.data[i][0]:
                    c.print_result(
                        t.target, str(t.data[i][1]) + " RELATED EMAILS", "HUNTER_PUB"
                    )
                if "HUNTER_RELATED" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], "HUNTER_RELATED")
                if "EMAILREP" in t.data[i][0]:
                    c.print_result(
                        t.target, str(t.data[i][1]).capitalize(), t.data[i][0]
                    )
                if "SNUS" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "LOCAL" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "BC_PASS" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "LEAKLOOKUP" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "LKLP" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "WLI" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
                if "SCYLLA" in t.data[i][0]:
                    c.print_result(t.target, t.data[i][1], t.data[i][0])
    
