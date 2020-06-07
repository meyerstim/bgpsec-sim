#!/bin/sh
echo "Fetching announcement history from RIPE (2 files)"
wget -O as29256.json 'https://stat.ripe.net/data/bgp-updates/data.json?resource=AS29256&starttime=2014-12-09T08:00&endtime=2014-12-09T09:00'
wget -O as29386.json 'https://stat.ripe.net/data/bgp-updates/data.json?resource=AS29386&starttime=2014-12-09T08:00&endtime=2014-12-09T09:00'

jq ".data.updates[].attrs.target_prefix" < as29256.json | sed s/\"//g | sort -n | uniq > /tmp/as29256-updated-prefixes.txt
jq ".data.updates[].attrs.target_prefix" < as29386.json | sed s/\"//g | sort -n | uniq > /tmp/as29386-updated-prefixes.txt

echo "Fetching all prefixes announced in the prior month"
wget -O as29256-legitimate-prefixes.json 'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS29256&starttime=2014-11-09T08:00&endtime=2014-12-09T08:00'
wget -O as29386-legitimate-prefixes.json 'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS29386&starttime=2014-11-09T08:00&endtime=2014-12-09T08:00'

jq ".data.prefixes[].prefix" < as29256-legitimate-prefixes.json | sed s/\"//g > /tmp/as29256-legitimate-prefixes.txt
jq ".data.prefixes[].prefix" < as29386-legitimate-prefixes.json | sed s/\"//g > /tmp/as29386-legitimate-prefixes.txt

echo "Removing legitimate prefix announcements"
diff --new-line-format="" --unchanged-line-format="" /tmp/as29256-updated-prefixes.txt /tmp/as29256-legitimate-prefixes.txt > /tmp/as29256-hijacked-prefixes.txt
diff --new-line-format="" --unchanged-line-format="" /tmp/as29386-updated-prefixes.txt /tmp/as29386-legitimate-prefixes.txt > /tmp/as29386-hijacked-prefixes.txt

echo "Looking up ASNs for $(wc -l "/tmp/as29256-hijacked-prefixes.txt" | cut -d' ' -f1) + $(wc -l "/tmp/as29386-hijacked-prefixes.txt" | cut -d' ' -f1) prefixes, this might take a while!"
python3 lookup-asn-list.py 2014-12-09T08:00 < /tmp/as29256-hijacked-prefixes.txt > asn29256-victims.txt
python3 lookup-asn-list.py 2014-12-09T08:00 < /tmp/as29386-hijacked-prefixes.txt > asn29386-victims.txt

grep asn\" asn29256-victims.txt | cut -d: -f2 | sed s/" "//g | sed s/\\\\n\'//g | sort -n | uniq > asn29256-victim-ASNs.txt
grep asn\" asn29386-victims.txt | cut -d: -f2 | sed s/" "//g | sed s/\\\\n\'//g | sort -n | uniq > asn29386-victim-ASNs.txt