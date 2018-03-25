import json

from contextlib import contextmanager

from .http_server import HTTPServer
from .named_pipe import NamedPipe
from .progress import progress
from .player import find_default_player
from .stream import stream_to_url
from .multi_server import HTTPRequest as server_HTTPRequest
from .multi_server import ThreadedHTTPServer as server_ThreadedHTTPServer

__all__ = [
    "NamedPipe", "HTTPServer", "JSONEncoder",
    "server_HTTPRequest", "server_ThreadedHTTPServer",
    "find_default_player", "ignored", "progress", "stream_to_url"
]


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json__"):
            return obj.__json__()
        elif isinstance(obj, bytes):
            return obj.decode("utf8", "ignore")
        else:
            return json.JSONEncoder.default(self, obj)


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass
