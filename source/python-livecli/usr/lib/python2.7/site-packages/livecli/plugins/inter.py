import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "inter.ua",
        "k1.ua",
        "ntn.ua",
    ],
    "geo_blocked": [
        "RU",
        "UA",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-02-02",
}


class Inter(Plugin):
    """Livecli Plugin for Livestreams of
        - http://inter.ua/ru/live
        - http://www.k1.ua/uk/live
        - http://ntn.ua/ru/live
    """

    _url_re = re.compile(r"""https?://
        (?:www\.)?
        (?:
            inter
            |
            k1
            |
            ntn
        )
        \.ua/
        (?:
            uk|ua|ru
        )
        /live
        """, re.VERBOSE | re.IGNORECASE)
    _playlist_re = re.compile(r"""hlssource:\s?["'](?P<url>[^"'\s]+)["']""", re.IGNORECASE)

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        headers = {
            "Referer": self.url,
            "User-Agent": useragents.FIREFOX
        }

        res = http.get(self.url, headers=headers)

        m = self._playlist_re.search(res.text)
        if not m:
            return

        res = http.get(m.group("url"), headers=headers)
        if not res.text.startswith("#EXTM3U"):
            hls_url = http.json(res).get("redir")
        else:
            hls_url = m.group("url")

        if hls_url is not None:
            self.logger.debug("HLS URL: {0}".format(hls_url))
            streams = HLSStream.parse_variant_playlist(self.session, hls_url, headers=headers)
            if not streams:
                return {"live": HLSStream(self.session, hls_url, headers=headers)}
            else:
                return streams


__plugin__ = Inter
