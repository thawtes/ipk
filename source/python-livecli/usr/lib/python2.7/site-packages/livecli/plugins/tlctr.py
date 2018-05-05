import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "tlctv.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-04-24",
}


class TLCtr(Plugin):

    _url_re = re.compile(r'https?://(?:www\.)?tlctv\.com\.tr/canli-izle')
    _hls_re = re.compile(r'''["'](?P<url>https?://[^/]+/live/hls/[^"']+)["']''')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        headers = {'User-Agent': useragents.FIREFOX}
        res = http.get(self.url, headers=headers)

        m = self._hls_re.search(res.text)
        if not m:
            self.logger.debug('No video url found.')
            return

        hls_url = m.group('url')
        self.logger.debug('URL={0}'.format(hls_url))
        streams = HLSStream.parse_variant_playlist(self.session, hls_url, headers=headers)
        if not streams:
            return {'live': HLSStream(self.session, hls_url, headers=headers)}
        else:
            return streams


__plugin__ = TLCtr
