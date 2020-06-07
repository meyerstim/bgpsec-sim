#!/bin/sh
echo "Fetching announcement history from RIPE"
wget -O as48685.json 'https://stat.ripe.net/data/bgp-updates/data.json?resource=as48685&starttime=2013-07-31T07:00&endtime=2013-07-31T09:00'

jq ".data.updates[].attrs.target_prefix" < as48685.json | sed s/\"//g | sort -n | uniq > /tmp/as48685-updated-prefixes.txt

echo "Fetching all prefixes announced in the prior month"
wget -O as48685-legitimate-prefixes.json 'https://stat.ripe.net/data/announced-prefixes/data.json?resource=as48685&starttime=2013-06-30T08:00&endtime=2013-07-31T07:00'

jq ".data.prefixes[].prefix" < as48685-legitimate-prefixes.json | sed s/\"//g > /tmp/as48685-legitimate-prefixes.txt

echo "Removing legitimate prefix announcements"
diff --new-line-format="" --unchanged-line-format="" /tmp/as48685-updated-prefixes.txt /tmp/as48685-legitimate-prefixes.txt > /tmp/as48685-hijacked-prefixes.txt

echo "Looking up ASNs for $(wc -l "/tmp/as48685-hijacked-prefixes.txt" | cut -d' ' -f1) prefixes, this might take a while!"
python3 lookup-asn-list.py 2013-07-31T07:00 < /tmp/as48685-hijacked-prefixes.txt > as48685-victims.txt

grep asn\" as48685-victims.txt | cut -d: -f2 | sed s/" "//g | sed s/\\\\n\'//g | sort -n | uniq > as48685-victim-ASNs.txt