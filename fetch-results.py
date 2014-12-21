#!/usr/bin/env python
"""
Append results from stdin to a Redis list
"""
import sys

from rq import RedisQueue

if __name__ == '__main__':
    rq = RedisQueue.from_config()
    for result in rq.fetch_results():
        sys.stdout.write(result + "\n")
