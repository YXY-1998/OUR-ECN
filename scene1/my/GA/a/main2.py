'''
存在无解情况
'''
import geatpy as ea                 # import geatpy
from GA.doublesoeaobjnon.MyProblem1 import MyProblem1     # 导入自定义问题接口
from GA.doublesoeaobjnon.MyProblem2 import MyProblem2     # 导入自定义问题接口
import numpy as np

def get_mu(N,lambd1,lambd2,lambd3,n,C,W2,mu):

    """=========================实例化问题对象==========================="""
    problem1 = MyProblem1(N,lambd1,lambd2,lambd3,n,C,W2,mu)               # 实例化问题对象
    """===========================种群设置=============================="""
    Encoding = 'RI'                     # 编码方式
    NIND = 100                          # 种群规模
    Field = ea.crtfld(Encoding, problem1.varTypes, problem1.ranges, problem1.borders)     # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)   # 实例化种群对象（此时种群还没被真正初始化，仅仅是生成一个种群对象）

    """=========================算法参数设置============================"""
    #myAlgorithm1 = ea.moea_NSGA3_templet(problem1, population)    # 实例化一个算法模板对象
    myAlgorithm1 = ea.soea_DE_best_1_L_templet(problem1, population) #单目标优化模板
    myAlgorithm1.MAXGEN = 200           # 最大遗传代数
    myAlgorithm1.mutOper.F = 0.5                                         # 设置差分进化的变异缩放因子
    myAlgorithm1.recOper.XOVR = 0.4                                      # 设置交叉概率
    #myAlgorithm1.mutOper.F = 1                                         # 设置差分进化的变异缩放因子
    #myAlgorithm1.recOper.XOVR = 0.6                                      # 设置交叉概率
    myAlgorithm1.drawing = 0             # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；3：绘制决策空间过程动画）

    """===================调用算法模板进行种群进化=======================
    调用run执行算法模板，得到帕累托最优解集NDSet。
    NDSet是一个种群类Population的对象。
    NDSet.ObjV为最优解个体的目标函数值；NDSet.Phen为对应的决策变量值。
    详见Population.py中关于种群类的定义。
    """

    [NDSet, population] = myAlgorithm1.run()## 执行算法模板，得到非支配种群, 返回帕累托最优个体以及最后一代种群 return [NDSet, pop]
    NDSet.save()                        # 把结果保存到文件中 # 输出
    
    if NDSet.sizes != 0:
        print('最优的目标函数值为：%s' % NDSet.ObjV[0][0])
        print('最优的控制变量值为：')
        result = [0 for i in range(NDSet.Phen.shape[1])]
        for i in range(NDSet.Phen.shape[1]):#shape:数组形状n维m列(n,m) shape[0]:行数=n shape[1]:列数=m 
            #print(NDSet.Phen[0, i])            
            result[i] = NDSet.Phen[0, i]
            print(result[i])

    else:
        print('此次未找到可行解。')
        result = [0,0,0]               
        #return
    print('评价次数：%s'%(myAlgorithm1.evalsNum))
    print('时间已过 %s 秒'%(myAlgorithm1.passTime))

    #return(NDSet.ObjV[0][0],NDSet.ObjV[0][1],NDSet.ObjV[0][0])#
    return(result)

def get_lambd(N,mu1,mu2,mu3,n,C,W2,mu):
    
    """=========================实例化问题对象==========================="""
    problem2 = MyProblem2(N,mu1,mu2,mu3,n,C,W2,mu)               # 实例化问题对象
    """===========================种群设置=============================="""
    Encoding = 'RI'                     # 编码方式
    NIND = 100                          # 种群规模
    Field = ea.crtfld(Encoding, problem2.varTypes, problem2.ranges, problem2.borders)     # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)   # 实例化种群对象（此时种群还没被真正初始化，仅仅是生成一个种群对象）

    """=========================算法参数设置============================"""
    #myAlgorithm2 = ea.moea_NSGA3_templet(problem2, population)     # 实例化一个算法模板对象
    myAlgorithm2 = ea.soea_DE_best_1_L_templet(problem2, population) #单目标优化模板
    myAlgorithm2.MAXGEN = 200            # 最大遗传代数
    myAlgorithm2.mutOper.F = 0.5                                        # 设置差分进化的变异缩放因子
    myAlgorithm2.recOper.XOVR = 0.5                                      # 设置交叉概率
    myAlgorithm2.drawing = 0             # 设置绘图方式

    """===================调用算法模板进行种群进化=======================
    调用run执行算法模板，得到帕累托最优解集lambdSet。
    lambdSet是一个种群类Population的对象。
    lambdSet.ObjV为最优解个体的目标函数值；lambdSet.Phen为对应的决策变量值。
    详见Population.py中关于种群类的定义。
    """
    [lambdSet, population] = myAlgorithm2.run()## 执行算法模板，得到非支配种群, 返回帕累托最优个体以及最后一代种群 return [lambdSet, pop]
    lambdSet.save()                        # 把结果保存到文件中 # 输出
    #选取一个最优解
    if lambdSet.sizes != 0:
        print('最优的目标函数值为：%s' % lambdSet.ObjV[0][0])
        print('最优的控制变量值为：')
        result = [0 for i in range(lambdSet.Phen.shape[1])]
        for i in range(lambdSet.Phen.shape[1]):#shape:数组形状n维m列(n,m) shape[0]:行数=n shape[1]:列数=m 
            #print(lambdSet.Phen[0, i])            
            result[i] = lambdSet.Phen[0, i]
            print(result[i])

    else:
        print('此次未找到可行解。')
        result = [0,0,0]  
    print('评价次数：%s'%(myAlgorithm2.evalsNum))
    print('时间已过 %s 秒'%(myAlgorithm2.passTime))
    return(result)

'''
def main():
    N=10
    lambd1=3
    lambd2=2
    lambd3=1
    lambd=lambd1+lambd2+lambd3
    n=3
    C=10
    W2=5
    mu=10
    #get_mu(N,lambd1,lambd2,lambd3,n,C,W2,mu);
    
    [mu1, mu2, mu3] = get_mu(N,lambd1,lambd2,lambd3,n,C,W2,mu);
    print(mu1)
    print(mu2)
    print(mu3)

    k1=lambd1/(mu1-lambd1)-(N+1)*pow(lambd1,N+1)/(pow(mu1,N+1)-pow(lambd1,N+1))
    k2=lambd2/(mu2-lambd2)-(N+1)*pow(lambd2,N+1)/(pow(mu2,N+1)-pow(lambd2,N+1))
    k3=lambd3/(mu3-lambd3)-(N+1)*pow(lambd3,N+1)/(pow(mu3,N+1)-pow(lambd3,N+1))
    print("------------------------------K-------------------------------------")
    print(k1)
    print(k2)
    print(k3)

    #get_lambd(N,mu1,mu2,mu3,n,C,W2,mu);
    
    
    [lambd1, lambd2, lambd3] = get_lambd(N,mu1,mu2,mu3,n,C,W2,mu);
    print(lambd1)
    print(lambd2)
    print(lambd3)

    k1=lambd1/(mu1-lambd1)-(N+1)*pow(lambd1,N+1)/(pow(mu1,N+1)-pow(lambd1,N+1))
    k2=lambd2/(mu2-lambd2)-(N+1)*pow(lambd2,N+1)/(pow(mu2,N+1)-pow(lambd2,N+1))
    k3=lambd3/(mu3-lambd3)-(N+1)*pow(lambd3,N+1)/(pow(mu3,N+1)-pow(lambd3,N+1))
    print("------------------------------K-------------------------------------")
    print(k1)
    print(k2)
    print(k3)
   
if __name__ == "__main__":
    main()
'''
