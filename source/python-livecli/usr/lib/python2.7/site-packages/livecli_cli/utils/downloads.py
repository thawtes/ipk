
def get_output_format(output_shortname):
    """creates an automated filetype name,
       it is not important if it is the right one.

       Default is .mp4
    """
    format_map = {
        ".flv": [
            "flv_playlist",
            "playlist",
            "rtmp",
        ],
        ".mp4": [
            "akamaihd",
            "hds",
            "http",
            "muxed-stream",
            "stream",
            "test",
        ],
        ".ts": [
            "hls-multi",
            "hls",
        ],
    }

    output_format = ".mp4"

    for _file_format, _file_type_list in format_map.items():
        for _file_type in _file_type_list:
            if not _file_type == output_shortname:
                continue
            else:
                output_format = _file_format
                break
    return output_format


def get_url_re_from_module(module):
    """Try to find _url_re from the current livecli module"""
    regex = ""
    try:
        regex = module._url_re
    except AttributeError:
        try:
            regex = module.url_re
        except AttributeError:
            import importlib
            mod = importlib.import_module(module.__module__)
            try:
                regex = mod._url_re
            except AttributeError:
                regex = mod.url_re
    return regex


def _filename_except(m, g):
    """Handles Exception for get_id_for_filename"""
    try:
        return m.group(g)
    except IndexError:
        return None


def get_id_for_filename(m):
    """Find a useful group item from _url_re"""
    filename = ""
    groups = [
        "username",
        "channel",
        "video_id",
        "videos_id",
        "video_id_2",
        "user",
        "broadcast_id",
        "liveChannel",
        "clip_name",
        "user_id",
    ]

    for item in groups:
        filename = _filename_except(m, item)
        if not filename:
            continue
        break

    return "" if filename is None else filename


__all__ = [
    "get_id_for_filename",
    "get_output_format",
    "get_url_re_from_module",
]
