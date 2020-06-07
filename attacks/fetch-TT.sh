#!/bin/sh
echo "Fetching announcement history from RIPE"
wget -O as9121.json 'https://stat.ripe.net/data/bgp-updates/data.json?resource=as9121&starttime=2014-03-29T8:30&endtime=2014-03-29T10:30'

jq ".data.updates[].attrs.target_prefix" < as9121.json | sed s/\"//g | sort -n | uniq > /tmp/as9121-updated-prefixes.txt
echo "Fetching all prefixes announced in the prior month"
wget -O as9121-legitimate-prefixes.json 'https://stat.ripe.net/data/announced-prefixes/data.json?resource=as9121&starttime=2014-02-28T08:00&endtime=2014-03-29T08:00'

jq ".data.prefixes[].prefix" < as9121-legitimate-prefixes.json | sed s/\"//g > /tmp/as9121-legitimate-prefixes.txt

echo "Removing legitimate prefix announcements"
diff --new-line-format="" --unchanged-line-format="" /tmp/as9121-updated-prefixes.txt /tmp/as9121-legitimate-prefixes.txt > /tmp/as9121-hijacked-prefixes.txt

echo "Looking up ASNs for $(wc -l /tmp/as9121-hijacked-prefixes.txt | cut -d' ' -f1) prefixes, this might take a while!"
python3 lookup-asn-list.py 2014-03-29T07:00 < /tmp/as9121-hijacked-prefixes.txt > as9121-victims.txt

grep asn\" as9121-victims.txt | cut -d: -f2 | sed s/" "//g | sed s/\\\\n\'//g | sort -n | uniq > as9121-victim-ASNs.txt