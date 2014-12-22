import os
import tempfile
import shutil
import subprocess
from contextlib import contextmanager

VERBOSE = "ALGOSTAT_VERBOSE" in os.environ


class GitRepo:
    def __init__(self, name):
        self.name = name

    def url(self):
        return "https://nouser:nopass@github.com/" + self.name + ".git"


@contextmanager
def clone(repo):
    """Clone a repository into a temporary directory which gets cleaned
    up afterwards"""
    repo.dir = tempfile.mkdtemp(suffix=repo.name.split("/")[1])

    if VERBOSE:
        print("Cloning {0} into {1}".format(repo.url(), repo.dir))

    with open(os.devnull, "w") as FNULL:
        subprocess.check_call(["git", "clone", "-q", repo.url(), repo.dir],
                              stdout=FNULL, stderr=subprocess.STDOUT)
    yield repo

    if VERBOSE:
        print("Cleaning up {0}".format(repo.dir))

    shutil.rmtree(repo.dir)
    del repo.dir
