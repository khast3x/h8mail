# -*- coding: utf-8 -*-
from .colors import colors as c
import os
import re
import stat
from string import printable


def breachcomp_check(targets, breachcomp_path):
    # https://gist.github.com/scottlinux/9a3b11257ac575e4f71de811322ce6b3
    try:
        import subprocess

        query_bin = os.path.join(breachcomp_path, "query.sh")
        st = os.stat(query_bin)
        os.chmod(query_bin, st.st_mode | stat.S_IEXEC)
        for t in targets:
            c.info_news(f"Looking up {t.target} in BreachCompilation")
            procfd = subprocess.run([query_bin, t.target], stdout=subprocess.PIPE)
            try:
                output = procfd.stdout.decode("cp437")
            except Exception as e:
                c.bad_news(f"Could not decode bytes for {t.target} results")
                output = procfd.stdout
                # print(output[:85], "[...]")
                print(output)
                continue
            if len(output) != 0:
                split_output = output.split("\n")
                for line in split_output:
                    if ":" in line:
                        t.pwned += 1
                        t.data.append(("BC_PASS", re.split("[;:]",line)[-1]))
                        c.good_news(
                            "Found BreachedCompilation entry {line}".format(line=line)
                        )
        return targets
    except Exception as e:
        c.bad_news("Breach compilation")
        print(e)
        return targets
