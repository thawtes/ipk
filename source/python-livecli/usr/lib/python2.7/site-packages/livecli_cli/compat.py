import sys

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)

if is_py2:
    input = raw_input  # noqa
    stdout = sys.stdout
    file = file  # noqa

elif is_py3:
    input = input
    stdout = sys.stdout.buffer
    from io import IOBase as file

try:
    from shutil import get_terminal_size as compat_get_terminal_size
except ImportError:
    # Python 2.7
    from backports.shutil_get_terminal_size import get_terminal_size as compat_get_terminal_size


__all__ = [
    "compat_get_terminal_size",
    "file",
    "input",
    "is_py2",
    "is_py3",
    "stdout",
]
