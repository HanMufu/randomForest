import pandas as pd

'''
f=pd.read_csv('hs300close.csv')
f=f[f.date<"2006-04-01"]
fclose=f.close
fopen=f.open
df1=pd.DataFrame({'price':fopen})
df2=pd.DataFrame({'price':fclose})
df3=pd.concat([df1,df2],axis=0)
fclose.append(fopen,ignore_index=True)
#fadd=fclose+fopen
print(df3.median())
'''

def mid(file):
	f=pd.read_csv(file)
	q=[]
	mid=[]
	fileOrignal=0
	for year in range(2006,2018):
		for quarter in range(1,5):
			if quarter==1:
				fileOrignal=f[f.date<str(year)+str('-04-01')]
				fileOrignal=fileOrignal[fileOrignal.date>=str(year)+str('-01-01')]
				print(fileOrignal)
			elif quarter==2:
				fileOrignal=f[f.date<str(year)+str('-07-01')]
				fileOrignal=fileOrignal[fileOrignal.date>=str(year)+str('-04-01')]
			elif quarter==3:
				fileOrignal=f[f.date<str(year)+str('-10-01')]
				fileOrignal=fileOrignal[fileOrignal.date>=str(year)+str('-07-01')]
			elif quarter==4:
				fileOrignal=f[f.date<=str(year)+str('-12-30')]
				fileOrignal=fileOrignal[fileOrignal.date>=str(year)+str('-10-01')]
			fileClose=fileOrignal.close
			fileOpen=fileOrignal.open
			dfOpen=pd.DataFrame({'price':fileOpen})
			dfClose=pd.DataFrame({'price':fileClose})
			dfInAll=pd.concat([dfOpen,dfClose],axis=0)
			q.append(str(year)+'-q'+str(quarter))
			mid.append(float(dfInAll.median()))
	#print(q)
	#print(mid)
	dfFinish=pd.DataFrame({'date':q,'price':mid})
	print(dfFinish)
	dfFinish.to_csv("MissonAcomplished.csv")

mid('hs300close.csv')
