#!/usr/bin/env python
"""
Find the most frequently used algorithms of the C++ standard library for
C++ projects on Github.

Usage:
    algostat.py -u USERNAME -p=PASSWORD [-v] [-t THREADS]
    algostat.py (-h | --help)

Options:
    -h --help         Show this screen
    -v                Show verbose output
    -t THREADS        How many threads to use in ThreadPool [default: 4]
    -u USERNAME       Github Account to make API requests with
    -p PASSWORD       Password or OAuth token of your Github Account
"""
import os
import tempfile
import shutil
import subprocess
import sys
import operator
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from collections import Counter
from contextlib import contextmanager

import requests
from requests.auth import HTTPBasicAuth

from docopt import docopt

from algorithm import filter_cpp_files, count_algorithms


VERBOSE=False


class GitRepo:
    def __init__(self, name, git_url):
        self.name = name
        self.git_url = git_url


@contextmanager
def clone(repo):
    """Clone a repository into a temporary directory which gets cleaned
    up afterwards"""
    try:
        repo.dir = tempfile.mkdtemp(suffix=repo.name.split("/")[1])
        if VERBOSE:
            print("Cloning {0} into {1}".format(repo.git_url, repo.dir))
        with open(os.devnull, "w") as FNULL:
            subprocess.check_call(["git", "clone", repo.git_url, repo.dir],
                                   stdout=FNULL, stderr=subprocess.STDOUT)
        yield repo
    finally:
        if VERBOSE:
            print("Cleaning up {0}".format(repo.dir))
        shutil.rmtree(repo.dir)
        del repo.dir


def get_cpp_repositories(make_request):
    """Search for the top 1000 cpp repos in github and return their git url"""
    url = "https://api.github.com/search/repositories?q=language:cpp&per_page=100"
    response = make_request(url)

    while "next" in response.links.keys():
        url = response.links["next"]["url"]
        response = make_request(url)

        for repo in response.json()["items"]:
            yield GitRepo(repo["full_name"], repo["git_url"])


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
        with clone(repo)  as local_repo:
            repo_algorithms = count_repo_algorithms(local_repo)
            if len(repo_algorithms) > 0:
                print_stats(repo, repo_algorithms)
            return repo_algorithms
    except subprocess.CalledProcessError:
        return Counter()

if __name__ == '__main__':
    args = docopt(__doc__)
    thread_count = int(args["-t"])

    if args["-v"]:
        VERBOSE = True

    def make_request(url):
        headers = {"Accept": "application/vnd.github.v3+json"}
        auth=HTTPBasicAuth(args["-u"], args["-p"])

        if VERBOSE:
            print("Get {0}".format(url))

        return requests.get(url, headers=headers, auth=auth)

    pool = ThreadPool(thread_count)
    analyzed_repos = pool.map(analyze_repo, get_cpp_repositories(make_request))
    pool.close()
    pool.join()
