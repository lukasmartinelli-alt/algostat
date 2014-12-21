#!/usr/bin/env python
"""
Count used algorithms in repos and write them to stdout.
You can pipe in a list of C++ repos to analyze via stdin or use a Redis Queue
to fetch jobs from.

Usage:
    algostat.py [--rq] [-v] [-t THREADS]
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

from algorithm import filter_cpp_files, count_algorithms


VERBOSE = False


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
    for cpp_path in filter_cpp_files(repo):
        repo_algorithms += count_algorithms(cpp_path)
    return repo_algorithms


def print_stats(repo, used_algorithms):
    """Print occurrences stats of algorithms for repo"""
    sorted_items = sorted(used_algorithms.items(),
                          key=operator.itemgetter(1),
                          reverse=True)
    counts = ["{0}:{1}".format(algo, count) for algo, count in sorted_items]
    print(" ".join([repo.name] + counts))


def analyze_repo(repo):
    """Count algorithms for repo"""
    try:
        with clone(repo) as local_repo:
            repo_algorithms = count_repo_algorithms(local_repo)
            if len(repo_algorithms) > 0:
                print_stats(repo, repo_algorithms)
            return repo_algorithms
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        return Counter()


def fetch_jobs():
    for line in sys.stdin:
        yield GitRepo(line.strip())


if __name__ == '__main__':
    args = docopt(__doc__)
    thread_count = int(args["-t"])

    if args["-v"]:
        VERBOSE = True

    with ThreadPool(thread_count) as pool:
        pool.map(analyze_repo, fetch_jobs())
        pool.join()
