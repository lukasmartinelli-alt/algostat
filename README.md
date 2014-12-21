# Algostat

Tools to find the most frequently used C++ algorithms on Github.

## Results

You can look and filter the results in [results.csv](results.csv).

## Usage

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
export ALGOSTAT_RQ="localhost:6379"
```

Now you need to fill the job queue.

```
cpp_repos.txt | ./rq-enqueue-jobs.py
```

On your workers you need to tell  `algostat.py` to fetch the jobs from
a redis queue and then store it in a results queue.

```
./algostat.py --rq | ./rq-store-results.py
```

After that you aggregate the results in a single csv.

```
./rq-fetch-results.py | ./create-csv.py > results.csv
```

## Installation

1. Make sure you have Python 3 installed
2. Clone the repository
3. Install requirements with `pip install -r requirements.txt`
