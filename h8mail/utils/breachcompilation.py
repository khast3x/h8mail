# -*- coding: utf-8 -*-
from .colors import colors as c
import os


def breachcomp_check(targets, breachcomp_path):
    # https://gist.github.com/scottlinux/9a3b11257ac575e4f71de811322ce6b3
    try:
        import subprocess

        c.info_news("Looking up targets in BreachCompilation")
        query_bin = os.path.join(breachcomp_path, "query.sh")
        subprocess.call(["chmod", "+x", query_bin])
        for t in targets:
            procfd = subprocess.run([query_bin, t.email], stdout=subprocess.PIPE)
            try:
                output = procfd.stdout.decode("utf-8")
            except Exception as e:
                c.bad_news(f"Could not decode bytes for {t.email} results")
                output = procfd.stdout
                print(output[:85], "[...]")
                continue
            if len(output) != 0:
                split_output = output.split("\n")
                for line in split_output:
                    if ":" in line:
                        t.data.append(("BC_PASS", line.split(":")[1]))
                        c.good_news(
                            "Found BreachedCompilation entry {line}".format(line=line)
                        )
        return targets
    except Exception as e:
        c.bad_news("Breach compilation")
        print(e)
