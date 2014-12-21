import os
import sys

from redis import Redis

from repo import GitRepo

HOST_ENV = "ALGOSTAT_RQ_HOST"
PORT_ENV = "ALGOSTAT_RQ_PORT"
JOBS_LIST = "algostat:jobs"
RESULTS_LIST = "algostat:results"


class RedisQueue:
    def __init__(self, redis):
        self.redis = redis

    def put_job(self, repo_name):
        self.redis.rpush(JOBS_LIST, repo_name.encode("utf-8"))

    def fetch_jobs(self):
        while self.redis.llen(JOBS_LIST) > 0:
            repo_name = self.redis.lpop(JOBS_LIST).decode("utf-8")
            yield GitRepo(repo_name)

    def put_result(self, result):
        self.redis.rpush(RESULTS_LIST, result.encode("utf-8"))

    def fetch_results(self):
        while self.redis.llen(RESULTS_LIST) > 0:
            yield self.redis.lpop(RESULTS_LIST).decode("utf-8")

    def from_config():
        if not (HOST_ENV in os.environ and PORT_ENV in os.environ):
            sys.stderr.write("Please provide {0} and {1} environment vars\n"
                             .format(HOST_ENV, PORT_ENV))
            sys.exit(1)
        else:
            return RedisQueue(Redis(host=os.environ[HOST_ENV],
                                    port=os.environ[PORT_ENV]))
