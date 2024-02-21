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
#TARGET_IP = "10.0.2.5"
RATE_C = 1#初始速度mbps
RATE_T = 0
RATE_AI = 5
CYCLE_N = 5#循环次数N
CYCLE_CUR = 5#快速恢复循环计数器n
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
        print("逐渐增加")
        RATE_T += RATE_AI
        RATE_C = (RATE_T + RATE_C) / 2
    elif SEND_STATE == "recover":
        if CYCLE_CUR > 0:
            print("快速恢复")
            RATE_C = (RATE_T + RATE_C) / 2
            CYCLE_CUR -= 1
        else:#"recover"--->"increase"
            print("逐渐增加")
            SEND_STATE = "increase"
            RATE_T += RATE_AI
            RATE_C = (RATE_T + RATE_C) / 2
    return RATE_C

def send_pkt(addr):
    global RATE_C
    global RATE_T
    global SEND_STATE
    global CYCLE_CUR

    
    #addr = socket.gethostbyname(TARGET_IP)
    iface = get_if()
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")/IP(dst=addr, tos=1, options = IPOption_INT(count=0, int_headers=[]))/UDP(dport=4321, sport=1234)
    payload_s = "\x00" * (100 - len(pkt))#\x00占一字节
    pkt = pkt / payload_s

    while SEND_SWITCH==True:       
        if SEND_STATE != "reduction":#状态不是减少
            RATE_C = send_rate();

        #RATE_PPS = RATE_C * 1000 / 8 * 1000 / 100 
        RATE_PPS = RATE_C * 1000000 / (8 * 100)         
        pkt.time=time.time()
        #sendpfast(pkt, pps=RATE_C, loop=RATE_C, iface=iface)
        sendpfast(pkt, mbps=RATE_C, loop=RATE_PPS, iface=iface)
        print("RATE: ",RATE_C)




def on_fbp_recv(p):
    global RATE_C
    global RATE_T
    global CYCLE_CUR
    global SEND_STATE
    global pkt_count
    global temp1
    global temp2
    #50个返回一个
    if p.haslayer("IP") and p["IP"].tos == 3:
        pkt_count = pkt_count+1
        #'''
        if p.haslayer(IPOption_INT):
            options = p.getlayer(IPOption_INT)
            qdepth = options.int_headers[0].qdepth
            lambda1 = options.int_headers[0].lambda1
            lambda2 = options.int_headers[0].lambda2
            #if lambda1 != temp1 and lambda2 != temp2:#当返回的系数与上一个反馈包不同时改变速率
            #if lambda2 != temp2:#当返回的系数与上一个反馈包不同时改变速率
            if pkt_count>=50: #50个包改变一次
                SEND_STATE = "reduction"
                print("速度减少") #reduction
                RATE_T = RATE_C
                #temp1 = lambda1#记录lambda1和2
                #temp2 = lambda2
                if(lambda1!=0 and lambda2!=0 and lambda2<lambda1):
                #if lambda1!=0:
                    print(lambda1,lambda2)
                    if lambda2/lambda1>0.5:
                        RATE_C = RATE_C * (lambda2/lambda1)
                        print("有解RATE: ",RATE_C)
                else:
                    BETA = random.uniform(0,1)
                    RATE_C = RATE_C * (1 - BETA/2)
                    print("RATE-bate: ",RATE_C)
                CYCLE_CUR = CYCLE_N
                SEND_STATE = "recover"
                pkt_count = 0#计数器清零
        '''
        if pkt_count>=50:           
            SEND_STATE = "reduction"
            RATE_T = RATE_C
            BETA = random.uniform(0,1)
            RATE_C = RATE_C * (1 - BETA/2)
            CYCLE_CUR = CYCLE_N
            print("正常RATE: ",RATE_C)
            SEND_STATE = "recover" 
            pkt_count = 0
        else:
            pky_count = pkt_count + 1
        '''
    else:
        return

   
        
    '''23
    if p.haslayer("IP") and p["IP"].tos == 3:
        if p.haslayer(IPOption_INT):
                #p.show2()
            options = p.getlayer(IPOption_INT)
                #print(options)
            qdepth = options.int_headers[0].qdepth
            lambda1 = options.int_headers[0].lambda1
            lambda2 = options.int_headers[0].lambda2
            if lambda1 != temp1 and lambda2 != temp2:#当返回的系数与上一个反馈包不同时降低速率
                temp1 = lambda1#记录lambda1和2
                temp2 = lambda2
                print(lambda1,lambda2)
                if(lambda1==0 or lambda2==0 or lambda2>=lambda1):#vt=0或者无解
                    SEND_STATE = "reduction"
                    RATE_T = RATE_C
                    BETA = random.uniform(0,1)
                    RATE_C = RATE_C * (1 - BETA/2)
                    CYCLE_CUR = CYCLE_N

                    print("无解RATE: ",RATE_C)

                    SEND_STATE = "recover" 
                else:
                    SEND_STATE = "reduction"
                    RATE_T = RATE_C
                    RATE_C = RATE_C * (lambda2/lambda1)
                    CYCLE_CUR = CYCLE_N
                    print("有解RATE: ",RATE_C)
                    SEND_STATE = "recover"  
    '''
                 
    '''
        SEND_STATE = "reduction"
        #print("got a feedback packet")            
        #print("速度减少") #reduction
        RATE_T = RATE_C
        RATE_C = RATE_C * (1 - BETA/2)
        CYCLE_CUR = CYCLE_N
        print("RATE: ",RATE_C)
        SEND_STATE = "recover"
    '''


def check_fbp():
    #sniff(prn=lambda x:on_fbp_recv(x), count=0, iface="h1-eth0")#count:指定最多嗅探多少个符合要求的报文，设置为0时则一直捕获
    iface = get_if()
    sniff(iface= iface, prn=lambda x:on_fbp_recv(x), count =0)

def main():
    #python RP.py 10.0.1.4
    ip = socket.gethostbyname(sys.argv[1])
    #iface = get_if()
    #print(iface)
    #t1 = threading.Thread(target=check_fbp)
    t1 = threading.Thread(target=check_fbp)
    t2 = threading.Thread(target=send_pkt, args=(ip,))
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()

