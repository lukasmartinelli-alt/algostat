#!/usr/bin/env python
"""
Append jobs from stdin to a Redis list
"""
import sys

from rq import RedisQueue

if __name__ == '__main__':
    rq = RedisQueue.from_config()
    for line in sys.stdin:
        repo_name = line.strip()
        sys.stdout.write(repo_name + "\n")
        rq.put_job(repo_name)
