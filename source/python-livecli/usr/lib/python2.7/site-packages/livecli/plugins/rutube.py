import re

from livecli.exceptions import NoStreamsError
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HDSStream
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "rutube.ru",
    ],
    "geo_blocked": [
        "RU"
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-04-26",
}


class RUtube(Plugin):
    ''' https://rutube.ru/feeds/live/ '''

    api_play = 'https://rutube.ru/api/play/options/{0}/?format=json&no_404=true&referer={1}'

    _url_re = re.compile(r'''https?://(\w+\.)?rutube\.ru/(?:play|video)/(?:embed/)?(?P<id>[a-z0-9]+)''')

    _video_schema = validate.Schema(
        validate.any({
            'live_streams': {
                validate.text: [{
                    "url": validate.text,
                }]
            },
            'video_balancer': {
                validate.text: validate.text,
            },
        }, {}
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        hls_urls = []
        hds_urls = []
        http.headers.update({'User-Agent': useragents.FIREFOX})

        match = self._url_re.match(self.url)
        if match is None:
            return

        video_id = match.group('id')
        self.logger.debug('video_id: {0}'.format(video_id))

        res = http.get(self.api_play.format(video_id, self.url))
        data = http.json(res, schema=self._video_schema)

        live_data = data.get('live_streams')
        vod_data = data.get('video_balancer')

        if live_data:
            self.logger.debug('Found live_data')
            for d in live_data['hls']:
                hls_urls.append(d['url'])
            for e in live_data['hds']:
                hds_urls.append(e['url'])
        elif vod_data:
            self.logger.debug('Found vod_data')
            hls_urls.append(vod_data['m3u8'])
            hds_urls.append(vod_data['default'])
        else:
            self.logger.error('restricted access to this video for your region')
            raise NoStreamsError(self.url)

        for hls_url in hls_urls:
            self.logger.debug('HLS URL: {0}'.format(hls_url))
            for s in HLSStream.parse_variant_playlist(self.session, hls_url).items():
                yield s

        for hds_url in hds_urls:
            self.logger.debug('HDS URL: {0}'.format(hds_url))
            for s in HDSStream.parse_manifest(self.session, hds_url).items():
                yield s


__plugin__ = RUtube
