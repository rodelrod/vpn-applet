#!/usr/bin/env bash
if [ $EUID -ne 0 ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi
service ipsec restart
service xl2tpd restart
ipsec auto --up rueil
xl2tpd-control connect rueil
