#!/usr/bin/env python

import os
import threading
from collections import deque
import queue

# def locate_emails(targetfile, targets):
#     with open(targetfile) as fd:
#         print("lol")


def breach_search(targets, q, q_found):
    while True:
        item = q.get()
        if item is None:
            break
        print(item)
        if ".py" in item:
                q_found.put(item)
        q.task_done()



# Should receive queue of files, max worker num, targets
# for each line, test all targets

def local_search(allfiles, targets, thread_num):
    q = queue.Queue()
    q.queue = queue.deque(allfiles)
    q_found = queue.Queue()

    threads = []
    for i in range(thread_num):
        t = threading.Thread(target=breach_search, args=(targets, q, q_found))
        t.start()
        threads.append(t)
    # block until all tasks are done
    q.join()
    # stop workers
    for i in range(thread_num):
        q.put(None)
    for t in threads:
        t.join()
    print("---------")
    print(list(q_found.queue))