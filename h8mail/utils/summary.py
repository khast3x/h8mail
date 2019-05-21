# -*- coding: utf-8 -*-

import time
from .colors import colors as c


def print_summary(start_time, breached_targets):
    """
    Prints a padded table where each line is a target, and associated value is simplified to breached/not breached.
    If breached, shows len(t.data). Shown elements and total may differ as some elements of t.data are not outputted to stdout.
    """
    print("{:_^90}".format(""))
    print(
        "\n\n\n{:^32}".format(""),
        c.bold,
        c.underline,
        "Session Recap:",
        c.reset,
        "\n\n",
    )
    print("{:^40} | ".format("Target"), "{:^40}".format("Status"), c.reset)
    print("{:_^90}\n".format(""))
    for t in breached_targets:
        if t.pwned:
            print(
                f"{t.email:^40} | ",
                c.fg.green,
                "{:^40}".format("Breach Found (" + str(len(t.data)) + " elements)"),
                c.reset,
            )
        else:
            print(
                f"{t.email:^40} | ",
                c.fg.lightgrey,
                "{:^40}".format("Not Compromised"),
                c.reset,
            )
        print("{:_^90}\n".format(""))
    total_time = time.time() - start_time
    print("Execution time (seconds): ", c.fg.lightcyan, f"{total_time}", c.reset, "\n")
