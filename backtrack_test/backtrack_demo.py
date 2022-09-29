import pandas as pd
import numpy as np
from collections import deque
import time
'''
尝试使用回溯算法实现组合
先实现连续数字组合
'''

class My_Combinations():
    def __init__(self,max_num,k):
        self.max_num=max_num
        self.k=k
        self.path=deque()
        self.result=[]

    def backtrack(self,current_index):
        if len(self.path)==self.k:
            self.result.append(self.path.copy())
            return

        for i in range(current_index,self.max_num+1):
            self.path.append(i)
            #print(i)
            #print(self.path)
            self.backtrack(current_index=i+1)
            #print(self.path)
            self.path.pop()
            #print(self.path)
            #print(i)
            #print(current_index)

if __name__=='__main__':
    start=time.time()
    obj=My_Combinations(max_num=5,k=3)
    obj.backtrack(current_index=1)
    end=time.time()
    print('运算时间',end-start)
    print(obj.result)



