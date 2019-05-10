from utils.colors import colors as c
import os

def breachcomp_check(targets, breachcomp_path):
    # https://gist.github.com/scottlinux/9a3b11257ac575e4f71de811322ce6b3
    try:
        import subprocess

        query_bin = os.path.join(breachcomp_path, "query.sh")
        subprocess.call(["chmod", "+x", query_bin])
        for t in targets:
            procfd = subprocess.run([query_bin, t.email], stdout=subprocess.PIPE)
            output = procfd.stdout.decode("utf-8")
            if len(output) != 0:
                split_output = output.split("\n")
                for line in split_output:
                    if ":" in line:
                        t.data.append(("BREACHEDCOMP", line.split(":")[1]))
        return targets
    except Exception as ex:
        c.bad_news(c, "Breach compilation")
        print(ex)
