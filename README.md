# Algostat 
![stability-deprecated](https://img.shields.io/badge/stability-deprecated-red.svg)
[![Build Status](https://travis-ci.org/lukasmartinelli/algostat.svg)](https://travis-ci.org/lukasmartinelli/algostat)
[![Coverage Status](https://coveralls.io/repos/lukasmartinelli/algostat/badge.svg)](https://coveralls.io/r/lukasmartinelli/algostat)
[![Code Health](https://landscape.io/github/lukasmartinelli/algostat/master/landscape.svg?style=flat)](https://landscape.io/github/lukasmartinelli/algostat/master)
[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/lukasmartinelli/algostat.svg?style=flat)](https://scrutinizer-ci.com/g/lukasmartinelli/algostat/?branch=master)

> :warning: This repository is no longer maintained by Lukas Martinelli.

Tools to find the most frequently used [C++ algorithms](http://en.cppreference.com/w/cpp/algorithm) on Github.

## Results

You can look at the results of 3869 analyzed C++ repos in my
[Google Spreadsheets](https://docs.google.com/spreadsheets/d/125CRiE0_2uHeMhj84hAVtpAatDwWWl-H71Y5JshaaUM/pubhtml)
 or use the [results.csv](results.csv) directly.

![Diagram of top 10 algorithms](https://docs.google.com/spreadsheets/d/125CRiE0_2uHeMhj84hAVtpAatDwWWl-H71Y5JshaaUM/pubchart?oid=1597254254&format=image)

algorithm                                                            | sum  |avg
---------------------------------------------------------------------|------|----
[swap](http://en.cppreference.com/w/cpp/algorithm/swap)              |108363|28
[find](http://en.cppreference.com/w/cpp/algorithm/find)              |81006 |21
[count](http://en.cppreference.com/w/cpp/algorithm/count)            |60306 |16
[move](http://en.cppreference.com/w/cpp/algorithm/move)              |57595 |15
[copy](http://en.cppreference.com/w/cpp/algorithm/copy)              |48050 |12
[sort](http://en.cppreference.com/w/cpp/algorithm/sort)              |33317 |9
[max](http://en.cppreference.com/w/cpp/algorithm/max)                |28848 |7
[equal](http://en.cppreference.com/w/cpp/algorithm/equal)            |27467 |7
[min](http://en.cppreference.com/w/cpp/algorithm/min)                |21720 |6
[unique](http://en.cppreference.com/w/cpp/algorithm/unique)          |18484 |5
[lower_bound](http://en.cppreference.com/w/cpp/algorithm/lower_bound)|15017 |4
[remove](http://en.cppreference.com/w/cpp/algorithm/remove)          |13972 |4
[replace](http://en.cppreference.com/w/cpp/algorithm/replace)        |13262 |3
[upper_bound](http://en.cppreference.com/w/cpp/algorithm/upper_bound)|11835 |3
[for_each](http://en.cppreference.com/w/cpp/algorithm/for_each)      |11518 |3

##Usage

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
cat cpp_repos.txt | ./algostat.py | ./create-csv.py > results.csv
```

### Distributed Analyzing with Redis Queue and workers

Use a Redis Queue to distribute jobs among workers and then fetch the results.
You need to provide the `ALGOSTAT_RQ` environment variable to the process with the
address of the redis server.

```
export ALGOSTAT_RQ_HOST="localhost"
export ALGOSTAT_RQ_PORT="6379"
```

Now you need to fill the job queue with results from top github repos
and repos listed in GHTorrent and sort out the duplicates.

```
./top-github-repos.py >> jobs.txt
cat cpp_repos.txt >> jobs.txt
sort -u jobs.txt | ./enqueue-jobs.py
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
