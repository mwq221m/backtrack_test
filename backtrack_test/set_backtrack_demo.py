import pandas as pd
import numpy as np
from collections import deque
import time

class MySubSet():
    def __init__(self,set_num):
        #self.set=set
        self.set_num=set_num
        self.result=[]
        self.layer=0#对于会在函数间彼此影响的全局变量使用要慎重
        self.subnet=deque()

    def backtrack(self,add_num):
        if add_num==self.set_num+1:
            self.result.append(self.subnet.copy())
            #self.layer-=1
            return


        #self.layer=add_num
        for i in range(2):
            if i==0:
                #self.subnet.append(self.layer)
                self.subnet.append(add_num)
            #print(self.layer)
            self.backtrack(add_num=add_num+1)
            if i==0:
                self.subnet.pop()
            #self.layer-=1
            #print(self.subnet)


        #self.subnet.pop()

if __name__=='__main__':
    obj=MySubSet(set_num=3)
    obj.backtrack(add_num=1)
    print(obj.result)
