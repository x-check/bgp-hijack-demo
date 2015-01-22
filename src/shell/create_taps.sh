#!/bin/sh

## network interfaces for quagga bgpd
openvpn --mktun --dev tap1
openvpn --mktun --dev tap2
openvpn --mktun --dev tap3
openvpn --mktun --dev tap4
openvpn --mktun --dev tap5
openvpn --mktun --dev tap6
openvpn --mktun --dev tap7

ifconfig tap1 up 192.168.1.1 netmask 255.255.255.255
ifconfig tap2 up 192.168.1.2 netmask 255.255.255.255
ifconfig tap3 up 192.168.1.3 netmask 255.255.255.255
ifconfig tap4 up 192.168.1.4 netmask 255.255.255.255
ifconfig tap5 up 192.168.1.5 netmask 255.255.255.255
ifconfig tap6 up 192.168.1.6 netmask 255.255.255.255
ifconfig tap7 up 192.168.1.7 netmask 255.255.255.255

## network interface for bgpmon
openvpn --mktun --dev tap101
ifconfig tap101 up 192.168.1.101 netmask 255.255.255.255
openvpn --mktun --dev tap102
ifconfig tap102 up 192.168.1.102 netmask 255.255.255.255
openvpn --mktun --dev tap103
ifconfig tap103 up 192.168.1.103 netmask 255.255.255.255
