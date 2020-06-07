# Usage: lookup-asn-list.py 2020-01-01T12:00 < [prefix-list] 
from urllib.request import urlopen
import sys

for prefix in sys.stdin:
    # This is a time just before the STE hijacks were announced
    url = "https://stat.ripe.net/data/prefix-overview/data.json?resource=" + prefix[:-1] + "&querytime=" + sys.argv[0]
    with urlopen(url) as f:
        for l in f:
            print(l)
