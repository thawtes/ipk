import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import RTMPStream

__livecli_docs__ = {
    "domains": [
        "younow.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-02-16",
}


class younow(Plugin):

    _url_re = re.compile(r"https?://(?:\w+\.)?younow\.com/(?P<channel>[^/&?]+)")

    api_url = "https://api.younow.com/php/api/broadcast/info/curId=0/user={0}"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        match = self._url_re.match(self.url)
        channel = match.group("channel")

        res = http.get(self.api_url.format(channel))
        data = http.json(res)

        if data.get("errorCode") == 0:
            media = data.get("media")
            if media:
                rtmp_url = "rtmp://{host}{app}/{stream}".format(
                    host=media["host"],
                    app=media["app"],
                    stream=media["stream"],
                )
                params = {
                    "rtmp": rtmp_url,
                    "live": True
                }

                yield "live", RTMPStream(self.session, params=params)


__plugin__ = younow
