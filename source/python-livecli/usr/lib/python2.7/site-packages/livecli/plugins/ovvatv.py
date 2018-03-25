import re

from base64 import b64decode
from datetime import datetime

from livecli import PluginError
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream
from livecli.utils import parse_json

__livecli_docs__ = {
    "domains": [
        "1plus1.video",
    ],
    "geo_blocked": [
        "UA",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-02-14",
}


class ovvaTV(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?1plus1\.video/tvguide/embed/[^/]")
    data_re = re.compile(r"""ovva-player["'],["'](.*?)["']\)};""")
    next_date_re = re.compile(r"""<div\sclass=["']o-message-timer['"]\sdata-timer=["'](\d+)["']""")
    ovva_data_schema = validate.Schema({
        "balancer": validate.url()
    }, validate.get("balancer"))
    ovva_redirect_schema = validate.Schema(validate.all(
        validate.transform(lambda x: x.split("=")),
        ['302', validate.url()],
        validate.get(1)
    ))

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url)
        data = self.data_re.search(res.text)
        next_date = self.next_date_re.search(res.text)
        if data:
            try:
                ovva_url = parse_json(b64decode(data.group(1)).decode("utf8"), schema=self.ovva_data_schema)
                stream_url = http.get(ovva_url, schema=self.ovva_redirect_schema)
            except PluginError as e:
                self.logger.error("Could not find stream URL: {0}", e)
            else:
                return HLSStream.parse_variant_playlist(self.session, stream_url)
        elif next_date:
            self.logger.info("The broadcast will be available at {0}".format(
                datetime.fromtimestamp(int(next_date.group(1))).strftime('%Y-%m-%d %H:%M:%S')))
        else:
            self.logger.error("Could not find player data.")


__plugin__ = ovvaTV
