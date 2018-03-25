import inspect
import os
import sys

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)
is_win32 = os.name == "nt"

# win/nix compatible devnull
try:
    from subprocess import DEVNULL

    def compat_devnull():
        return DEVNULL
except ImportError:
    def compat_devnull():
        return open(os.path.devnull, 'w')

if is_py2:
    _str = str
    str = unicode  # noqa
    range = xrange  # noqa

    def bytes(b, enc="ascii"):
        return _str(b)

elif is_py3:
    bytes = bytes
    str = str
    range = range

try:
    from urllib.parse import (
        urlparse, urlunparse, urljoin, quote, unquote, parse_qsl, urlencode
    )
except ImportError:
    from urlparse import urlparse, urlunparse, urljoin, parse_qsl
    from urllib import quote, unquote, urlencode

try:
    from urllib.parse import unquote_plus
except ImportError:
    # python 2.7
    from urllib import unquote_plus

try:
    import queue as compat_queue
except ImportError:
    # python 2.7
    import Queue as compat_queue

try:
    from shutil import which as compat_which
except ImportError:
    try:
        # Kodi - script.module.livecli
        from shutil_which.shutil_which import which as compat_which
    except ImportError:
        # python 2.7
        from backports.shutil_which import which as compat_which


try:
    from Cryptodome.Cipher import AES as crypto_AES
except ImportError:
    from Crypto.Cipher import AES as crypto_AES

try:
    from Cryptodome.Cipher import Blowfish as crypto_Blowfish
except ImportError:
    from Crypto.Cipher import Blowfish as crypto_Blowfish

try:
    # python 3.4+
    from html import unescape as compat_unescape
except ImportError:
    # python 2.7
    from HTMLParser import HTMLParser
    compat_unescape = HTMLParser().unescape

if hasattr(inspect, "getfullargspec"):
    # python 3
    def compat_getargspec(func):
        return inspect.getfullargspec(func)
else:
    # python 2.7
    def compat_getargspec(func):
        return inspect.getargspec(func)


__all__ = [
    "bytes",
    "compat_devnull",
    "compat_getargspec",
    "compat_queue",
    "compat_unescape",
    "compat_which",
    "crypto_AES",
    "crypto_Blowfish",
    "is_py2",
    "is_py3",
    "is_win32",
    "parse_qsl",
    "quote",
    "range",
    "str",
    "unquote_plus",
    "unquote",
    "urlencode",
    "urljoin",
    "urlparse",
    "urlunparse",
]
