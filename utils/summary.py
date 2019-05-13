import time
from utils.colors import colors as c


def print_summary(start_time, breached_targets):
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
                "{:^40}".format("Breach Found"),
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
