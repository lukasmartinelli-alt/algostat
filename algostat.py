#!/usr/bin/env python
"""
Count used algorithms in repos and write them to stdout.
You can pipe in a list of C++ repos to analyze via stdin or use a Redis Queue
to fetch jobs from.

Usage:
    algostat.py [-v] [-t THREADS]
    algostat.py [--rq] [-v]
    algostat.py (-h | --help)

Options:
    -h --help         Show this screen
    -v                Show verbose output
    -t THREADS        How many threads to use in ThreadPool [default: 4]
    --rq              Use Redis Queue from ALGOSTAT_RQ env to fetch jobs
"""
import os
import tempfile
import shutil
import subprocess
import sys
import operator
from collections import Counter
from contextlib import contextmanager
from multiprocessing.dummy import Pool as ThreadPool

from docopt import docopt

from redis import Redis

from algorithm import filter_cpp_files, count_algorithms

VERBOSE = False
HOST_ENV = "ALGOSTAT_RQ_HOST"
PORT_ENV = "ALGOSTAT_RQ_PORT"


class GitRepo:
    def __init__(self, name):
        self.name = name

    def url(self):
        return "https://github.com/" + self.name + ".git"


@contextmanager
def clone(repo):
    """Clone a repository into a temporary directory which gets cleaned
    up afterwards"""
    repo.dir = tempfile.mkdtemp(suffix=repo.name.split("/")[1])
    if VERBOSE:
        print("Cloning {0} into {1}".format(repo.url(), repo.dir))
    with open(os.devnull, "w") as FNULL:
        subprocess.check_call(["git", "clone", repo.url(), repo.dir],
                              stdout=FNULL, stderr=subprocess.STDOUT)
    yield repo
    if VERBOSE:
        print("Cleaning up {0}".format(repo.dir))
    shutil.rmtree(repo.dir)
    del repo.dir


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

    if args["-v"]:
        VERBOSE = True

    jobs = fetch_jobs_stdin()
    if args["--rq"]:
        if not (HOST_ENV in os.environ and PORT_ENV in os.environ):
            sys.stderr.write("Please provide ALGOSTAT_RQ_HOST and ALGOSTAT_RQ_PORT environment variables\n")
            sys.exit(1)
        redis = Redis(host=os.environ[HOST_ENV], port=os.environ[PORT_ENV])
        for repo in fetch_jobs_redis(redis):
            analyze_repo(repo)
    else:
        with ThreadPool(thread_count) as pool:
            pool.map(analyze_repo, jobs)
            pool.join()
