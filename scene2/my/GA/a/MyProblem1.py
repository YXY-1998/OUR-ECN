import numpy as np
import geatpy as ea
from decimal import * 

class MyProblem1(ea.Problem):               
    def __init__(self,N,lambd1,lambd2,lambd3,n,C,W2,mu):
        self.N=N
        self.lambd1=lambd1
        self.lambd2=lambd2
        self.lambd3=lambd3
        self.n=n
        self.C=C
        self.W2=W2
        self.mu=mu
        name = 'MyProblem1'                 
        M = 1                            
        maxormins = [1]                  
        Dim = 3                           
        varTypes = [0] * Dim               

        
        lb = [0]* Dim                        
        ub = [self.N]* Dim                       
        lbin = [0]* Dim                      
        ubin = [0]* Dim 
        
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):                
        Vars = pop.Phen                     
        mu1 = Vars[:, [0]]               
        mu2 = Vars[:, [1]]                 
        mu3 = Vars[:, [2]]                  
                 
        getcontext().prec = 256

        lambd1 = float(Decimal(self.lambd1))
        #print(lambd1)
        lambd2 = float(Decimal(self.lambd1))
        lambd3 = float(Decimal(self.lambd1))

        N=float(Decimal(self.N))

        n=float(Decimal(self.n))
        C=float(Decimal(self.C))
        W2=float(Decimal(self.W2))
        mu=float(Decimal(self.mu))
        

        f11=(n+1)*C-sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                     lambd2/(mu2-lambd2)-(N*pow(lambd2,N+1)+lambd1*pow(mu2,N))/(pow(mu2,N+1)-pow(lambd2,N+1)),
                     lambd3/(mu3-lambd3)-(N*pow(lambd3,N+1)+lambd1*pow(mu3,N))/(pow(mu3,N+1)-pow(lambd3,N+1))])

        f12=1/(mu1-lambd1)-N*pow(lambd1,N)/mu1*(pow(mu1,N)-pow(lambd1,N))

        f21=1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))

        f22=abs(W2-(1/(mu2-lambd2)-N*pow(lambd2,N)/mu2*(pow(mu2,N)-pow(lambd2,N))))

        f31=1/(mu3-lambd3)-N*pow(lambd3,N)/mu3*(pow(mu3,N)-pow(lambd3,N))

        f32=pow(lambd3,N+1)*(mu3-lambd3)/(pow(mu3,N+1)-pow(lambd3,N+1))

        f4=sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                     lambd2/(mu2-lambd2)-(N*pow(lambd2,N+1)+lambd1*pow(mu2,N))/(pow(mu2,N+1)-pow(lambd2,N+1)),
                     lambd3/(mu3-lambd3)-(N*pow(lambd3,N+1)+lambd1*pow(mu3,N))/(pow(mu3,N+1)-pow(lambd3,N+1))])/(n+1)*C
        


        cv2=sum([lambd1/(mu1-lambd1)-(N+1)*pow(lambd1,N+1)/(pow(mu1,N+1)-pow(lambd1,N+1)),
                 lambd2/(mu1-lambd2)-(N+1)*pow(lambd2,N+1)/(pow(mu2,N+1)-pow(lambd2,N+1)),
                 lambd3/(mu1-lambd3)-(N+1)*pow(lambd3,N+1)/(pow(mu3,N+1)-pow(lambd3,N+1))])-N

        
        cv31=lambd1-mu1
        cv32=lambd2-mu2
        cv33=lambd3-mu3

        cv4=sum([mu1,mu2,mu3])-mu
        #cv4=np.abs(sum([mu1,mu2,mu3])-mu)

        cv5=sum([lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                 lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1)),
                 lambd1/(mu1-lambd1)-(N*pow(lambd1,N+1)+lambd1*pow(mu1,N))/(pow(mu1,N+1)-pow(lambd1,N+1))])-(n+1)*C  
        '''

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
