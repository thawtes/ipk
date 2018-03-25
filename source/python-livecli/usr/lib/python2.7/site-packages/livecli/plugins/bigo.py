import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "bigo.tv",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-02-08",
}


class Bigo(Plugin):
    _url_re = re.compile(r"https?://(www\.)?bigo\.tv/[\w\d]+")
    _video_re = re.compile(r"""videoSrc:\s?["'](?P<url>[^"']+)["']""")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url,
                       allow_redirects=True,
                       headers={"User-Agent": useragents.IPHONE_6})
        m = self._video_re.search(res.text)
        if not m:
            return

        videourl = m.group("url")
        yield "live", HLSStream(self.session, videourl)


__plugin__ = Bigo
