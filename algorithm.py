import os
import re
from collections import Counter
from pathlib import Path

VERBOSE = "ALGOSTAT_VERBOSE" in os.environ
ALGORITHMS = [
    # Non-modifying sequence operations
    "all_of", "any_of", "none_of", "for_each", "count", "count_if",
    "mismatch", "equal", "find", "find_if", "find_if_not", "find_end",
    "find_first_of", "adjacent_find", "search", "search_n",
    # Modifying sequence operations
    "copy", "copy_if", "copy_n", "copy_backward", "move", "move_backward",
    "fill", "fill_n", "transform", "generate", "generate_n", "remove",
    "remove_if", "remove_copy", "remove_copy_if", "replace", "replace_if",
    "replace_copy", "replace_copy_if", "swap", "swap_ranges", "iter_swap",
    "reverse", "reverse_copy", "rotate", "rotate_copy", "random_shuffle",
    "shuffle", "unique", "unique_copy"
    #  Partitioning operations
    "is_partitioned", "partition", "partition_copy", "stable_partition",
    "partition_point",
    # Sorting operations
    "is_sorted", "is_sorted_until", "sort", "partial_sort",
    "partial_sort_copy", "stable_sort", "nth_element",
    # Binary search operations (on sorted ranges)
    "lower_bound", "upper_bound", "binary_search", "equal_range",
    # Set operations (on sorted ranges)
    "merge", "inplace_merge", "includes", "set_difference",
    "set_intersection", "set_symmetric_difference", "set_union",
    # Heap operations
    "is_heap", "is_heap_until", "make_heap", "push_heap",
    "pop_heap", "sort_heap",
    # Minimum/maximum operations
    "max", "max_element", "min", "min_element", "minmax",
    "minmax_element", "lexicographical_compare", "is_permutation",
    "next_permutation", "prev_permutation",
    # Numeric operations
    "iota", "accumulate", "inner_product", "adjacent_difference",
    "partial_sum"
]


def _has_headers(cpp_file):
    try:
        for line in cpp_file:
            if "<algorithm>" in line or "<numeric>" in line:
                return True
    except UnicodeDecodeError:
        # We cannot do anything if we don't know the encoding of the file
        pass
    return False


def count_algorithms(cpp_file):
    """Count all algorithms in a file"""
    algorithms = Counter({key: 0 for key in ALGORITHMS})
    try:
        for line in cpp_file:
            for algo in algorithms:
                # This will cache automatically after the first call
                matches = re.findall(algo + "\s*\(", line)
                algorithms[algo] += len(matches)
    except UnicodeDecodeError:
        # We cannot do anything if we don't know the encoding of the file
        pass
    return algorithms


def filter_cpp_files(repo):
    """
    Filter out all cpp files that include an <algorithm> or <numeric> header
    """
    repo_path = Path(repo.dir)

    try:
        cpp_extensions = ["cpp", "hpp", "h", "hh", "c", "cc"]
        file_types = [repo_path.glob("**/*." + ext) for ext in cpp_extensions]
        for paths in file_types:
            for cpp_path in paths:
                with cpp_path.open() as cpp_file:
                    if _has_headers(cpp_file):
                        yield cpp_file
                    elif VERBOSE:
                        print("Skipping " + cpp_path)
    except OSError:
        # Too many recursive symlinks
        pass
