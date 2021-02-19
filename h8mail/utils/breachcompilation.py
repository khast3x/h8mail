# -*- coding: utf-8 -*-
from .colors import colors as c
import os
import re
import stat
from string import printable


def check_shell():
    shell = os.environ['SHELL']
    print("SHELL IS " + shell)
    if "bash" not in shell:
        c.info_news("If you're having issues or not results, be sure to launch h8mail using bash for this operation.")
        c.info_news("OSX users should read this https://khast3x.club/posts/2021-02-17-h8mail-with-COMB/#targeting-emails\n")


def breachcomp_check(targets, breachcomp_path):
    # https://gist.github.com/scottlinux/9a3b11257ac575e4f71de811322ce6b3
    try:
        import subprocess

        check_shell()
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
                            f"Found BreachedCompilation entry {line}"
                        )
        return targets
    except Exception as e:
        c.bad_news("Breach compilation")
        print(e)
        return targets
