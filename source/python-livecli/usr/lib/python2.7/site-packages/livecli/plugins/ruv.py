import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "ruv.is",
    ],
    "geo_blocked": [
        "IS",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-02-17",
}


class Ruv(Plugin):
    """Plugin for RUV, the Icelandic national television."""

    _url_re = re.compile(r"""https?://
        (?:www\.)?ruv\.is/
            (?P<channel>
                ras-1
                |
                ras-2
                |
                ras1
                |
                ras2
                |
                rondo
                |
                ruv
                |
                ruv-2
                |
                ruv2
            )
        /?$
        """, re.VERBOSE)

    _channel_map = {
        "ras-1": "ras1",
        "ras-2": "ras2",
        "ras1": "ras1",
        "ras2": "ras2",
        "rondo": "ras3",
        "ruv": "ruv",
        "ruv-2": "ruv2",
        "ruv2": "ruv2",
    }

    live_api = "http://www.ruv.is/sites/all/themes/at_ruv/scripts/ruv-stream.php?channel={0}&format=json"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        url_m = self._url_re.match(self.url)

        res = http.get(self.live_api.format(self._channel_map[url_m.group("channel")]))
        data = http.json(res)

        result = data.get("result")
        if result:
            for url in result:
                if url.endswith(".m3u8"):
                    streams = HLSStream.parse_variant_playlist(self.session, url).items()
                    if not streams:
                        yield "live", HLSStream(self.session, url)
                    for s in streams:
                        yield s


__plugin__ = Ruv
