#!/usr/bin/env python

import argparse
import sys
import socket
import random, string
import struct
import time

from scapy.all import sniff,sendp, send, hexdump, get_if_list, get_if_hwaddr, sendpfast
from scapy.all import Packet, IPOption
from scapy.all import Ether, IP, UDP,Raw
from scapy.all import IntField, FieldListField, FieldLenField, ShortField, PacketListField, BitField
from scapy.layers.inet import _IPOption_HDR

from time import sleep

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class SwitchTrace(Packet):
    #32bit
    fields_desc = [ BitField("swid", 0, 32),
                    #BitField("qid", 0, 3),
                    #BitField("priority", 0, 3),
                    #BitField("qdepth", 0,13),
                    #BitField("portid",0,6)
                    #BitField("pkt_length", 0,16)
                    BitField("qdepth", 0,32),
                    BitField("lambda1",0,32),
                    #BitField("lambda2",0,32),
                  ]
    def extract_padding(self, p):
                return "", p

class IPOption_INT(IPOption):
    name = "INT"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="int_headers",
                                  adjust=lambda pkt,l:l*2+4),
                    ShortField("count", 0),
                    PacketListField("int_headers",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]

def main():
    #Get arguments#获取参数python3 send.py 10.0.1.3(目标ip)  
    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")/IP(dst=addr, tos=1, options = IPOption_INT(count=0, int_headers=[]))/UDP(dport=4321, sport=1234)
    payload_s = "\x00" * (100 - len(pkt))
    pkt = pkt / payload_s
    pkt.show2()
    rate=20
    pkt.time=time.time()
    #sendpfast(pkt, iface=iface, mbps=10, loop=200000)
    #sendp(pkt, iface=iface, count=100)
    while True:        
        sendpfast(pkt, iface=iface, mbps=1, loop=50)#3000包/秒#loop=2*rate效果最好 
        #RATE_PPS = 1 * 1000 / 8 * 1000 / 100  



if __name__ == '__main__':
    main()
