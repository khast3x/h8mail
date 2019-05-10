from multiprocessing import Pool
from utils.classes import local_breach_target
from utils.colors import colors as c
import gzip


def gzip_worker(filepath, target_list):
    try:
        found_list = []
        with gzip.open(filepath, "r") as gzipfile:
            # for line in enumerate(gzipfile):
            #     print(line)
            for cnt, line in enumerate(gzipfile):
                for t in target_list:
                    if t in str(line):
                        try:
                            decoded = str(line, "utf-8")
                            found_list.append(
                                local_breach_target(t, filepath, cnt, decoded)
                            )
                            c.good_news(
                                c,
                                f"Found occurrence [{filepath}] Line {cnt}: {decoded}",
                            )
                        except Exception as e:
                            c.bad_news(
                                c, f"Got a decoding error line {cnt} - file: {filepath}"
                            )
                            c.good_news(
                                c, f"Found occurrence [{filepath}] Line {cnt}: {line}"
                            )
                            found_list.append(
                                local_breach_target(t, filepath, cnt, str(line))
                            )
        return found_list
    except Exception as e:
        c.bad_news(c, "Something went wrong with gzip worker")
        print(e)


def local_gzip_search(files_to_parse, target_list):
    pool = Pool()
    found_list = []
    for f in files_to_parse:
        async_results = pool.apply_async(gzip_worker, args=(f, target_list))
        if async_results.get() is not None:
            found_list.extend(async_results.get())
    pool.close()
    pool.join()
    return found_list
