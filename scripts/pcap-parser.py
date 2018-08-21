#!/usr/local/bin/python2.7

import dpkt

filename='/Users/kevin/Documents/quic-results/network/20180813-191642/client/client-quicker/ngtcp2-2g_loss-index.html.pcap'
start_ts = None
for ts, pkt in dpkt.pcap.Reader(open(filename,'r')):

    if start_ts is None:
        print("timestamp: 0")
        start_ts = ts
    else:
        print("timestamp: " + str(ts - start_ts))
    eth = dpkt.sll.SLL(pkt)
    ip=eth.data
    print("ip proto: " + str(ip.p))

    if ip.p!=dpkt.ip.IP_PROTO_UDP:
       continue
    udp_packet =ip.data
    print("src port: " + str(udp_packet.sport))
    print("dst port: " + str(udp_packet.dport))
