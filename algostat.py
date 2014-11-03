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

import requests
from requests.auth import HTTPBasicAuth

from docopt import docopt

from algorithm import filter_cpp_files, count_algorithms


class TemporaryGitRepo:
    def __init__(self, git_url):
        self.git_url = git_url

    def __enter__(self):
        self.dir = tempfile.mkdtemp(suffix="cpp")
        FNULL = open(os.devnull, 'w')
        print("Cloning {0} into {1}".format(git_url, self.dir))
        subprocess.check_call(["git", "clone", self.git_url, self.dir],
                               stdout=FNULL, stderr=subprocess.STDOUT)
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.dir)


def get_cpp_repositories(make_request):
    """Search for the top 1000 cpp repos in github and return their git url"""
    url = "https://api.github.com/search/repositories?q=language:cpp&per_page=100"
    response = make_request(url)

    while "next" in response.links.keys():
        url = response.links["next"]["url"]
        response = make_request(url)
        for repo in response.json()["items"]:
            yield repo["git_url"]


def count_repo_algorithms(repo):
    """Count all algorithms in a repository"""
    repo_algorithms = Counter()
    for cpp_path in filter_cpp_files(repo):
        repo_algorithms += count_algorithms(cpp_path)
    print("Found algorithms for {0}".format(repo.dir))
    print(repo_algorithms)
    return repo_algorithms

if __name__ == '__main__':
    args = docopt(__doc__)
    all_algorithms = Counter()

    def print_results():
        print("-----------RESULT------------")
        print(all_algorithms)

    def signal_handler(signal, frame):
        print_results()
        sys.exit(0)

    def make_request(url):
        headers = {"Accept": "application/vnd.github.v3+json"}
        auth=HTTPBasicAuth(args["-u"], args["-p"])
        return requests.get(url, headers=headers, auth=auth)

    signal.signal(signal.SIGINT, signal_handler)

    for git_url in get_cpp_repositories(make_request):
        with TemporaryGitRepo(git_url) as repo:
            all_algorithms += count_repo_algorithms(repo)

    print_results()
