import os

from livecli import __version__ as LIVECLI_VERSION
from livecli.compat import is_win32

DEFAULT_PLAYER_ARGUMENTS = "{filename}"

if is_win32:
    APPDATA = os.environ["APPDATA"]
    CONFIG_FILES = [os.path.join(APPDATA, "livecli", "liveclirc")]
    PLUGINS_DIR = os.path.join(APPDATA, "livecli", "plugins")
    USERPROFILE = os.environ["userprofile"]
    DOWNLOAD_DIR = os.path.join(USERPROFILE, "Downloads")
else:
    HOME = os.path.expanduser("~")
    DOWNLOAD_DIR = os.environ.get("XDG_DOWNLOAD_DIR") or os.path.join(HOME, "Downloads")
    XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME") or os.path.join(HOME, ".config")
    CONFIG_FILES = [
        os.path.expanduser(XDG_CONFIG_HOME + "/livecli/config"),
        os.path.expanduser("~/.liveclirc")
    ]
    PLUGINS_DIR = os.path.expanduser(XDG_CONFIG_HOME + "/livecli/plugins")

STREAM_SYNONYMS = ["best", "worst"]
STREAM_PASSTHROUGH = ["hls", "http", "rtmp"]

__all__ = [
    "CONFIG_FILES",
    "DEFAULT_PLAYER_ARGUMENTS",
    "DOWNLOAD_DIR",
    "LIVECLI_VERSION",
    "PLUGINS_DIR",
    "STREAM_PASSTHROUGH",
    "STREAM_SYNONYMS",
]
