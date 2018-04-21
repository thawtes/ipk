import re


def comma_list(values):
    return [val.strip() for val in values.split(",")]


def filesize(value):
    _filesize_re = re.compile("""
        (?P<size>\d+(\.\d+)?)
        (?P<modifier>[Kk]|[Mm])?
        (?:[Bb])?
    """, re.VERBOSE)
    match = _filesize_re.match(value)
    if not match:
        raise ValueError

    size = float(match.group("size"))
    if not size:
        raise ValueError

    modifier = match.group("modifier")
    if modifier in ("M", "m"):
        size *= 1024 * 1024
    elif modifier in ("K", "k"):
        size *= 1024

    return int(size)


def keyvalue(value):
    _keyvalue_re = re.compile("(?P<key>[^=]+)\s*=\s*(?P<value>.*)")
    match = _keyvalue_re.match(value)
    if not match:
        raise ValueError

    return match.group("key", "value")


def command_session(session, old_data):
    """ create a new dict and resolve all commands to the session """
    valid_cmd = {
        # data_other
        "cache": "data_other",
        "hls-session-reload": "data_other",
        "l": "data_other",
        "loglevel": "data_other",
        "url": "data_other",
        # data_other_comma_list
        "default-stream": "data_other_comma_list",
        "q": "data_other_comma_list",
        "quality": "data_other_comma_list",
        "stream-sorting-excludes": "data_other_comma_list",
        "stream-types": "data_other_comma_list",
        "stream": "data_other_comma_list",
        # set_option_store - other
        "http-ignore-env": "http-ignore-env",
        "http-no-ssl-verify": "http-no-ssl-verify",
        "ringbuffer-size": "ringbuffer-size",
        # set_option_store_true
        "ffmpeg-verbose": "set_option_store_true",
        "hls-live-restart": "set_option_store_true",
        "http-disable-dh": "set_option_store_true",
        # set_option_comma_list
        "hls-audio-select": "set_option_comma_list",
        "hls-segment-ignore-names": "set_option_comma_list",
        # set_option
        "ffmpeg-audio-transcode": "set_option",
        "ffmpeg-ffmpeg": "set_option",
        "ffmpeg-verbose-path": "set_option",
        "ffmpeg-video-transcode": "set_option",
        "hls-key-uri": "set_option",
        "http-proxy": "set_option",
        "http-ssl-cert": "set_option",
        "https-proxy": "set_option",
        "locale": "set_option",
        "rtmp-proxy": "set_option",
        "rtmp-rtmpdump": "set_option",
        "subprocess-errorlog-path": "set_option",
        # set_option_num
        "hds-live-edge": "set_option_num",
        "hds-segment-attempts": "set_option_num",
        "hds-segment-threads": "set_option_num",
        "hds-segment-timeout": "set_option_num",
        "hds-timeout": "set_option_num",
        "hls-live-edge": "set_option_num",
        "hls-playlist-reload-attempts": "set_option_num",
        "hls-segment-attempts": "set_option_num",
        "hls-segment-ignore-number": "set_option_num",
        "hls-segment-threads": "set_option_num",
        "hls-segment-timeout": "set_option_num",
        "hls-timeout": "set_option_num",
        "http-stream-timeout": "set_option_num",
        "http-timeout": "set_option_num",
        "rtmp-timeout": "set_option_num",
        "stream-segment-attempts": "set_option_num",
        "stream-segment-threads": "set_option_num",
        "stream-segment-timeout": "set_option_num",
        "stream-timeout": "set_option_num",
        # hours_minutes_seconds as set_option_num
        "hls-duration": "set_option_num",
        "hls-start-offset": "set_option_num",
        # keyvalue set_option_key
        "http-cookie": "set_option_key",
        "http-header": "set_option_key",
        "http-query-param": "set_option_key",
        # set_plugin_option_value
        "abweb-password": "set_plugin_option_value",
        "abweb-username": "set_plugin_option_value",
        "afreeca-password": "set_plugin_option_value",
        "afreeca-username": "set_plugin_option_value",
        "animelab-email": "set_plugin_option_value",
        "animelab-password": "set_plugin_option_value",
        "bbciplayer-password": "set_plugin_option_value",
        "bbciplayer-username": "set_plugin_option_value",
        "btv-password": "set_plugin_option_value",
        "btv-username": "set_plugin_option_value",
        "crunchyroll-password": "set_plugin_option_value",
        "crunchyroll-session-id": "set_plugin_option_value",
        "crunchyroll-username": "set_plugin_option_value",
        "funimation-language": "set_plugin_option_value",
        "liveedu-email": "set_plugin_option_value",
        "liveedu-password": "set_plugin_option_value",
        "pixiv-password": "set_plugin_option_value",
        "pixiv-username": "set_plugin_option_value",
        "schoolism-email": "set_plugin_option_value",
        "schoolism-part": "set_plugin_option_value",
        "schoolism-password": "set_plugin_option_value",
        "tvplayer-email": "set_plugin_option_value",
        "tvplayer-password": "set_plugin_option_value",
        "twitch-oauth-token": "set_plugin_option_value",
        "ustream-password": "set_plugin_option_value",
        "wwenetwork-email": "set_plugin_option_value",
        "wwenetwork-password": "set_plugin_option_value",
        "zattoo-email": "set_plugin_option_value",
        "zattoo-password": "set_plugin_option_value",
        # set_plugin_option_comma_list
        "resolve-blacklist-netloc": "set_plugin_option_comma_list",
        "resolve-blacklist-path": "set_plugin_option_comma_list",
        "resolve-whitelist-netloc": "set_plugin_option_comma_list",
        "resolve-whitelist-path": "set_plugin_option_comma_list",
        # set_plugin_option_store_true
        "abweb-purge-credentials": "set_plugin_option_store_true",
        "funimation-mux-subtitles": "set_plugin_option_store_true",
        "npo-subtitles": "set_plugin_option_store_true",
        "pluzz-mux-subtitles": "set_plugin_option_store_true",
        "resolve-turn-off": "set_plugin_option_store_true",
        "rtve-mux-subtitles": "set_plugin_option_store_true",
        "twitch-oauth-authenticate": "set_plugin_option_store_true",
        "zattoo-purge-credentials": "set_plugin_option_store_true",
    }

    set_plugin_option = {
        "abweb-password": ("abweb", "password"),
        "abweb-username": ("abweb", "username"),
        "afreeca-password": ("afreeca", "password"),
        "afreeca-username": ("afreeca", "username"),
        "animelab-email": ("animelab", "email"),
        "animelab-password": ("animelab", "password"),
        "bbciplayer-password": ("bbciplayer", "password"),
        "bbciplayer-username": ("bbciplayer", "username"),
        "btv-password": ("btv", "password"),
        "btv-username": ("btv", "username"),
        "crunchyroll-password": ("crunchyroll", "password"),
        "crunchyroll-session-id": ("crunchyroll", "session_id"),
        "crunchyroll-username": ("crunchyroll", "username"),
        "funimation-language": ("funimation", "language"),
        "liveedu-email": ("liveedu", "email"),
        "liveedu-password": ("liveedu", "password"),
        "pixiv-password": ("pixiv", "password"),
        "pixiv-username": ("pixiv", "username"),
        "resolve-blacklist-netloc": ("resolve", "blacklist_netloc"),
        "resolve-blacklist-path": ("resolve", "blacklist_path"),
        "resolve-whitelist-netloc": ("resolve", "whitelist_netloc"),
        "resolve-whitelist-path": ("resolve", "whitelist_path"),
        "schoolism-email": ("schoolism", "email"),
        "schoolism-part": ("schoolism", "part"),
        "schoolism-password": ("schoolism", "password"),
        "tvplayer-email": ("tvplayer", "email"),
        "tvplayer-password": ("tvplayer", "password"),
        "twitch-oauth-token": ("twitch", "oauth_token"),
        "ustream-password": ("ustreamtv", "password"),
        "wwenetwork-email": ("wwenetwork", "email"),
        "wwenetwork-password": ("wwenetwork", "password"),
        "zattoo-email": ("zattoo", "email"),
        "zattoo-password": ("zattoo", "password"),
    }

    data_other = {}
    for cmd, value in old_data:
        status_cmd = valid_cmd.get(cmd)
        if status_cmd in ["set_plugin_option_value",
                          "set_plugin_option_comma_list",
                          "set_plugin_option_store_true"]:
            for plugin_name, plugin_option in [set_plugin_option[cmd]]:
                if status_cmd == "set_plugin_option_comma_list":
                    value = comma_list(value)
                elif status_cmd == "set_plugin_option_store_true":
                    value = True
                session.set_plugin_option(plugin_name, plugin_option, value)
        elif status_cmd in ["set_option",
                            "set_option_num",
                            "set_option_comma_list",
                            "set_option_store_true",
                            "set_option_key"]:
            if status_cmd == "set_option_num":
                try:
                    value = int(value)
                except ValueError:
                    continue
            elif status_cmd == "set_option_comma_list":
                value = comma_list(value)
            elif status_cmd == "set_option_store_true":
                value = True
            elif status_cmd == "set_option_key":
                value = keyvalue(value)
            session.set_option(cmd, value)
        elif status_cmd == "http-no-ssl-verify":
            session.set_option("http-ssl-verify", False)
        elif status_cmd == "http-ignore-env":
            session.set_option("http-trust-env", False)
        elif status_cmd == "ringbuffer-size":
            value = filesize(value)
            session.set_option(cmd, value)
        elif status_cmd in ["data_other", "data_other_comma_list"]:
            if status_cmd == "data_other_comma_list":
                value = comma_list(value)
            data_other[cmd] = value

    return data_other, session


__all__ = ["command_session"]
