import tempfile
import os
from collections import namedtuple
from algorithm import count_algorithms, filter_cpp_files


Repo = namedtuple('Repo', ['dir'])


def test_filter_only_includes_files_with_extensions_and_includes():
    with tempfile.TemporaryDirectory(suffix="test_algorithm") as tmp:
        with open(os.path.join(tmp, "test.cpp"), "w") as file1:
            file1.writelines([
                '#include "customfile.h"',
                "#include <algorithm>"
            ])
        with open(os.path.join(tmp, "test.cc"), "w") as file2:
            file2.writelines([
                "#include <string>"
            ])
        with open(os.path.join(tmp, "test.h"), "w") as file3:
            file3.writelines([
                "#include <algorithm>",
                "#include <string>"
            ])
        with open(os.path.join(tmp, "test.hpp"), "w") as file4:
            file4.writelines([
                "#include <numeric>",
                "#include <string>"
            ])
        # file should be excluded even if it contains C++ includes
        with open(os.path.join(tmp, "test.txt"), "w") as file5:
            file5.writelines([
                "#include <numeric>",
            ])

        repo = Repo(dir=tmp)
        cpp_files = list(filter_cpp_files(repo))

        assert len(cpp_files) == 3
        file_names = sorted([os.path.basename(f.name) for f in cpp_files])
        assert file_names == ["test.cpp", "test.h", "test.hpp"]


def test_count_algorithms_works_for_various_function_formats():
    file1 = [
        "std::sort(sorted.begin(), sorted.end(), &compare_range_by_left);",
        "sort   (sorted.begin, sorted.end());",
        "auto sorted_or_not = is_sorted (sorted);"
    ]
    algos = count_algorithms(file1)
    assert algos["sort"] == 2
    assert algos["is_sorted"] == 1
