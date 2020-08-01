# -*- coding: utf-8 -*-

from multiprocessing import Pool
from .classes import local_breach_target
from .colors import colors as c
from .localsearch import raw_in_count, progress
import io
import os
import sys
import signal
import zstandard as zstd


def progress_zstd(count):
    """
    Prints count without rewriting to stdout
    """
    sys.stdout.write("Lines checked:%i\r" % (count))
    sys.stdout.write("\033[K")


def zstd_worker(filepath, target_list):
    """
    Searches for every email from target_list in every line of filepath.
    Uses python zstandard bindings to decompress file line by line.
    Archives with multiple files are read as long single files.
    Attempts to decode line using cp437. If it fails, catch and use raw data.
    """
    try:
        found_list = []
        size = os.stat(filepath).st_size
        with open(filepath, "rb") as breach_file:
            dctx = zstd.ZstdDecompressor()
            stream_reader = dctx.stream_reader(breach_file)
            zstdfile = io.TextIOWrapper(stream_reader, encoding='utf-8', errors='replace')
            c.info_news(
                "Worker [{PID}] is searching for targets in {filepath} ({size:,.0f} MB)".format(
                    PID=os.getpid(), filepath=filepath, size=size / float(1 << 20)
                )
            )
            for cnt, line in enumerate(zstdfile):
                for t in target_list:
                    if t in str(line):
                        c.good_news(
                            f"Found occurrence [{filepath}] Line {cnt}: {line}"
                        )
                        found_list.append(
                            local_breach_target(t, filepath, cnt, str(line))
                        )
        return found_list
    except Exception as e:
        c.bad_news("Something went wrong with zstd worker")
        print(e)


def local_zstd_search(files_to_parse, target_list):
    """
    Receives list of all files to check for target_list.
    Starts a worker pool, one worker per file.
    Return list of local_breach_targets objects to be tranformed in target objects.
    """
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool()
    found_list = []
    signal.signal(signal.SIGINT, original_sigint_handler)
    # Launch
    try:
        async_results = [
            pool.apply_async(zstd_worker, args=(f, target_list))
            for i, f in enumerate(files_to_parse)
        ]
        for r in async_results:
            if r.get() is not None:
                found_list.extend(r.get(60))
    except KeyboardInterrupt:
        c.bad_news("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        c.info_news("Terminating worker pool")
        pool.close()
    pool.join()
    return found_list


def local_search_single_zstd(files_to_parse, target_list):
    """
    Single process searching of every target_list emails, in every files_to_parse list.
    To be used when stability for big files is a priority
    Return list of local_breach_target objects to be tranformed in target objects
    """
    found_list = []
    for file_to_parse in files_to_parse:
        with open(file_to_parse, "rb") as breach_file:
            dctx = zstd.ZstdDecompressor()
            stream_reader = dctx.stream_reader(breach_file)
            zstdfile = io.TextIOWrapper(stream_reader, encoding= 'utf-8', errors='replace')
            size = os.stat(file_to_parse).st_size
            c.info_news(
                f"Searching for targets in {file_to_parse} ({size} bytes)"
            )
            for cnt, line in enumerate(zstdfile):
                progress_zstd(cnt)
                for t in target_list:
                    if t in str(line):
                        c.good_news(
                            f"Found occurrence [{file_to_parse}] Line {cnt}: {line}"
                        )
                        found_list.append(
                            local_breach_target(t, file_to_parse, cnt, str(line))
                        )
    return found_list
