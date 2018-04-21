# coding: utf8
"""Livecli extracts streams from various services.

The main compontent of Livecli is a command-line utility that
launches the streams in a video player.

An API is also provided that allows direct access to stream data.

Full documentation is available at https://livecli.github.io.

"""
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__title__ = "livecli"
__license__ = "Simplified BSD"
__author__ = "Livecli"
__copyright__ = "Copyright 2018 Livecli"
__credits__ = ["https://github.com/livecli/livecli/blob/master/AUTHORS"]

from livecli.api import streams  # noqa
from livecli.exceptions import (
    LivecliError,
    NoPluginError,
    NoStreamsError,
    PluginError,
    StreamError,
)  # noqa
from livecli.session import Livecli  # noqa

__all__ = [
    "__author__",
    "__copyright__",
    "__credits__",
    "__license__",
    "__title__",
    "__version__",
    "Livecli",
    "LivecliError",
    "NoPluginError",
    "NoStreamsError",
    "PluginError",
    "StreamError",
    "streams",
]
