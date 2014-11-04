#!/usr/bin/env python
"""
Find the most frequently used algorithms of the C++ standard library for
C++ projects on Github.

Usage:
    algostat.py -u USERNAME -p=PASSWORD
    algostat.py (-h | --help)

Options:
    -h --help         Show this screen
    -u USERNAME       Github Account to make API requests with
    -p PASSWORD       Password or OAuth token of your Github Account
"""
import os
import tempfile
import shutil
import subprocess
import signal
import sys
from pathlib import Path
from collections import Counter
from contextlib import contextmanager

import requests
from requests.auth import HTTPBasicAuth

from docopt import docopt

from algorithm import filter_cpp_files, count_algorithms


class GitRepo:
    def __init__(self, name, git_url):
        self.name = name
        self.git_url = git_url


@contextmanager
def clone(repo):
    repo.dir = tempfile.mkdtemp(suffix="cpp")
    with open(os.devnull, "w") as FNULL:
        subprocess.check_call(["git", "clone", repo.git_url, repo.dir],
                               stdout=FNULL, stderr=subprocess.STDOUT)
    yield repo
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
    if len(repo_algorithms) > 0:
        print(40 * "=")
        print("Algorithm stats for {0}".format(repo.name))
        print(40 * "=")
        print_stats(repo_algorithms)
    return repo_algorithms


def print_stats(used_algorithms):
    for algorithm, count in used_algorithms.items():
        print("{0}:{1}".format(algorithm, count))


if __name__ == '__main__':
    args = docopt(__doc__)
    all_algorithms = Counter()

    def signal_handler(signal, frame):
        print(20 * "=")
        print("All algorithms")
        print(20 * "=")
        print_stats(all_algorithms)
        sys.exit(0)

    def make_request(url):
        headers = {"Accept": "application/vnd.github.v3+json"}
        auth=HTTPBasicAuth(args["-u"], args["-p"])
        return requests.get(url, headers=headers, auth=auth)

    signal.signal(signal.SIGINT, signal_handler)

    for repo in get_cpp_repositories(make_request):
        with clone(repo)  as local_repo:
            all_algorithms += count_repo_algorithms(local_repo)

    print(20 * "=")
    print("All algorithms")
    print(20 * "=")
    print_stats(all_algorithms)
