# Algostat

Tools to find the most frequently used C++ algorithms on Github.

## Results

You can look at the results in my [Google Spreadsheets](https://docs.google.com/spreadsheets/d/125CRiE0_2uHeMhj84hAVtpAatDwWWl-H71Y5JshaaUM/pubhtml)
 or use the [results.csv](results.csv) directly.

![Diagram of top 10 algorithms](https://docs.google.com/a/lukasmartinelli.ch/spreadsheets/d/125CRiE0_2uHeMhj84hAVtpAatDwWWl-H71Y5JshaaUM/pubchart?oid=1597254254&format=image)

## Usage

For best mode you should disable input and output buffering of Python.

```
export PYTHONUNBUFFERED=true
```

### Analyze top C++ repos on Github

Analyze the top C++ repos on Github and create a CSV file.

```
./top-github-repos.py | ./algostat.py | ./create-csv.py > results.csv
```

### Analyze all C++ repos on Github

Analyze all C++ repos listed in [GHTorrent](http://ghtorrent.org/).

```
cpp_repos.txt | ./algostat.py | ./create-csv.py > results.csv
```

### Distributed Analyzing with Redis Queue and workers

Use a Redis Queue to distribute jobs among workers and then fetch the results.
You need to provide the `ALGOSTAT_RQ` environment variable to the process with the
address of the redis server.

```
export ALGOSTAT_RQ_HOST="localhost"
export ALGOSTAT_RQ_PORT="6379"
```

Now you need to fill the job queue.

```
cpp_repos.txt | ./enqueue-jobs.py
```

On your workers you need to tell  `algostat.py` to fetch the jobs from
a redis queue and then store it in a results queue.

```
./algostat.py --rq | ./enqueue-results.py
```

After that you aggregate the results in a single csv.

```
./fetch-results.py | ./create-csv.py > results.csv
```

## Installation

1. Make sure you have Python 3 installed
2. Clone the repository
3. Install requirements with `pip install -r requirements.txt`

## Using Docker for Deployment

You can use Docker to run the application in a distributed setup.

### Redis

Run the redis server.

```
docker run --name redis -p 6379:6379 -d sameersbn/redis:latest
```

Get the IP address of your redis server. Assign it to the `ALGOSTAT_RQ_HOST` env variable for all following `docker run` commands. In this example we will work with `104.131.5.11`.


### Get the image

I have already setup an automated build `lukasmartinelli/algostat` which you can use.

```
docker pull lukasmartinelli/algostat
```

Or you can clone the repo and build the docker image yourself.

```
docker build -t lukasmartinelli/algostat .
```

### Fill job queue

```
docker run -it --rm --name queue-filler \
-e ALGOSTAT_RQ_HOST=104.131.5.11 \
-e ALGOSTAT_RQ_PORT=6379 \
lukasmartinelli/algostat bash -c "cat cpp_repos.txt | ./enqueue-jobs.py"
```

### Run the workers

Assign as many workers as you like.

```
docker run -it --rm --name worker1 \
-e ALGOSTAT_RQ_HOST=104.131.5.11 \
-e ALGOSTAT_RQ_PORT=6379 \
lukasmartinelli/algostat bash -c "./algostat.py --rq | ./enqueue-results.py"
```

### Aggregate results

Note that this step is not repeatable. Once you've aggregated the results the redis list will be empty.

```
docker run -it --rm --name result-aggregator \
-e ALGOSTAT_RQ_HOST=104.131.5.11 \
-e ALGOSTAT_RQ_PORT=6379 \
lukasmartinelli/algostat bash -c "./fetch-results.py | ./create-csv.py"
```
