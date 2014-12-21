# Algostat

Tools to find the most frequently used C++ algorithms on Github.

## Usage

### Analyze top 500 C++ repos on Github

Analyze the top 500 C++ repos on Github and create a CSV file.
For using the Github API you need to provide a Github Access Token
with the `ALGOSTAT_GH_TOKEN` environment variable.

```
export ALGOSTAT_GH_TOKEN="asdfqwet12341532"
./top-github-repos.py | ./algostat.py | ./create-csv.py > results.csv
```

### Analyze all C++ repos on Github

Analyze all C++ repos listed in [GHTorrent](http://ghtorrent.org/).

```
cpp_repos.txt | ./algostat.py | ./create-csv.py > results.csv
```

### Distributed analyzing with Redis Queue and workers

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

## Results

These functions have over a thousand usages and seem to be the most used ones.

Algorithm   | Count
------------|-----------
`min`       | 34187
`count`     | 26905
`max`       | 24345
`move`      | 20492
`find`      | 18798
`copy`      | 10613
`remove`    | 9196
`sort`      | 7768
`swap`      | 5818
`replace`   | 4831
`search`    | 4696
`transform` | 4567
`equal`     | 4536
`fill`      | 4282
`generate`  | 3476
`merge`     | 3155
`unique`    | 2874
`reverse`   | 2575
`shuffle`   | 1977
`rotate`    | 1644
`partition` | 1149
`for_each`  | 1144

Some functions have just over 200 usages:

Algorithm       | Count
----------------|-----------
`mismatch`      | 873
`lower_bound`   | 759
`includes`      | 680
`accumulate`    | 533
`is_heap`       | 524
`find_if`       | 520
`upper_bound`   | 495
`is_heap_until` | 494
`find_first_of` | 445
`max_element`   | 406
`iota`          | 365
`stable_sort`   | 312
`random_shuffle`| 295
`equal_range`   | 280
`min_element`   | 268
`fill_n`        | 229

There are also some functions which in my opinion shouldn't be even in
the standard library because no one wants to use them

Algorithm                   | Count
----------------------------|-----------
`move_backward`             | 6
`is_permutation`            | 3
`partition_point`           | 3
`find_if_not`               | 0
`partition_copy`            | 0
`unique_copyis_partitioned` | 0
