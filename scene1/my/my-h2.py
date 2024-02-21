
from p4utils.utils import thrift_API
import nnpy
import struct
from p4utils.utils.helper import load_topo

import time
import math


from GA.a import main2 #DE_best_1_Ltemplet#(((n+1)))


class controller():

    def __init__(self, port):
        self.port = port#监听端口
        pre_type = thrift_API.PreType.SimplePre

        self.controller = thrift_API.ThriftAPI(self.port, 'localhost', pre_type)
        

    def read_and_write(self):
        
        self.controller.register_reset("lambda_register")#初始化register
        self.controller.register_reset("my_register")
        self.controller.register_reset("usage")

        self.controller.register_write("my_register", int(10), 300)
        self.controller.register_write("my_register", int(17), 300)
        self.controller.register_write("my_register", int(24), 300)
        self.controller.register_write("my_register", int(11), 21)
        self.controller.register_write("my_register", int(18), 21)
        self.controller.register_write("my_register", int(25), 21)
        t1=time.time()#单位s
        while True:

            entries=self.controller.register_read("lambda_register")
            print("lambda_register:",entries)
            t2=time.time()
            t=t2-t1
            lambda1=entries[1]/t
            lambda2=entries[2]/t
            lambda3=entries[3]/t
            self.controller.register_reset("lambda_register")#重置lambda_register=0            
            t1=time.time()
  
          
            entries=self.controller.register_read("my_register")
            print("my_register:",entries)
            W2=entries[15]/1000000#单位s
            lambd = lambda1+lambda2+lambda3
            N=64#队列总容量
            n=2#链路数量2+1
            #C=28136#单位pps,取的中位数
            C=10*1000000/(100*8)#单位pps,取的中位数
            mu = 1000

            #if(lambda1==0 and lambda2==0 and lambda3==0): #全部为0，说明未开始发包       
            #    time.sleep(2)
            #当到达率不为0时，第一次运算得到mu1\2\3=====================================================
            if (lambda1!=0 or lambda2!=0 or lambda3!=0):
                print("lambda1:%s,lambda2:%s,lambda3:%s,W2:%s" %(lambda1,lambda2,lambda3,W2))
                [mu1, mu2, mu3] = main2.get_mu(N,lambda1,lambda2,lambda3,n,C,W2,mu);
                print("==================mu1:%s,mu2:%s,mu3:%s====================" % (mu1,mu2,mu3))
                with open('h2.txt', 'a') as f:#mu写入文件
                    str1="mu1:"+str(mu1)+",mu2:"+str(mu2)+",mu3:"+str(mu3)+"\n"
                    f.write(str1)
                
                if(mu1==0 and mu2==0 and mu3==0):#无解时,omega和K默认为22
                    omega1=300
                    omega2=300
                    omega3=300
                    k1=21
                    k2=21
                    k3=21               
                if(mu1 !=0 or mu2!=0 or mu3!=0):#有解时
                    omega1=mu*mu1/(mu1+mu2+mu3)
                    omega2=mu*mu2/(mu1+mu2+mu3)
                    omega3=mu*mu3/(mu1+mu2+mu3)              
                    print("omega1:%s,omega2:%s,omega3:%s" % (omega1,omega2,omega3))

                    #k1=omega1
                    #k2=omega2
                    #k3=omega3                
                    k1=N*mu1/(mu1+mu2+mu3)
                    k2=N*mu2/(mu1+mu2+mu3)
                    k3=N*mu3/(mu1+mu2+mu3)  
                    #k1=lambda1/(mu1-lambda1)-(N+1)*pow(lambda1,N+1)/(pow(mu1,N+1)-pow(lambda1,N+1))
                    #k2=lambda2/(mu2-lambda2)-(N+1)*pow(lambda2,N+1)/(pow(mu2,N+1)-pow(lambda2,N+1))
                    #k3=lambda3/(mu3-lambda3)-(N+1)*pow(lambda3,N+1)/(pow(mu3,N+1)-pow(lambda3,N+1))
                with open('h2.txt', 'a') as f:#omega,k写入文件
                    str1="omega1:"+str(omega1)+",omega2:"+str(omega2)+",omega3:"+str(omega3)+"\n"
                    str2="k1:"+str(k1)+",k2:"+str(k2)+",k3:"+str(k3)+"\n"
                    f.write(str1)
                    f.write(str2)
                k1=math.ceil(k1)
                k2=math.ceil(k2)
                k3=math.ceil(k3)
                print("=====================k1:%s,k2:%s,k3:%s===================" %(k1,k2,k3))
                #omega写入寄存器
                self.controller.register_write("my_register", int(10), omega1)
                self.controller.register_write("my_register", int(17), omega2)
                self.controller.register_write("my_register", int(24), omega3)                          
                #K写入寄存器
                self.controller.register_write("my_register", int(11), k1)
                self.controller.register_write("my_register", int(18), k2)
                self.controller.register_write("my_register", int(25), k3)

                #第二次计算lambda11\12\13================================================================================================
                if(mu1 !=0 or mu2!=0 or mu3!=0):#有解时
                    [lambda11, lambda22, lambda33] = main2.get_lambd(N,mu1,mu2,mu3,n,C,W2,mu);#根据目前的出队率求取最好的lambda
                    print("lambda11:%s,lambda22:%s,lambda33:%s" %(lambda11,lambda22,lambda33))
                    with open('h2.txt', 'a') as f:#lambda写入文件
                        str1="lambda11:"+str(lambda11)+",lambda22:"+str(lambda22)+",lambda33:"+str(lambda33)+"\n"
                        f.write(str1)
                    
                    #lambda11写入寄存器                                            
                    entries=self.controller.register_read("lambda_register")
                    t3=time.time()
                    t=t3-t2
                    lambda1=(entries[1]-lambda1)/t
                    lambda2=(entries[2]-lambda2)/t
                    lambda3=(entries[3]-lambda3)/t
                    self.controller.register_write("my_register", int(12), lambda1)
                    self.controller.register_write("my_register", int(19), lambda2)
                    self.controller.register_write("my_register", int(26), lambda3)
                    self.controller.register_write("my_register", int(13), lambda11)
                    self.controller.register_write("my_register", int(20), lambda22)
                    self.controller.register_write("my_register", int(27), lambda33) 
            self.controller.register_reset("lambda_register")#重置lambda_register=0            
            t1=time.time()
            time.sleep(2)                              
            #end_all_lambda!=0
        #结束一次循环





def main():
    port=int(9091)#监听端口
    controller(port).read_and_write()
    

if __name__ == '__main__':
    main()
