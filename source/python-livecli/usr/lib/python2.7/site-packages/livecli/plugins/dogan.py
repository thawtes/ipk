# coding=utf-8
from __future__ import print_function

import re

from livecli.compat import urljoin
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "teve2.com.tr",
        "kanald.com.tr",
        "dreamtv.com.tr",
        "cnnturk.com",
        "dreamturk.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-02-13",
}


class Dogan(Plugin):
    """
    Support for the live streams from Dogan Media Group channels
    """
    url_re = re.compile(r"""
        https?://(?:www\.)?(?:
            teve2\.com\.tr/(?:canli-yayin|filmler/.*|programlar/.*)
            |
            kanald\.com\.tr/.*
            |
            cnnturk\.com/canli-yayin
            |
            dreamt(?:urk|v)\.com\.tr/canli(?:-yayin)?
        )
    """, re.VERBOSE)
    playerctrl_re = re.compile(r'''<div[^>]*?ng-controller=(?P<quote>["'])(?:Live)?PlayerCtrl(?P=quote).*?>''', re.DOTALL)
    videoelement_re = re.compile(r'''<div[^>]*?id=(?P<quote>["'])video-element(?P=quote).*?>''', re.DOTALL)
    data_id_re = re.compile(r'''data-id=(?P<quote>["'])(?P<id>\w+)(?P=quote)''')
    content_id_re = re.compile(r'"content(?:I|i)d", "(\w+)"')
    content_api = "/actions/content/media/{id}"
    new_content_api = "/action/media/{id}"
    content_api_schema = validate.Schema({
        "Id": validate.text,
        "Media": {
            "Link": {
                "DefaultServiceUrl": validate.url(),
                validate.optional("ServiceUrl"): validate.any(validate.url(), ""),
                "SecurePath": validate.text,
            }
        }
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_content_id(self):
        res = http.get(self.url)
        # find the contentId
        content_id_m = self.content_id_re.search(res.text)
        if content_id_m:
            self.logger.debug("Found content_id_re")
            return content_id_m.group(1)

        # find the PlayerCtrl div
        player_ctrl_m = self.playerctrl_re.search(res.text)
        if player_ctrl_m:
            self.logger.debug("Found playerctrl_re")
            # extract the content id from the player control data
            player_ctrl_div = player_ctrl_m.group(0)
            content_id_m = self.data_id_re.search(player_ctrl_div)
            if content_id_m:
                return content_id_m.group("id")

        # find <div id="video-element"
        videoelement_m = self.videoelement_re.search(res.text)
        if videoelement_m:
            self.logger.debug("Found videoelement_re")
            # extract the content id from the player control data
            videoelement_div = videoelement_m.group(0)
            content_id_m = self.data_id_re.search(videoelement_div)
            if content_id_m:
                return content_id_m.group("id")

    def _get_hls_url(self, content_id):
        # make the api url relative to the current domain
        if "cnnturk" in self.url or "teve2.com.tr" in self.url:
            self.logger.debug("Using new content API url")
            api_url = urljoin(self.url, self.new_content_api.format(id=content_id))
        else:
            api_url = urljoin(self.url, self.content_api.format(id=content_id))

        apires = http.get(api_url)

        stream_data = http.json(apires, schema=self.content_api_schema)
        d = stream_data["Media"]["Link"]
        return urljoin((d["ServiceUrl"] or d["DefaultServiceUrl"]), d["SecurePath"])

    def _get_streams(self):
        content_id = self._get_content_id()
        if content_id:
            self.logger.debug("Loading content: {0}".format(content_id))
            hls_url = self._get_hls_url(content_id)
            return HLSStream.parse_variant_playlist(self.session, hls_url)
        else:
            self.logger.error("Could not find the contentId for this stream")


__plugin__ = Dogan
