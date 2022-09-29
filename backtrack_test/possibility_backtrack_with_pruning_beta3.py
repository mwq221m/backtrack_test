import pandas as pd
import numpy as np
from collections import deque
import time
from dlpf_in_disconnected_conditions import DLPFInDisconnectedConditions
import warnings
'''
目前实现了最基础的按照概率阈值按照回溯算法进行对故障树的深度优先搜索 在遇到概率低于阈值时回溯
接下来需要进行剪枝操作 剪枝根据n-2枚举下来存在风险的故障组合
该操作最大价值在于可以并行计算
剪枝操作更激进
新增：
在故障组合a和b（a<b）中，出现path有b却没有a直接return
******故障元件数更换为11个

'''
def calculate_fault_probability(outage_probability_list,fault_idx):
    operating_probability_list=1-outage_probability_list
    fault_probability_list=operating_probability_list.copy()
    for i in fault_idx:
        fault_probability_list[i]=outage_probability_list[i].copy()
    return np.product(fault_probability_list)

class PossibilityBacktrackwithPruning():
    def __init__(self,data,fault_idx1,fault_idx2):
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
        self.fault_idx1=fault_idx1
        self.fault_idx2=fault_idx2
        self.fault_idx_min=np.min([self.fault_idx1,self.fault_idx2])
        self.fault_idx_max=np.max([self.fault_idx1,self.fault_idx2])
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
        #if possibility>self.p_min:

        if possibility<self.p_min:
            #self.result.append(list(self.idx)[:-1].copy())
            #self.result.append(self.idx.copy())
            return#达到认为要回溯的节点
        if self.fault_idx_max in self.idx and self.fault_idx_min not in self.idx:
            return
        if self.fault_idx1 in self.idx and self.fault_idx2 in self.idx:
            self.result.append(self.idx.copy())#搜索路径上有想要的两个节点应该加入到结果
        #for i in range(startindex,self.num):
        if self.fault_idx1 in self.idx and self.fault_idx2 in self.idx:#当前路径已经存在需要的点 接下来的层正常搜索就行 不需要剪枝
            for i in range(startindex,self.num):
                self.idx.append(i)
                self.backtrack(startindex=i+1)
                self.idx.pop()#撤销之前的路径
        if self.fault_idx1 not in self.idx or self.fault_idx2 not in self.idx:
            for i in range(startindex,self.fault_idx_max+1):#当前情况需要的点还未出现 必须在接下来的层查找 剪枝去除不可能出现希望点的树枝
                self.idx.append(i)
                self.backtrack(startindex=i+1)
                self.idx.pop()#撤销之前的路径







if __name__=='__main__':
    start=time.time()
    data=pd.read_excel('component_outage_test.xlsx',sheet_name=2)
    st1=time.time()
    obj1=PossibilityBacktrackwithPruning(data=data,fault_idx1=0,fault_idx2=1)
    obj1.backtrack(startindex=0)
    ed1=time.time()

    st2=time.time()
    obj2 = PossibilityBacktrackwithPruning(data=data, fault_idx1=0, fault_idx2=2)
    obj2.backtrack(startindex=0)
    ed2=time.time()

    st3=time.time()
    obj3 = PossibilityBacktrackwithPruning(data=data, fault_idx1=0, fault_idx2=7)
    obj3.backtrack(startindex=0)
    ed3=time.time()

    st4=time.time()
    obj4 = PossibilityBacktrackwithPruning(data=data, fault_idx1=1, fault_idx2=2)
    obj4.backtrack(startindex=0)
    ed4=time.time()

    st5=time.time()
    obj5 = PossibilityBacktrackwithPruning(data=data, fault_idx1=1, fault_idx2=7)
    obj5.backtrack(startindex=0)
    ed5=time.time()

    st6=time.time()
    obj6 = PossibilityBacktrackwithPruning(data=data, fault_idx1=2, fault_idx2=7)
    obj6.backtrack(startindex=0)
    ed6=time.time()

    st7=time.time()
    obj7 = PossibilityBacktrackwithPruning(data=data, fault_idx1=3, fault_idx2=7)
    obj7.backtrack(startindex=0)
    ed7=time.time()

    st8=time.time()
    obj8 = PossibilityBacktrackwithPruning(data=data, fault_idx1=4, fault_idx2=6)
    obj8.backtrack(startindex=0)
    ed8=time.time()

    st9=time.time()
    obj9 = PossibilityBacktrackwithPruning(data=data, fault_idx1=4, fault_idx2=7)
    obj9.backtrack(startindex=0)
    ed9=time.time()

    st10=time.time()
    obj10 = PossibilityBacktrackwithPruning(data=data, fault_idx1=4, fault_idx2=8)
    obj10.backtrack(startindex=0)
    ed10=time.time()

    st11=time.time()
    obj11 = PossibilityBacktrackwithPruning(data=data, fault_idx1=5, fault_idx2=7)
    obj11.backtrack(startindex=0)
    ed11=time.time()

    st12=time.time()
    obj12 = PossibilityBacktrackwithPruning(data=data, fault_idx1=6, fault_idx2=7)
    obj12.backtrack(startindex=0)
    ed12=time.time()

    st13=time.time()
    obj13 = PossibilityBacktrackwithPruning(data=data, fault_idx1=6, fault_idx2=8)
    obj13.backtrack(startindex=0)
    ed13=time.time()

    st14=time.time()
    obj14 = PossibilityBacktrackwithPruning(data=data, fault_idx1=7, fault_idx2=8)
    obj14.backtrack(startindex=0)
    ed14=time.time()

    st15=time.time()
    obj15 = PossibilityBacktrackwithPruning(data=data, fault_idx1=7, fault_idx2=9)
    obj15.backtrack(startindex=0)
    ed15=time.time()

    st16=time.time()
    obj16 = PossibilityBacktrackwithPruning(data=data, fault_idx1=7, fault_idx2=10)
    obj16.backtrack(startindex=0)
    ed16=time.time()

    st=time.time()
    result_list=[]
    for i in obj1.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj2.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj3.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj4.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj5.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj6.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj7.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj8.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj9.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj10.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj11.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj12.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj13.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj14.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj15.result:
        if i not in result_list:
            result_list.append(i)

    for i in obj16.result:
        if i not in result_list:
            result_list.append(i)

    ed=time.time()
    end=time.time()
    print('运行时间',end-start)
    time_temp=np.max([ed1-st1,ed2-st2,ed3-st3,ed4-st4,ed5-st5,ed6-st6,ed7-st7,ed8-st8,ed9-st9,ed10-st10,ed11-st11,ed12-st12,ed13-st13,ed14-st14,ed15-st15,ed16-st16])+ed-st
    print('并行运行时间',time_temp)

    result_list_original_idx=[]
    for result in result_list:
        result_original_idx=[]
        for i in result:
            result_original_idx.append(obj1.outage_list[i])
        result_list_original_idx.append(result_original_idx)


    # for fault_idx in result_list_original_idx:
    #     print('\n计算到', fault_idx)
    '''
    以下部分将筛选出的预想事故集进行风险评估
    '''


    # temp_list=[]
    # branch_data = pd.read_excel('rts79_test.xlsx', sheet_name=0)
    # bus_data = pd.read_excel('rts79_test.xlsx', sheet_name=1)
    #
    # with warnings.catch_warnings():
    #     warnings.simplefilter('ignore')
    #
    #     for i in range(len(result_list_original_idx)):
    #         fault_idx=result_list_original_idx[i]
    #         print('\n计算到', fault_idx)
    #         fault_probability=calculate_fault_probability(outage_probability_list=np.array(obj1.possibility_list),fault_idx=result_list[i])
    #         curtailment = 0
    #         generator_tripping = 0
    #         v_risk_list = np.zeros(24)
    #         pf_risk_list = np.zeros(38)
    #         obj = DLPFInDisconnectedConditions(branch_data=branch_data, bus_data=bus_data, fault_idx=fault_idx)
    #         obj.run()
    #         v_risk_list += np.array(obj.v_risk_metrics['v_risk_metrics'])
    #         pf_risk_list += np.array(obj.pf_risk_metrics['pf_risk_metrics'])
    #         curtailment += np.sum(obj.curtailment_list)
    #         generator_tripping += np.sum(obj.generator_tripping_list)
    #         temp_list.append(
    #             {'fault_idx': fault_idx, 'fault_probability': fault_probability, 'v_risk_metric': np.sum(v_risk_list),
    #              'pf_risk_metric': np.sum(pf_risk_list),
    #              'curtailment_metric': curtailment / 2850, 'generator_tripping': generator_tripping / 2904.2})
    #     result_df = pd.DataFrame(temp_list)
    #     result_df['v_risk'] = result_df['fault_probability'] * result_df['v_risk_metric']
    #     result_df['pf_risk'] = result_df['fault_probability'] * result_df['pf_risk_metric']
    #     result_df['curtailment_risk'] = result_df['fault_probability'] * result_df['curtailment_metric']
    #     result_df['generator_tripping_risk'] = result_df['fault_probability'] * result_df['generator_tripping']
    #     result_df['risk'] = result_df['v_risk'] + result_df['pf_risk'] + result_df['curtailment_risk'] + result_df[
    #         'generator_tripping_risk']

