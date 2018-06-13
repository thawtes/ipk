# IPK

Livecli repacked as ipkg for E2 receiver.

- source: https://github.com/back-to/ipk
- liveproxy: https://github.com/back-to/liveproxy
- streamlink: https://github.com/streamlink/streamlink

# GUIDE

A Guide can be found at

- https://liveproxy.github.io/
- https://liveproxy.github.io/install.html#enigma2

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

# DEVELOPER INSTRUCTIONS

create an .ipk file from the source folder.

Example for python-iso3166

```sh
$ cd build
$ ../source/ipkg-build ../source/python-livecli/
sha256sum *.ipk > sha256sum.txt
sha256sum -c sha256sum.txt
```

Remove **.pyc** with `find . -name '*.pyc' -delete`

source of the ipkg-build file
- http://reichholf.net/files/dreambox/tools/ipkg-build
