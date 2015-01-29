import os
import sys
import json

from redis import Redis

from repo import GitRepo

HOST_ENV = "ALGOSTAT_RQ_HOST"
PORT_ENV = "ALGOSTAT_RQ_PORT"
CLOUDFOUNDRY_ENV = "VCAP_SERVICES"
JOBS_LIST = "algostat:jobs"
RESULTS_LIST = "algostat:results"


class RedisQueue(object):
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

    def from_config(self):
        if "VCAP_SERVICES" in os.environ:
            cf_config = os.environ[CLOUDFOUNDRY_ENV]
            rediscloud_service = json.loads(cf_config)['rediscloud'][0]
            credentials = rediscloud_service['credentials']
            redis = Redis(host=credentials['hostname'],
                          port=credentials['port'],
                          password=credentials['password'])
            return RedisQueue(redis)
        elif not (HOST_ENV in os.environ and PORT_ENV in os.environ):
            sys.stderr.write("Please provide {0} and {1} environment vars\n"
                             .format(HOST_ENV, PORT_ENV))
            sys.exit(1)
        else:
            return RedisQueue(Redis(host=os.environ[HOST_ENV],
                                    port=os.environ[PORT_ENV]))
