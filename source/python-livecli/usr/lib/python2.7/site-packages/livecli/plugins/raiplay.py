import re

from livecli import PluginError
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "raiplay.it",
    ],
    "geo_blocked": [
        "IT",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-04-30",
}


class RaiPlay(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?raiplay\.it/dirette/(\w+)/?")
    stream_re = re.compile(r"data-video-url.*?=.*?\"([^\"]+)\"")
    stream_schema = validate.Schema(
        validate.all(
            validate.transform(stream_re.search),
            validate.any(
                None,
                validate.all(validate.get(1), validate.url())
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        http.headers.update({"User-Agent": useragents.FIREFOX})
        channel = self.url_re.match(self.url).group(1)
        self.logger.debug("Found channel: {0}", channel)
        stream_url = http.get(self.url, schema=self.stream_schema)
        if stream_url:
            try:
                return HLSStream.parse_variant_playlist(self.session, stream_url)
            except Exception as e:
                if "Missing #EXTM3U header" in str(e):
                    raise PluginError("The streaming of this content is available in Italy only.")
                raise e


__plugin__ = RaiPlay
