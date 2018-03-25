import re
import json

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HDSStream
from livecli.stream import HLSStream
from livecli.stream import HTTPStream
from livecli.utils import update_scheme

__livecli_docs__ = {
    "domains": [
        "sportschau.de",
    ],
    "geo_blocked": [
        "DE",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-02-26",
}


class Sportschau(Plugin):

    _url_re = re.compile(r"https?://(\w+\.)?sportschau\.de/")
    _player_js = re.compile(r"https?://deviceids-medp\.wdr\.de/ondemand/.*\.js")
    _data_re = re.compile(r"""(?P<data>{[^)(]+})""")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        res = http.get(self.url)
        match = self._player_js.search(res.text)
        if match:
            player_js = match.group(0)
            self.logger.info("Found player js {0}", player_js)
        else:
            self.logger.info("Didn't find player js. Probably this page doesn't contain a video")
            return

        res = http.get(player_js)
        m = self._data_re.search(res.text)
        if not m:
            self.logger.info("Couldn't extract json metadata from player.js: {0}", player_js)
            return

        stream_metadata = json.loads(m.group("data"))
        is_video = stream_metadata["mediaType"] in ["live", "vod"]
        is_audio = stream_metadata["mediaType"] == "aod"

        media_version = tuple([int(d) for d in stream_metadata["mediaVersion"].split("-")[0].split(".")])

        if is_video or is_audio:
            media_url = stream_metadata["mediaResource"]["dflt"]["videoURL" if is_video else "audioURL"]
            media_url_alt = stream_metadata["mediaResource"]["alt"]["videoURL" if is_video else "audioURL"]
            media_name = "audio" if is_audio else "vod"

            if media_version >= (1, 2, 0):
                media_format = stream_metadata["mediaResource"]["dflt"]["mediaFormat"]
                media_format_alt = stream_metadata["mediaResource"]["alt"]["mediaFormat"]
            else:
                media_format = stream_metadata["mediaFormat"]
                media_format_alt = media_url_alt[-4:]

            stream_url = {
                "url": media_url,
                "format": media_format,
                "name": media_name
            }

            stream_url_alt = {
                "url": media_url_alt,
                "format": media_format_alt,
                "name": media_name
            }

            for stream in [stream_url, stream_url_alt]:
                url = update_scheme("http://", stream["url"])
                try:
                    if stream["format"] in ["hds", ".f4m"]:
                        for s in HDSStream.parse_manifest(self.session, url, is_akamai=True).items():
                            yield s
                    elif stream["format"] in ["hls", "m3u8"]:
                        streams = HLSStream.parse_variant_playlist(self.session, url).items()
                        if not streams:
                            yield "live", HLSStream(self.session, url)
                        for s in streams:
                            yield s
                    elif stream["format"] in ["mp3", "mp4", ".mp3", ".mp4"]:
                        yield stream["name"], HTTPStream(self.session, url)
                except IOError as err:
                    self.logger.error("Failed to extract {0} streams: {1}",
                                      stream["format"], err)


__plugin__ = Sportschau
