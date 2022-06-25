# -*- coding: utf-8 -*-
from .colors import colors as c
import os
import re
import stat
from string import printable
from .localsearch import local_search

def check_shell():
    shell = os.environ['SHELL']
    print("SHELL IS " + shell)
    if "bash" not in shell:
        c.info_news("If you're having issues or not results, be sure to launch h8mail using bash for this operation.")
        c.info_news("OSX users should read this https://khast3x.club/posts/2021-02-17-h8mail-with-COMB/#targeting-emails\n")


def clean_targets(targets):
    """
    This function is necessary since local_search performs a loose search.
    We'll double check results to ensure ONLY target email is present is results
    """
    for t in targets:
        cleaned_data = []
        for d in t.data:
            if d:
                found_email = re.split("[;:]",d[1])[0]
                if found_email == t.target:
                    # We rebuild the expected data array ["BC_PASS", "password"]
                    new_data = [d[0], re.split("[;:]",d[1])[-1]]
                    cleaned_data.append(new_data)
                else:
                    c.info_news("Removing " + d[1] + " (cleaning function)")
        t.data = cleaned_data

    return targets

def breachcomp_check(targets, breachcomp_path):
    breachcomp_path =  os.path.join(breachcomp_path, "data")
    for t in targets:
        if len(t.target):
            for i in range(len(t.target)):
                if t.target[i].isalnum():
                    next_dir_to_test = os.path.join(breachcomp_path, t.target[i])
                else:
                    next_dir_to_test = os.path.join(breachcomp_path, "symbols")
                if os.path.isdir(next_dir_to_test):
                    breachcomp_path = next_dir_to_test
                else:
                    if os.path.isfile(next_dir_to_test):
                        found_list = local_search([next_dir_to_test], [t.target])
                        for f in found_list:
                            t.pwned += 1
                            t.data.append(("BC_PASS", f.content.strip()))
                    else:
                        c.bad_news(next_dir_to_test + " is neither a file or directory")
                        
                    break

    targets = clean_targets(targets)
    return targets

def old_breachcomp_check(targets, breachcomp_path):
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
