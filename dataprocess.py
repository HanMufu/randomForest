# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 11:09:13 2018

@author: YAO
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

'''
import main
main.mmmm()
'''

#中位数去极值
def step_a(data):
    adata=data
    nrow=data.shape[0]#行
    ncol=data.shape[1]#列
    dmedian=[]
    dmedian1=[]

    a=[]
    b=[]
    
    #求中位数
    for j in range(ncol):#求中位数
        for i in range(nrow):
            if(pd.isnull(adata[i][j])==False):
                a.append(adata[i][j])
        a=sorted(a) #每列的非空数排序
        dmedian.append(a[(len(a))//2])#中间的就是中位数
        a=[]
        
    #Di-Dm的中位数 其余同上
    for j in range(ncol):
        for i in range(nrow):
            if(pd.isnull(data[i][j])==False):
                b.append(abs(adata[i][j]-dmedian[j]))
        b=sorted(b)
        dmedian1.append(b[(len(b))//2])
        b=[]

    #找出 大于Dm+5Di 和 小于Dm-5Di
    for j in range(ncol):
        for i in range(nrow):
            dmax=dmedian[j]+5*dmedian1[j]
            dmin=dmedian[j]-5*dmedian1[j]
            if(adata[i][j]>dmax and pd.isnull(data[i][j])==False):
                adata[i][j]=dmax
            elif(data[i][j]<dmin and pd.isnull(data[i][j])==False):
                adata[i][j]=dmin
    
    return adata



#缺失值处理
def step_b(data,codedata,incode):#data codedata incodedata
    bdata=data
   
    nrow=data.shape[0]#行
    ncol=data.shape[1]#列
    #filleddata=[]
    #iHY001code现在没什么用
    iHY001=[]
    iHY001code=[]
    iHY002=[]
    iHY002code=[]
    iHY003=[]
    iHY003code=[]
    iHY004=[]
    iHY004code=[]
    iHY005=[]
    iHY005code=[]
    iHY006=[]
    iHY006code=[]   
    iHY007=[]
    iHY007code=[]   
    iHY008=[]
    iHY008code=[] 
    iHY009=[]
    iHY009code=[] 
    iHY010=[]
    iHY010code=[] 
    iHY011=[]
    iHY011code=[] 
    i0=[]
    i0code=[] 
    for i in range(nrow):  
        #按照行业分别装进去，用来求平均值
        if(incode[i]=="HY001"):
            iHY001.append(bdata[i])
            iHY001code.append(codedata[i])
            
        elif(incode[i]=="HY002"):
            iHY002.append(bdata[i])
            iHY002code.append(codedata[i])  
        elif(incode[i]=="HY003"):
            iHY003.append(bdata[i])
            iHY003code.append(codedata[i])     
        elif(incode[i]=="HY004"):
            iHY004.append(bdata[i])
            iHY004code.append(codedata[i])   
        elif(incode[i]=="HY005"):
            iHY005.append(bdata[i])
            iHY005code.append(codedata[i])   
        elif(incode[i]=="HY006"):
            iHY006.append(bdata[i])
            iHY006code.append(codedata[i])       
        elif(incode[i]=="HY007"):
            iHY007.append(bdata[i])
            iHY007code.append(codedata[i])     
            
        elif(incode[i]=="HY008"):
            iHY008.append(bdata[i])
            iHY008code.append(codedata[i])
            
        elif(incode[i]=="HY009"):
            iHY009.append(bdata[i])
            iHY009code.append(codedata[i])       
            
        elif(incode[i]=="HY010"):
            iHY010.append(bdata[i])
            iHY010code.append(codedata[i])    
            
        elif(incode[i]=="HY011"):
            iHY011.append(bdata[i])
            iHY011code.append(codedata[i])   
        
        elif(incode[i]=="0"):

            i0.append(bdata[i])
            i0code.append(codedata[i]) 
        #这里11个行业 elif
        
    #irow=len(iHY001)#行
    #i1col=len(iHY001[0])#列 
    
    #用nanmean求11个行业的平均值
    meaniHY001=np.nanmean(iHY001, axis=0)
    meaniHY002=np.nanmean(iHY002, axis=0)
    meaniHY003=np.nanmean(iHY003, axis=0)
    meaniHY004=np.nanmean(iHY004, axis=0)
    meaniHY005=np.nanmean(iHY005, axis=0)
    meaniHY006=np.nanmean(iHY006, axis=0)
    meaniHY007=np.nanmean(iHY007, axis=0)
    meaniHY008=np.nanmean(iHY008, axis=0)
    meaniHY009=np.nanmean(iHY009, axis=0)
    meaniHY010=np.nanmean(iHY010, axis=0)
    meaniHY011=np.nanmean(iHY011, axis=0)
    meani0=np.nanmean(i0, axis=0)

    #遍历 找出nan 用平均值填补
    for i in range(nrow):
        for j in range(ncol):
            if(pd.isnull(bdata[i][j])==True and incode[i]=="HY001"):
                bdata[i][j]=meaniHY001[j]
                #filleddata.append([i,j])#记录被修改过的
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY002"):
                bdata[i][j]=meaniHY002[j]  
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY003"):
                bdata[i][j]=meaniHY003[j]  
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY004"):
                bdata[i][j]=meaniHY004[j]  
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY005"):
                bdata[i][j]=meaniHY005[j]  
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY006"):
                bdata[i][j]=meaniHY006[j]  
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY007"):
                bdata[i][j]=meaniHY007[j]   
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY008"):
                bdata[i][j]=meaniHY008[j]   
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY009"):
                bdata[i][j]=meaniHY009[j]   
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY010"):
                bdata[i][j]=meaniHY010[j]   
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="HY011"):
                bdata[i][j]=meaniHY011[j]   
            elif(pd.isnull(bdata[i][j])==True and incode[i]=="0"):
                bdata[i][j]=meani0[j]        
    return bdata 
    

def step_c(data,bdata,dummy,market):
    cdata=data
    nrow=cdata.shape[0]#行
    ncol=cdata.shape[1]#列
    for j in range(ncol):#最后一列是市值
        x=[]
        y=[]
        testx=[]
        resulty=[]
        index=[]
        for i in range(nrow):
            if(pd.isnull(cdata[i][j])==False):
                
                a=data[i][j]
                
                b=list(dummy[i])
                b.append(market[i])#市值
                
                x.append(b)
                y.append(a)
                
            else:
                c=list(dummy[i])
                
                c.append(market[i])
                
                testx.append(c)
                
                index.append(i)#记录哪一行
                
        if(len(index)!=0): #如果这一列有nan 线性回归一下
            linreg=LinearRegression()
            linreg.fit(x,y)
            resulty = linreg.predict(testx)
            for k in range((len(index))):
                cdata[index[k]][j]=resulty[k]-bdata[index[k]][j]
    return cdata


#标准化
def step_d(data):
    ddata=data
    ddata = ddata-np.mean(ddata, axis = 0) #减去均值
    ddata=ddata/ np.std(ddata, axis = 0)#除以标准差
    
    return ddata
    




    
#datadf=pd.read_csv('2006q2TEST.csv')#数据
datadf=pd.read_csv('tagedALLDATA(2).csv')#数据
print(datadf)
codedata=np.array(datadf['code'])#取出代码

incodedata=np.array(datadf['HY'])#取出行业

marketdata=np.array(datadf['market_cap'])#取出标签
statedata=np.array(datadf['statDate'])#取出日期

labeldata=np.array(datadf['label'])#取出标签

dummy = pd.get_dummies(incodedata)#行业转化为哑变量
dummy = np.array(dummy)
print(dummy)



#删了不要的
droplist = ['num','code','HY','label','statDate','gain_ratio']
#droplist = ['code','HY']

datadrop=datadf.drop(droplist,axis=1)

#转化为nparray
rdata = np.array(datadrop)
print(rdata)
#a步
adataed=step_a(rdata)
adataed = np.array(adataed)


#b步
bdataed=step_b(adataed,codedata,incodedata)
bdataed = np.array(bdataed)


#c步
cdataed=step_c(adataed,bdataed,dummy,marketdata)
cdataed = np.array(cdataed)

#d步
ddataed=step_d(cdataed)
ddataed = np.array(ddataed)



#print(ddataed)#除代码 行业 标签外的处理完的数据
alldata=[]
for i in range(len(ddataed)):

    a=list(ddataed[i])
    a.append(codedata[i])
    #a.append(incodedata[i])
    a.append(labeldata[i])
    a.append(statedata[i])

    alldata.append(a)

    #ddataed[i].append(incodedata[i])
    #print(alldata[i])


    
alldata= np.array(alldata)
np.savetxt('data1.csv' ,alldata, delimiter=',' ,fmt = '%s')  
 

    
#print(alldata)

        