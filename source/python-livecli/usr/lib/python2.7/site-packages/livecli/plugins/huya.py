import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream
from livecli.utils import update_scheme

__livecli_docs__ = {
    "domains": [
        "huya.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-02-24",
}


class Huya(Plugin):

    _url_re = re.compile(r'https?://(?:www\.)?huya\.com/(?P<channel>[^/]+)', re.VERBOSE)
    _hls_re = re.compile(r'''^\s*<video\s+id=["']html5player-video["']\s+src=["'](?P<url>[^"']+)["']''', re.MULTILINE)

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        headers = {'User-Agent': useragents.IPAD}
        channel = self._url_re.match(self.url).group('channel')

        res = http.get('https://m.huya.com/{0}'.format(channel), headers=headers)
        m = self._hls_re.search(res.text)
        if not m:
            self.logger.debug('No m3u8 url found.')
            return

        hls_url = update_scheme('https://', m.group('url'))
        self.logger.debug('URL={0}'.format(hls_url))
        return {'live': HLSStream(self.session, hls_url, headers=headers)}


__plugin__ = Huya
