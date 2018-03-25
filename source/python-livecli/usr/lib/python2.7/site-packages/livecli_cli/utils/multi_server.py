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


def _play_stream(HTTPBase):
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
    quality = (data_other.get("q") or
               data_other.get("quality") or
               data_other.get("stream") or
               data_other.get("default-stream") or
               "best")
    try:
        cache = data_other.get("cache") or 4096
    except TypeError:
        cache = 4096

    loglevel = data_other.get("l") or data_other.get("loglevel") or "debug"
    session.set_loglevel(loglevel)
    try:
        streams = session.streams(url)
    except Exception as e:
        HTTPBase._headers(404, "text/html")
        logger.error("No Stream Found!")
        return

    if not streams:
        HTTPBase._headers(404, "text/html")
        return

    # XXX: only one quality will work currently
    try:
        stream = streams[quality]
    except KeyError:
        stream = streams["best"]
        quality = "best"

    if isinstance(stream, HTTPStream) is False and isinstance(stream, HDSStream) is False:
        # allow only http based streams: HDS HLS HTTP
        # RTMP is not supported
        HTTPBase._headers(404, "text/html")
        return

    hls_session_reload = data_other.get("hls-session-reload")
    if hls_session_reload:
        livecli_cache = Cache(
            filename="streamdata.json",
            key_prefix="cache:{0}".format(stream.url)
        )
        livecli_cache.set("cache_stream_name", quality, (int(hls_session_reload) + 60))
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
