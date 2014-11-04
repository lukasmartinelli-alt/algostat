Algostat
========

Finds the most frequently used C++ algorithms on Github

Installation
------------

1. Clone the repository
2. Install requirements with `pip install -r requirements.txt`

Usage
-----

Because of the Github API rate limits it is recommended to use your Github User
to connect with Github.

```bash
./algostat.py -u USERNAME -p PASSWORD
```

Results
-------

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


