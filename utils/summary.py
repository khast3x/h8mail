import time
from utils.colors import colors as c

def print_summary(start_time, breached_targets):
    for t in breached_targets:
        if t.pwned:
            print(f"{t.email} - ", c.fg.green, "Breach Found", c.reset)
        else:
            print(f"{t.email} - ", c.fg.lightgrey, "No Data")
    total_time = time.time() - start_time
    print(f"Execution time: {total_time}")