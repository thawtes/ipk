# -*- coding: utf-8 -*-
"""
    This file is used for the Kodi Addon service.livecli.proxy
    - https://github.com/livecli/service.livecli.proxy
    - https://github.com/livecli/repo

    every change must be compatible with it.
"""
import errno
import os
import socket

from livecli import Livecli
from livecli import StreamError
from livecli.cache import Cache
from livecli.compat import parse_qsl
from livecli.compat import unquote_plus
from livecli.compat import urlparse
from livecli.stream import HDSStream
from livecli.stream import HTTPStream
from livecli.stream.ffmpegmux import MuxedStream

from .multi_args import command_session

from time import time

try:
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
except ImportError:
    # Python 2.7
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer

try:
    from socketserver import ThreadingMixIn
except ImportError:
    # Python 2.7
    from SocketServer import ThreadingMixIn

try:
    # service.livecli.proxy
    import xbmc
    PLUGINS_DIR = xbmc.translatePath("special://profile/addon_data/service.livecli.proxy/plugins/").encode("utf-8")
    is_kodi = True
except ImportError:
    from livecli_cli.constants import PLUGINS_DIR
    is_kodi = False

STREAM_SYNONYMS = ["best", "worst"]


def resolve_stream_name(streams, stream_name):
    """Returns the real stream name of a synonym."""

    if stream_name in STREAM_SYNONYMS and stream_name in streams:
        for name, stream in streams.items():
            if stream is streams[stream_name] and name not in STREAM_SYNONYMS:
                return name

    return stream_name


def format_valid_streams(plugin, streams):
    """Formats a dict of streams.

    Filters out synonyms and displays them next to
    the stream they point to.

    Streams are sorted according to their quality
    (based on plugin.stream_weight).

    """

    delimiter = ", "
    validstreams = []

    for name, stream in sorted(streams.items(),
                               key=lambda stream: plugin.stream_weight(stream[0])):
        if name in STREAM_SYNONYMS:
            continue

        def synonymfilter(n):
            return stream is streams[n] and n is not name
        synonyms = list(filter(synonymfilter, streams.keys()))

        if len(synonyms) > 0:
            joined = delimiter.join(synonyms)
            name = "{0} ({1})".format(name, joined)

        validstreams.append(name)

    return delimiter.join(validstreams)


def _play_stream(HTTPBase, redirect=False):
    """Creates a livecli session and plays the stream."""
    session = Livecli()
    session.set_logprefix("[ID-{0}]".format(str(int(time()))[4:]))
    logger = session.logger.new_module("livecli-server")
    session.set_loglevel("info")

    logger.info("User-Agent: {0}".format(HTTPBase.headers.get("User-Agent", "???")))
    logger.info("Client: {0}".format(HTTPBase.client_address))
    logger.info("Address: {0}".format(HTTPBase.address_string()))

    # Load custom user plugins
    if os.path.isdir(PLUGINS_DIR):
        session.load_plugins(PLUGINS_DIR)

    old_data = parse_qsl(urlparse(HTTPBase.path).query)
    data = []
    for k, v in old_data:
        data += [(unquote_plus(k), unquote_plus(v))]

    data_other, session = command_session(session, data)

    url = data_other.get("url")
    if not url:
        HTTPBase._headers(404, "text/html")
        logger.error("No URL provided.")
        return

    plugin = session.resolve_url(url)
    logger.info("Found matching plugin {0} for URL {1}",
                plugin.module, url)

    # set cache size
    try:
        cache = data_other.get("cache") or 4096
    except TypeError:
        cache = 4096

    # set loglevel
    loglevel = data_other.get("l") or data_other.get("loglevel") or "debug"
    session.set_loglevel(loglevel)

    # find streams
    try:
        if redirect is True:
            streams = session.streams(url, stream_types=["hls", "http"])
        elif data_other.get("stream-types"):
            streams = session.streams(url, stream_types=data_other.get("stream-types"))
        else:
            streams = session.streams(url)
    except Exception as e:
        HTTPBase._headers(404, "text/html")
        logger.error("No Stream Found!")
        return

    if not streams:
        HTTPBase._headers(404, "text/html")
        return

    # set quality
    quality = (data_other.get("q") or
               data_other.get("quality") or
               data_other.get("stream") or
               data_other.get("default-stream") or
               ["best"])

    stream_name = "best"

    validstreams = format_valid_streams(plugin, streams)
    for stream_name in quality:
        if stream_name in streams:
            logger.info("Available streams: {0}", validstreams)
            stream_name = resolve_stream_name(streams, stream_name)
            break

    try:
        stream = streams[stream_name]
        logger.debug("Valid quality: {0}".format(stream_name))
    except KeyError:
        logger.debug("Invald quality: '{0}', using 'best' instead".format(stream_name))
        stream = streams["best"]

    if not isinstance(stream, (HDSStream, HTTPStream, MuxedStream)):
        # allow only http based streams: HDS HLS HTTP
        # RTMP is not supported
        logger.debug("only HTTP, HLS, HDS or MuxedStreams are supported.")
        logger.debug(str(type(stream)))
        HTTPBase._headers(404, "text/html")
        return

    if redirect is True:
        logger.info("301 - URL: {0}".format(stream.url))
        HTTPBase.send_response(301)
        HTTPBase.send_header("Location", stream.url)
        HTTPBase.end_headers()
        logger.info("301 - done")
        return

    hls_session_reload = data_other.get("hls-session-reload")
    if hls_session_reload:
        livecli_cache = Cache(
            filename="streamdata.json",
            key_prefix="cache:{0}".format(stream.url)
        )
        livecli_cache.set("cache_stream_name", stream_name, (int(hls_session_reload) + 60))
        livecli_cache.set("cache_url", url, (int(hls_session_reload) + 60))
        session.set_option("hls-session-reload", int(hls_session_reload))

    try:
        fd = stream.open()
    except StreamError as err:
        HTTPBase._headers(404, "text/html")
        logger.error("Could not open stream: {0}".format(err))
        return

    HTTPBase._headers(200, "video/unknown")
    try:
        logger.debug("Pre-buffering {0} bytes".format(cache))
        while True:
            buff = fd.read(cache)
            if not buff:
                logger.error("No Data!")
                break
            HTTPBase.wfile.write(buff)
        HTTPBase.wfile.close()
    except socket.error as e:
        if isinstance(e.args, tuple):
            if e.errno == errno.EPIPE:
                # remote peer disconnected
                logger.info("Detected remote disconnect")
                pass
            else:
                logger.error(str(e))
        else:
            logger.error(str(e))

    fd.close()
    logger.info("Stream ended")
    fd = None


class HTTPRequest(BaseHTTPRequestHandler):

    def _headers(self, status, content):
        self.send_response(status)
        self.send_header("Server", "Livecli")
        self.send_header("Content-type", content)
        self.end_headers()

    def do_HEAD(self):
        """Respond to a HEAD request."""
        self._headers(404, "text/html")

    def do_GET(self):
        """Respond to a GET request."""
        if self.path.startswith("/play/"):
            _play_stream(self)
        elif self.path.startswith("/301/"):
            _play_stream(self, redirect=True)
        else:
            self._headers(404, "text/html")


class Server(HTTPServer):
    """HTTPServer class with timeout."""
    timeout = 5


class ThreadedHTTPServer(ThreadingMixIn, Server):
    """Handle requests in a separate thread."""
    daemon_threads = True


__all__ = [
    "HTTPRequest",
    "ThreadedHTTPServer",
]
