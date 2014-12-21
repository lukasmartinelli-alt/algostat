#!/usr/bin/env python
"""
Count used algorithms in repos and write them to stdout.
You can pipe in a list of C++ repos to analyze via stdin or use a Redis Queue
to fetch jobs from.

Usage:
    algostat.py [-t THREADS]
    algostat.py [--rq]
    algostat.py (-h | --help)

Options:
    -h --help         Show this screen
    -t THREADS        How many threads to use in ThreadPool [default: 4]
    --rq              Use Redis Queue from ALGOSTAT_RQ env to fetch jobs
"""
import os
import sys
import operator
from collections import Counter
from multiprocessing.dummy import Pool as ThreadPool

from docopt import docopt

from rq import RedisQueue
from algorithm import filter_cpp_files, count_algorithms
from repo import clone, GitRepo

VERBOSE = "ALGOSTAT_VERBOSE" in os.environ


def count_repo_algorithms(repo):
    """Count all algorithms in a repository"""
    repo_algorithms = Counter()
    for cpp_file in filter_cpp_files(repo):
        if VERBOSE:
            print("Analyzing {0}".format(cpp_file.name))
        repo_algorithms += count_algorithms(cpp_file)
    return repo_algorithms


def write_stats(repo, used_algorithms):
    """Print occurrences stats of algorithms for repo"""
    sorted_items = sorted(used_algorithms.items(),
                          key=operator.itemgetter(1),
                          reverse=True)
    counts = ["{0}:{1}".format(algo, count) for algo, count in sorted_items]
    sys.stdout.write(" ".join([repo.name] + counts) + "\n")


def analyze_repo(repo):
    """Count algorithms for repo"""
    try:
        with clone(repo) as local_repo:
            repo_algorithms = count_repo_algorithms(local_repo)
            if len(repo_algorithms) > 0:
                write_stats(repo, repo_algorithms)
            return repo_algorithms
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        return Counter()


def fetch_jobs_stdin():
    for line in sys.stdin:
        yield GitRepo(line.strip())


def fetch_jobs_redis(redis):
    while redis.llen("jobs") > 0:
        repo_name = redis.lpop("jobs").decode("utf-8")
        yield GitRepo(repo_name)


if __name__ == '__main__':
    args = docopt(__doc__)
    thread_count = int(args["-t"])

    if args["--rq"]:
        rq = RedisQueue.from_config()
        for repo in rq.fetch_jobs():
            analyze_repo(repo)
    else:
        with ThreadPool(thread_count) as pool:
            jobs = fetch_jobs_stdin()
            pool.map(analyze_repo, jobs)
            pool.join()
