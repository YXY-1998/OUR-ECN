import geatpy as ea                
from GA.doublesoeaobjnon.MyProblem1 import MyProblem1     
from GA.doublesoeaobjnon.MyProblem2 import MyProblem2     
import numpy as np

def get_mu(N,lambd1,lambd2,lambd3,n,C,W2,mu):


    problem1 = MyProblem1(N,lambd1,lambd2,lambd3,n,C,W2,mu)             

    Encoding = 'RI'                     
    NIND = 100                         
    Field = ea.crtfld(Encoding, problem1.varTypes, problem1.ranges, problem1.borders)    
    population = ea.Population(Encoding, Field, NIND)   

    myAlgorithm1 = ea.soea_DE_best_1_L_templet(problem1, population) 
    myAlgorithm1.MAXGEN = 200          
    myAlgorithm1.mutOper.F = 0.5                                         
    myAlgorithm1.recOper.XOVR = 0.4                                     
    myAlgorithm1.drawing = 0            


    [NDSet, population] = myAlgorithm1.run()
    NDSet.save()                        
    
    if NDSet.sizes != 0:
        result = [0 for i in range(NDSet.Phen.shape[1])]
        for i in range(NDSet.Phen.shape[1]):          
            result[i] = NDSet.Phen[0, i]
            print(result[i])

    else:
        result = [0,0,0]               
    return(result)

def get_lambd(N,mu1,mu2,mu3,n,C,W2,mu):
    problem2 = MyProblem2(N,mu1,mu2,mu3,n,C,W2,mu)              
    Encoding = 'RI'                   
    NIND = 100                        
    Field = ea.crtfld(Encoding, problem2.varTypes, problem2.ranges, problem2.borders)    
    population = ea.Population(Encoding, Field, NIND)   

    myAlgorithm2 = ea.soea_DE_best_1_L_templet(problem2, population) 
    myAlgorithm2.MAXGEN = 200            
    myAlgorithm2.mutOper.F = 0.5                                        
    myAlgorithm2.recOper.XOVR = 0.4                                     
    myAlgorithm2.drawing = 0            

    [lambdSet, population] = myAlgorithm2.run()
    lambdSet.save()                       

    if lambdSet.sizes != 0:
        result = [0 for i in range(lambdSet.Phen.shape[1])]
        for i in range(lambdSet.Phen.shape[1]):           
            result[i] = lambdSet.Phen[0, i]
            print(result[i])

    else:
        result = [0,0,0]  
    return(result)
