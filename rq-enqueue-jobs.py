#!/usr/bin/env python
"""
Append jobs from stdin to a Redis list
"""
import os
import sys
import fileinput

from redis import Redis


HOST_ENV = "ALGOSTAT_RQ_HOST"
PORT_ENV = "ALGOSTAT_RQ_PORT"

if __name__ == '__main__':
    if not (HOST_ENV in os.environ and PORT_ENV in os.environ):
        sys.stderr.write("Please provide ALGOSTAT_RQ_HOST and ALGOSTAT_RQ_PORT environment variables\n")
        sys.exit(1)

    redis = Redis(host=os.environ[HOST_ENV], port=os.environ[PORT_ENV])
    for line in fileinput.input():
        repo_name = line.strip().encode('utf-8')
        redis.rpush("jobs", repo_name)
