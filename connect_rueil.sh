#!/usr/bin/env bash
if [ $EUID -ne 0 ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi
service ipsec restart
service xl2tpd restart
ipsec auto --up rueil
xl2tpd-control connect rueil
sleep 3
ROUTE_EXISTS=`ip route show 172.27.4.128/25 | wc -l`
if [ $ROUTE_EXISTS -eq 0 ]; then
    route add -net 172.27.4.128/25 dev ppp0
fi
