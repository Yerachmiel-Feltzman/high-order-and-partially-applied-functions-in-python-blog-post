# -------------
import gzip
import io
import os
from collections.abc import Iterable
from functools import partial
from pathlib import Path


def map(func: callable, iterable: Iterable):
    return [func(x) for x in iterable]


def filter(func: callable, iterable: Iterable):
    return [x for x in iterable if func(x)]


# --------------
def add_ten(number):
    return number + 10


numbers = [1, 2, 3, 4, 5]
added_ten = map(add_ten, numbers)

assert list(added_ten) == [11, 12, 13, 14, 15]


# -----------
def only_foo(s):
    return s == "foo"


my_strings = ["foo", "bar", "baz", "foo"]
filtered = filter(only_foo, my_strings)

assert list(filtered) == ["foo", "foo"]


# ------------
def read_parse_and_write_gzip(file_path: str | Path,
                              output_dir: Path,
                              line_parser: callable):
    with open(file_path, "rt") as in_f:
        with gzip.open(output_dir / (file_path.name + "_parsed.gz"), "wt") as out_f:
            for line in in_f:
                # line_parser can be any function that maps text lines
                modified_line = line_parser(line.removesuffix("\n")) + "\n"
                out_f.write(modified_line)


folder = Path("/tmp")
file = folder / "foo.txt"
with open(file, "wt") as f:
    f.write("abc\n123\n")

read_parse_and_write_gzip(file, folder, line_parser=lambda x: x + "foo")

with gzip.open(folder / (file.name + "_parsed.gz"), "rt") as result:
    for line in result:
        assert line.endswith("foo\n")


# ------------
def slice(l: list, start: int, end: int) -> list:
    return l[start:end]


head = partial(slice, start=0)
tail = partial(slice, end=None)

s = "abc"
assert head(s, end=2) == "ab"
assert tail(s, start=1) == "bc"

# --------
# input file content = "abc\n123\n"

read_parse_and_write_gzip(file, folder, partial(head, end=2))
# written gz file content = "ab\n12\n"

with gzip.open(folder / (file.name + "_parsed.gz"), "rt") as result:
    assert result.read() == "ab\n12\n"

read_parse_and_write_gzip(file, folder, partial(tail, start=1))
# written gz file content = "bc\n23\n"

with gzip.open(folder / (file.name + "_parsed.gz"), "rt") as result:
    assert result.read() == "bc\n23\n"

# ------------
# input file content = "abc\n123\n"

apply_to_my_file = partial(read_parse_and_write_gzip, file_path=file)

apply_to_my_file(output_dir=folder, line_parser=partial(head, end=2))
# written gz file content = "ab\n12\n"

apply_to_my_file(output_dir=folder, line_parser=partial(tail, start=2))
# written gz file content = "bc\n23\n"
