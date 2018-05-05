import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.compat import urljoin
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "brittv.co.uk",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-04-22",
}


class BritTV(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?brittv\.co.uk/watch/")
    js_re = re.compile(r"""/js/brittv\.player\.js\.php\?key=([^'"]+)['"]""")
    player_re = re.compile(r"""src:\s?["'](https?://[^"']+)["']""")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        http.headers.update({"User-Agent": useragents.CHROME})
        res = http.get(self.url)
        self.logger.debug("search for js_re")
        m = self.js_re.search(res.text)
        if m:
            self.logger.debug("Found js key: {0}", m.group(1))
            js_url = m.group(0)
            http.headers.update({"Referer": self.url})
            res = http.get(urljoin(self.url, js_url))
            self.logger.debug("search for player_re")
            for url in self.player_re.findall(res.text):
                self.logger.debug("Found url: {0}".format(url))
                if "adblock" not in url:
                    yield "live", HLSStream(self.session, url)


__plugin__ = BritTV
