import pandas as pd
import numpy as np
from collections import deque
import time
'''
目前实现了最基础的按照概率阈值按照回溯算法进行对故障树的深度优先搜索 在遇到概率低于阈值时回溯
接下来需要进行剪枝操作
'''

class Possibility_Backtrack():
    def __init__(self,data):
        self.data=data
        self.path=deque()
        self.idx=deque()
        self.result=[]
        self.p_min=0.0001
        self.outage_possibility_dic={}
        self.outage_list=list(self.data['original_idx'])
        self.possibility_list=list(self.data['outage_probability'])
        self.operating_possibility_list=1-np.array(self.possibility_list)
        self.num=len(self.data)
        for i in range(len(self.data)):
            temp=self.data.loc[i]
            idx=int(temp['idx'])
            outage_possibility=temp['outage_probability']
            self.outage_possibility_dic[idx]=outage_possibility


    def backtrack(self,startindex):
        #possibility_temp_list=[self.possibility_list[i] for i in self.idx]
        possibility_temp_list=self.operating_possibility_list.copy()
        for i in self.idx:
            possibility_temp_list[i]=self.possibility_list[i]
        possibility=np.prod(possibility_temp_list)
        if possibility>self.p_min:
            self.result.append(self.idx.copy())#搜索路径上大于阈值的解都应该加入到结果
        if possibility<self.p_min:
            #self.result.append(list(self.idx)[:-1].copy())
            #self.result.append(self.idx.copy())
            return#达到认为要回溯的节点
        for i in range(startindex,self.num):
            self.idx.append(i)
            self.backtrack(startindex=i+1)
            self.idx.pop()#撤销之前的路径





if __name__=='__main__':
    start=time.time()
    #data=pd.read_excel('component_outage_test.xlsx',sheet_name=1)
    data = pd.read_excel('component_outage_test.xlsx', sheet_name=4)
    obj=Possibility_Backtrack(data=data)
    obj.backtrack(startindex=0)
    end=time.time()
    print('运算时间',end-start)
    # result_list=[]
    # for i in obj.result:
    #     if i not in result_list:
    #         result_list.append(i)