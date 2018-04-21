# IPK

Livecli repacked as ipkg for E2 receiver.

- source: https://github.com/livecli/ipk
- livecli: https://github.com/livecli/livecli

# INSTALLATION

This is only tested with a **Vu+ Duo2**

open the **terminal** and install ...

_install required packages_

```sh
opkg install python-futures
opkg install python-singledispatch
opkg install python-six
opkg install python-requests
```

_download and install all required packages from this repo_

```
cd /tmp

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-backports.shutil-get-terminal-size_1.0.0_all.ipk
opkg install /tmp/python-backports.shutil-get-terminal-size_1.0.0_all.ipk

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-backports.shutil-which_3.5.1_all.ipk
opkg install /tmp/python-backports.shutil-which_3.5.1_all.ipk

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-iso3166_0.8_all.ipk
opkg install /tmp/python-iso3166_0.8_all.ipk

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-iso639_0.4.5_all.ipk
opkg install /tmp/python-iso639_0.4.5_all.ipk

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-socks_1.6.8_all.ipk
opkg install /tmp/python-socks_1.6.8_all.ipk

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-websocket_0.47.0_all.ipk
opkg install /tmp/python-websocket_0.47.0_all.ipk

wget https://raw.githubusercontent.com/livecli/ipk/master/build/python-livecli_3.8.0_all.ipk
opkg install /tmp/python-livecli_3.8.0_all.ipk
```

_test livecli_

```
livecli -l debug
```

Install the server service script, this will only work for a receiver with `init.d`

```
wget https://raw.githubusercontent.com/livecli/ipk/master/build/enigma2-livecli-server_1.0.0_all.ipk
opkg install /tmp/enigma2-livecli-server_1.0.0_all.ipk
```

_start the server_

```
update-rc.d /etc/init.d/livecli-server defaults
```

### optional

if you want to use

- service **5001** gstplayer (gstreamer)
- service **5002** exteplayer3 (ffmpeg)

instead of

- service **4097** IPTV

```
opkg install enigma2-plugin-systemplugins-serviceapp
```

# HELPER

### m3u to userbouquet

convert m3u data to userbouquet data

- SEARCH

```
#EXTINF:-1 tvg-id="([^"']+)".+\n(http.+)
```

- REPLACE

```
#SERVICE 4097:0:1:0:0:0:0:0:0:0:$2:$1
#DESCRIPTION $1
```

### Network Time Protocol (NTP)

Known issue `SystemTimeWarning`

```
/usr/lib/python2.7/site-packages/requests/packages/urllib3/connection.py:303:
SystemTimeWarning: System time is way off (before 2014-01-01).
This will probably lead to SSL verification errors SystemTimeWarning
```

run **NTP** at the startup

```
update-rc.d /etc/init.d/ntpupdate.sh defaults
```

# DESCRIPTION

**Bouquet Example** for https://www.zdf.de/sender/zdf/zdf-live-beitrag-100.html

The basic livecli service path is

`http%3a//127.0.0.1%3a53473/play/?url=`

No `:` is allowed in an url, use `%3a`

Now encode the stream url with an [urlencoder](https://www.urlencoder.org)

`https://www.zdf.de/sender/zdf/zdf-live-beitrag-100.html`

changes to

`https%3A%2F%2Fwww.zdf.de%2Fsender%2Fzdf%2Fzdf-live-beitrag-100.html`

combinate the basic livecli service path and the stream url

`http%3a//127.0.0.1%3a53473/play/?url=https%3A%2F%2Fwww.zdf.de%2Fsender%2Fzdf%2Fzdf-live-beitrag-100.html`

with this url you can now build the valid bouquet data

```
#SERVICE 4097:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a53473/play/?url=https%3A%2F%2Fwww.zdf.de%2Fsender%2Fzdf%2Fzdf-live-beitrag-100.html:ZDF HD
#DESCRIPTION ZDF HD
```

# DEVELOPER INSTRUCTIONS

create an .ipk file from the source folder.

Example for python-iso3166

```sh
$ cd build
$ ../source/ipkg-build ../source/python-iso3166/
sha256sum *.ipk > sha256sum.txt
sha256sum -c sha256sum.txt
```

Remove **.pyc** with `find . -name '*.pyc' -delete`

source of the ipkg-build file
- http://reichholf.net/files/dreambox/tools/ipkg-build
