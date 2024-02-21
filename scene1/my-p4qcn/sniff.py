#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import PacketListField, ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR
import time
class SwitchTrace(Packet):

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
                    ShortField("count", 0),#短整形字段，名字count，初始值0
                    PacketListField("int_headers",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]

def get_if():
#获取接口列表['lo','eth0','eth1','eth2']
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def handle_pkt(pkt):
    #print("got a packet")
    #pkt.show2()
    if pkt.haslayer(IPOption_INT):
        #p.show2()
        options = pkt.getlayer(IPOption_INT)
        #print(len(options))
        swid = options.int_headers[0].swid
        lambda1 = options.int_headers[0].lambda1
        lambda2 = options.int_headers[1].lambda1
        src = pkt[IP].src
        print(lambda2,lambda1)
        with open('priority.txt', 'a') as f:
            f.write(str(src)+":"+str(lambda2)+' '+str(lambda1)+'\n')
    '''
    if pkt.haslayer(IPOption_INT) and pkt[IP].tos==3:#发送方获取信息
        #p.show2()
        options = pkt.getlayer(IPOption_INT)
        print(len(options))
        swid = options.int_headers[0].swid
        lambda1 = options.int_headers[0].lambda1
        #lambda2 = options.int_headers[0].lambda2
        print(swid,lambda1)

    options = pkt.getlayer(IPOption_INT)
    print(options)
    print("--------------------------------------------------------")
    print(options.int_headers)
    print("--------------------------------------------------------")
    print(options.int_headers[0].qdepth)
    print(options.int_headers[0].pkt_length)
    print("--------------------------------------------------------")
    '''
    sys.stdout.flush()


def main():
    iface = get_if()
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="udp", iface = iface, prn = lambda x: handle_pkt(x))


if __name__ == '__main__':
    main()
