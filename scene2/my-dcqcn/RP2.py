import socket
import time
import threading
import sys

from scapy.all import sniff,sendp, send, hexdump, get_if_list, get_if_hwaddr, sendpfast
from scapy.all import Packet, IPOption
from scapy.all import Ether, IP, UDP,Raw
from scapy.all import IntField, FieldListField, FieldLenField, ShortField, PacketListField, BitField
from scapy.layers.inet import _IPOption_HDR
import random

SEND_STATE = "increase"  # "recover" "increase"
SEND_SWITCH = True
#TARGET_IP = "10.0.0.2"
TARGET_IP = "10.0.2.5"

RATE_C = 1#mbps
RATE_T = 0
RATE_AI = 5
CYCLE_N = 5
CYCLE_CUR = 5
BETA = 1
pkt_count=0
temp1=0
temp2=0

class SwitchTrace(Packet):
    #32bit
    fields_desc = [ #BitField("priority", 0, 3),
                    #BitField("qdepth", 0,13),
                    #BitField("pkt_length", 0,16)
                    BitField("qdepth", 0,32),
                    BitField("lambda1",0,32),
                    BitField("lambda2",0,32),
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

def send_rate():
    global RATE_C
    global RATE_T
    global SEND_STATE
    global CYCLE_CUR
    global SEND_SWITCH
    if SEND_STATE == "increase":
        RATE_T += RATE_AI
        RATE_C = (RATE_T + RATE_C) / 2
    elif SEND_STATE == "recover":
        if CYCLE_CUR > 0:
            RATE_C = (RATE_T + RATE_C) / 2
            CYCLE_CUR -= 1
        else:#"recover"--->"increase"
            SEND_STATE = "increase"
            RATE_T += RATE_AI
            RATE_C = (RATE_T + RATE_C) / 2
    return RATE_C

def send_pkt():
    global RATE_C
    global RATE_T
    global SEND_STATE
    global CYCLE_CUR

    
    addr = socket.gethostbyname(TARGET_IP)
    iface = get_if()
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")/IP(dst=addr, tos=1, options = IPOption_INT(count=0, int_headers=[]))/UDP(dport=4321, sport=1234)
    payload_s = "\x00" * (100 - len(pkt))
    pkt = pkt / payload_s

    while SEND_SWITCH==True:       
        if SEND_STATE != "reduction":
            RATE_C = send_rate();

        RATE_PPS = RATE_C * 1000 / 8 * 1000 / 100        
        pkt.time=time.time()
        sendpfast(pkt, mbps=RATE_C, loop=RATE_PPS, iface=iface)
        print("RATE: ",RATE_C)




def on_fbp_recv(p):
    global RATE_C
    global RATE_T
    global CYCLE_CUR
    global SEND_STATE
    if p.haslayer("IP") and p["IP"].tos == 2:
        SEND_STATE = "reduction"
        RATE_T = RATE_C
        RATE_C = RATE_C * (1 - BETA/2)
        CYCLE_CUR = CYCLE_N
        print("RATE: ",RATE_C)
        SEND_STATE = "recover"            
    else:
        return



def check_fbp():
    iface = get_if()
    sniff(iface= iface, prn=lambda x:on_fbp_recv(x), count =0)

def main():

    t1 = threading.Thread(target=check_fbp)
    t2 = threading.Thread(target=send_pkt)
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()

