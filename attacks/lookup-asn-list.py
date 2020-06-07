from urllib.request import urlopen
import sys
for prefix in sys.stdin:
    # This is a time just before the STE hijacks were announced
    url = "https://stat.ripe.net/data/prefix-overview/data.json?resource=" + prefix[:-1] + "&querytime=2014-12-09T08:30"
    with urlopen(url) as f:
        for l in f:
            print(l)
