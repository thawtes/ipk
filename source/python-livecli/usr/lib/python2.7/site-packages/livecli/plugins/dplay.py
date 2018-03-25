import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "dplay.se",
        "dplay.no",
        "dplay.dk",
    ],
    "geo_blocked": [
        "DK",
        "SE",
        "NO",
    ],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "2018-02-16",
}

_api_schema = validate.Schema(
    {
        'data': validate.Schema(
            {
                'attributes': validate.Schema(
                    {
                        'streaming': {
                            'hls': {
                                'url': validate.text,
                            }
                        }
                    },
                    validate.get('streaming')
                )
            },
            validate.get('attributes')
        )
    },
    validate.get('data')
)


class Dplay (Plugin):
    """Plugin for Dplay service."""

    _url_re = re.compile(r'''https?://(?:www\.)?(?P<host>dplay\.(?P<country>dk|se|no))/(?:video(?:er|s)/)?(?P<id>[^/]+/[^/?#]+)''')
    _videoid_re = re.compile(r'''data-video-id=["'](?P<id>[^"']+)''')

    _api_url = 'https://disco-api.{0}'

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        m_url = self._url_re.match(self.url)

        host = m_url.group('host')
        id_url = m_url.group('id')

        api_url = self._api_url.format(host)
        headers = {'User-Agent': useragents.FIREFOX}

        res = http.get(self.url, headers=headers)
        m = self._videoid_re.search(res.text)
        if m:
            video_id = m.group('id')
        else:
            http.get('{0}/token'.format(api_url), params={'realm': host.replace('.', '')})
            headers2 = {
                'User-Agent': useragents.FIREFOX,
                'Referer': self.url,
                'x-disco-client': 'WEB:UNKNOWN:dplay-client:0.0.1'
            }
            try:
                res = http.get('{0}/content/videos/{1}'.format(api_url, id_url), headers=headers2)
            except Exception as e:
                if '404' in str(e):
                    self.logger.error('No video found on this url.')
                return
            data = http.json(res)
            if data:
                video_id = data['data']['id']

        if not video_id:
            self.logger.error('Found no video id')
            return

        res = http.get('{0}/playback/videoPlaybackInfo/{1}'.format(api_url, video_id), headers=headers)
        data = http.json(res, schema=_api_schema)

        if not data:
            return

        hls_url = data['hls']['url']

        streams = HLSStream.parse_variant_playlist(self.session, hls_url, headers=headers)
        if not streams:
            return {'live': HLSStream(self.session, hls_url, headers=headers)}
        else:
            return streams


__plugin__ = Dplay
