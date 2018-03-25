import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HDSStream
from livecli.stream import HLSStream
from livecli.stream import HTTPStream

__livecli_docs__ = {
    "domains": [
        "ap.vgtv.no",
        "tv.aftonbladet.se",
        "vgtv.no",
    ],
    "geo_blocked": [
        "NO",
        "SE",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-02-18",
}


class VGTV(Plugin):
    """
        Plugin for VGTV, Norwegian newspaper VG Nett's streaming service.
        Plugin for swedish news paper Aftonbladet's streaming service.
    """

    _url_re = re.compile(r"""https?://(?:www\.)?
        (?P<host>
            tv\.aftonbladet\.se/abtv
            |
            (?:ap\.)?vgtv\.no
        )
        (?:/webtv(?:[^/]+)?)?
        /[^/]+/(?P<id>\d+)
        """, re.VERBOSE)

    appname_map = {
        "ap.vgtv.no": "aptv",
        "tv.aftonbladet.se/abtv": "abtv",
        "vgtv.no": "vgtv",
    }

    apiname_map = {
        "abtv": "ab",
        "aptv": "ap",
        "vgtv": "vgtv",
    }

    api_url = "https://svp.vg.no/svp/api/v1/{0}/assets/{1}?appName={2}-website"

    _video_schema = validate.Schema(
        {
            validate.optional("title"): validate.text,
            validate.optional("assetType"): validate.text,
            validate.optional("streamType"): validate.text,
            validate.optional("status"): validate.text,
            "streamUrls": {
                validate.optional("hls"): validate.any(validate.text, None),
                validate.optional("hds"): validate.any(validate.text, None),
                validate.optional("mp4"): validate.any(validate.text, None),
            },
        }
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        m_url = self._url_re.match(self.url)
        if not m_url:
            return

        video_id = m_url.group("id")
        appname = self.appname_map[m_url.group("host")]
        apiname = self.apiname_map[appname]

        headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url
        }

        res = http.get(self.api_url.format(apiname, video_id, appname), headers=headers)
        data = http.json(res, schema=self._video_schema)

        title = data.get("title")
        streamurls = data.get("streamUrls")

        if title:
            self.stream_title = title

        if streamurls:
            hls_url = streamurls.get("hls")
            if hls_url:
                self.logger.debug("HLS URL: {0}".format(hls_url))
                streams = HLSStream.parse_variant_playlist(self.session, hls_url, headers=headers).items()
                if not streams:
                    yield "live", HLSStream(self.session, hls_url, headers=headers)
                for s in streams:
                    yield s

            hds_url = streamurls.get("hds")
            if hds_url:
                self.logger.debug("HDS URL: {0}".format(hds_url))
                for s in HDSStream.parse_manifest(self.session, hds_url, headers=headers).items():
                    yield s

            mp4_url = streamurls.get("mp4")
            if mp4_url:
                self.logger.debug("MP4 URL: {0}".format(mp4_url))
                name = "live"
                yield name, HTTPStream(self.session, mp4_url, headers=headers)


__plugin__ = VGTV
