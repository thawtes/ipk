import re

from livecli.plugin import Plugin
from livecli.plugin.api import http

__livecli_docs__ = {
    "domains": [
        "mediaklikk.hu",
    ],
    "geo_blocked": [
        "HU",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-02-11",
}


class Mediaklikk(Plugin):

    _url_re = re.compile(r"http(s)?://(www\.)?mediaklikk\.hu/")
    _id_re = re.compile(r"""(?P<q>["'])(?:streamId|token)(?P=q):(?P=q)(?P<id>[^"']+)(?P=q)""")

    new_self_url = "https://player.mediaklikk.hu/playernew/player.php?video={0}"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        res = http.get(self.url)

        m = self._id_re.search(res.text)
        if not m:
            self.logger.info("Found no videoid.")
            self.url = "resolve://{0}".format(self.url)
            return self.session.streams(self.url)

        video_id = m.group("id")
        if video_id:
            self.logger.debug("Found id: {0}".format(video_id))
            self.url = self.new_self_url.format(video_id)

            return self.session.streams(self.url)


__plugin__ = Mediaklikk
