#!/usr/bin/env python
"""
Find the top C++ repos on Github with the Github Search API.
"""
import sys

import requests


def get_cpp_repositories():
    """Search for the top 1000 cpp repos in github and return their git url"""
    url = "https://api.github.com/search/repositories?q=language:cpp&per_page=101"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)

    while "next" in response.links.keys():
        url = response.links["next"]["url"]
        response = requests.get(url, headers=headers)

        if response.status_code == requests.codes.ok:
            for repo in response.json()["items"]:
                yield repo["full_name"]
        else:
            sys.stderr.write("Request " + url + " was not successful.")
            sys.exit(1)


if __name__ == '__main__':
    for repo in get_cpp_repositories():
        sys.stdout.write(repo + "\n")
