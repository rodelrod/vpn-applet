#!/usr/bin/env bash
if [ $EUID -ne 0 ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi
xl2tpd-control disconnect rueil
ipsec auto --down rueil
ROUTE_EXISTS=`ip route show 172.27.4.128/25 | wc -l`
if [ $ROUTE_EXISTS -eq 1 ]; then
    route del -net 172.27.4.128/25
fi
