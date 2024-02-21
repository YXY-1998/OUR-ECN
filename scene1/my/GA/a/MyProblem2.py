import numpy as np
import geatpy as ea
from decimal import * #精于计算
#from decimal import getcontext #保留的小数位数，自己设置

class MyProblem2(ea.Problem):                # 继承Problem父类
    def __init__(self, N,mu1,mu2,mu3,n,C,W2,mu):
        self.N=N
        self.mu1=mu1
        self.mu2=mu2
        self.mu3=mu3
        self.n=n
        self.C=C
        self.W2=W2
        self.mu=mu
        name = 'MyProblem2'                  # 初始化name（函数名称，可以随意设置）
        M = 1                             # 初始化M（目标维数）
        maxormins = [1]                    # 初始化目标最小最大化标记列表，1：min；-1：max
        Dim = 3                           # 初始化Dim（决策变量维数）
        varTypes = [0] * Dim                # 初始化决策变量类型，0：连续；1：离散
        '''
        lb = [0,0]                        # 决策变量下界
        ub = [10,10]                        # 决策变量上界
        lbin = [1,1]                      # 决策变量下边界
        ubin = [1,1]                      # 决策变量上边界 # 调用父类构造方法完成实例化
        '''
        #'''
        lb = [0]* Dim                         # 决策变量下界
        ub = [self.N]* Dim                         # 决策变量上界
        lbin = [0]* Dim                       # 决策变量下边界
        ubin = [0]* Dim 
        #'''
        #N=1000
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):                 # 目标函数，pop为传入的种群对象
        Vars = pop.Phen                     # 得到决策变量矩阵
        lambd1 = Vars[:, [0]]                 # 取出第一列得到所有个体的x1组成的列向量
        lambd2 = Vars[:, [1]] 
        lambd3 = Vars[:, [2]]
        #lambd = Vars[:, [1]]                   # 取出第二列得到所有个体的x2组成的列向量
        #x3 = Vars[:, [2]]                   # 取出第三列得到所有个体的x3组成的列向量
        # 计算目标函数值，赋值给pop种群对象的ObjV属性#假设到达率为10
        #print(mu)
        #print(lambd)
        getcontext().prec = 64

        mu1 = float(Decimal(self.mu1))
        mu2 = float(Decimal(self.mu2))
        mu3 = float(Decimal(self.mu3))

        N=float(Decimal(self.N))
        n=float(Decimal(self.n))
        C=float(Decimal(self.C))
        W2=float(Decimal(self.W2))
        mu=float(Decimal(self.mu))
        #N=10

        #目标函数
        f11=(n+1)*C-sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                     lambd2/(mu2-lambd2)-(N*pow(lambd2,N+1)+lambd1*pow(mu2,N))/(pow(mu2,N+1)-pow(lambd2,N+1)),
                     lambd3/(mu3-lambd3)-(N*pow(lambd3,N+1)+lambd1*pow(mu3,N))/(pow(mu3,N+1)-pow(lambd3,N+1))])
        f12=1/(mu1-lambd1)-N*pow(lambd1,N)/mu1*(pow(mu1,N)-pow(lambd1,N))

        f21=1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))
        f22=abs(W2-(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))))

        f31=1/(mu3-lambd3)-N*pow(lambd3,N)/mu3*(pow(mu3,N)-pow(lambd3,N))
        f32=pow(lambd3,N+1)*(mu3-lambd3)/(pow(mu3,N+1)-pow(lambd3,N+1))

        #带宽利用率
        f4=sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                     lambd2/(mu2-lambd2)-(N*pow(lambd2,N+1)+lambd1*pow(mu2,N))/(pow(mu2,N+1)-pow(lambd2,N+1)),
                     lambd3/(mu3-lambd3)-(N*pow(lambd3,N+1)+lambd1*pow(mu3,N))/(pow(mu3,N+1)-pow(lambd3,N+1))])/(n+1)*C

        # 采用可行性法则处理约束，生成种群个体违反约束程度矩阵
        #pop.CV = np.hstack([2*x1 + x2 - 1, x1 + 2*x3 - 2, np.abs(x1 + x2 + x3 - 1)])   # 第1.2.3个约束
        cv2=sum([lambd1/(mu1-lambd1)-(N+1)*pow(lambd1,N+1)/(pow(mu1,N+1)-pow(lambd1,N+1)),
                 lambd2/(mu1-lambd2)-(N+1)*pow(lambd2,N+1)/(pow(mu2,N+1)-pow(lambd2,N+1)),
                 lambd3/(mu1-lambd3)-(N+1)*pow(lambd3,N+1)/(pow(mu3,N+1)-pow(lambd3,N+1))])-N

        
        cv31=lambd1-mu1
        cv32=lambd2-mu2
        cv33=lambd3-mu3

        cv4=sum([lambd1,lambd2,lambd3])-mu
        #cv4=np.abs(sum([mu1,mu2,mu3])-mu)

        cv5=sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                 lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                 lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1))])-(n+1)*C
        '''
        #目标函数>0
        cv61=N*pow(lambd1,N)/mu1*(pow(mu1,N)-pow(lambd1,N))-1/(mu1-lambd1)
        cv62=N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))-1/(mu2-lambd1)
        cv63=N*pow(lambd3,N)/mu3*(pow(mu3,N)-pow(lambd3,N))-1/(mu3-lambd1)
        #cv64=-abs(W2-(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))))
        cv64=-pow(lambd3,N+1)*(mu3-lambd3)/(pow(mu3,N+1)-pow(lambd3,N+1))
        '''
        #pop.CV = np.hstack([cv2, cv31, cv32, cv33, cv4, cv5])
        #pop.ObjV = np.hstack([f11,f12,f21,f22,f31,f32])
        pop.CV = np.hstack([cv2, cv31, cv32, cv33, cv4, cv5])
        '''
        pop.ObjV = mu1/mu*(n*C-sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                                    lambd2/(mu2-lambd2)-(N*pow(lambd2,N+1)+lambd1*pow(mu2,N))/(pow(mu2,N+1)-pow(lambd2,N+1)),
                                    lambd3/(mu3-lambd3)-(N*pow(lambd3,N+1)+lambd1*pow(mu3,N))/(pow(mu3,N+1)-pow(lambd3,N+1))])+1/(mu1-lambd1)-N*pow(lambd1,N)/mu1*(pow(mu1,N)-pow(lambd1,N)))+mu2/mu*(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))+abs(W2-(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N)))))+mu3/mu*(1/(mu3-lambd3)-N*pow(lambd3,N)/mu3*(pow(mu3,N)-pow(lambd3,N))+pow(lambd3,N+1)*(mu3-lambd3)/(pow(mu3,N+1)-pow(lambd3,N+1)))
        '''
        pop.ObjV = mu1/(mu1+mu2+mu3)*((n+1)*C-sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),lambd2/(mu2-lambd2)-(N*pow(lambd2,N+1)+lambd1*pow(mu2,N))/(pow(mu2,N+1)-pow(lambd2,N+1)),lambd3/(mu3-lambd3)-(N*pow(lambd3,N+1)+lambd1*pow(mu3,N))/(pow(mu3,N+1)-pow(lambd3,N+1))])+1/(mu1-lambd1)-N*pow(lambd1,N)/mu1*(pow(mu1,N)-pow(lambd1,N)))+mu2/(mu1+mu2+mu3)*(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))+abs(W2-(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N)))))+mu3/(mu1+mu2+mu3)*(1/(mu3-lambd3)-N*pow(lambd3,N)/mu3*(pow(mu3,N)-pow(lambd3,N))+pow(lambd3,N+1)*(mu3-lambd3)/(pow(mu3,N+1)-pow(lambd3,N+1)))-f4
