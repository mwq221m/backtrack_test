import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
#import pandasgui as pg
from dlpf import DLPF
import warnings
import time

'''
除了各个子网分区信息需要识别正确 还需要注意可能存在的切负荷问题
例如一个分区只有一个pv节点 其余都是pq且负荷需求远超p
可以现在子图中将节点类型和负荷大小信息加入图中
'''
'''
主要作用是判断网络是否有解列，若有则将各个子网节点重新编号 并且判断当前子网是否适合直接进行潮流计算（网络是否含有平衡节点or子网有功注入大于零）
目前发现branch_data_list有边重复的问题:原因在于rts79存在并联导线
发现有出现子网只有电源没有负荷，类似这种情况下让pv节点当做平衡节点会使得该节点注入功率为负 不符合实际情况
发现未使用multigraph导致的bug 原本网络解列的判断不准确
'''

class DLPFInDisconnectedConditions():
    def __init__(self,branch_data,bus_data,fault_idx):
        self.branch_data=branch_data
        self.bus_data=bus_data
        self.bus_type={}
        self.bus_p={}
        self.bus_q={}
        self.fault_idx=fault_idx
        self.fault_num=len(self.fault_idx)
        self.bus_num = len(self.bus_data)
        self.branch_num = len(self.branch_data)
        #self.net = nx.Graph()
        self.net=nx.MultiGraph()
        self.node_list = []
        self.edge_list = []
        self.bus_result_list=[]
        self.pf_result_list=[]
        self.curtailment_list=[]
        self.generator_tripping_list=[]
        for i in range(self.bus_num):
            temp = self.bus_data.iloc[i]
            num = temp['num']
            self.node_list.append(num)
            type=temp['type']
            p=temp['p']
            q=temp['q']
            self.bus_type[num]=type
            self.bus_p[num]=p
            self.bus_q[num]=q


        for i in range(self.branch_num):
            temp = self.branch_data.iloc[i]
            start = int(temp['start'])
            end = int(temp['end'])
            status = temp['status']
            if status == 1:
                self.edge_list.append((start, end))
        self.net.add_nodes_from(self.node_list)

        for i,j in self.bus_p.items():
            self.net.nodes[i]['p']=j
        for i,j in self.bus_q.items():
            self.net.nodes[i]['q']=j
        for i,j in self.bus_type.items():
            self.net.nodes[i]['type']=j

        self.net.add_edges_from(self.edge_list)
        self.remove_list=[]
        for i in self.fault_idx:
            #print(i)
            temp=self.branch_data.iloc[i]
            start=int(temp['start'])
            end=int(temp['end'])
            status=temp['status']
            self.remove_list.append((start,end))
        self.net.remove_edges_from(self.remove_list)
        self.number_connected_components = nx.number_connected_components(self.net)
        #self.connected_components=nx.connected_components(self.net)
        self.connected_components=[i for i in nx.connected_components(self.net)]
        self.subgraph=[nx.Graph() for i in range(self.number_connected_components)]
        for i in range(self.number_connected_components):
            #g=self.subgraph[i]
            nbunch=self.connected_components[i]
            #print(nbunch)
            self.subgraph[i]=nx.subgraph(self.net,nbunch=nbunch)

        temp_branch_data=self.branch_data.copy()
        temp_branch_data=temp_branch_data.drop([i for i in range(self.branch_num)])#dataframe的drop和append需要x=x.drop()的形式
        temp_bus_data=self.bus_data.copy()
        temp_bus_data=temp_bus_data.drop([i for i in range(self.bus_num)])
        self.branch_data_list=[temp_branch_data for i in range(self.number_connected_components)]
        self.bus_data_list=[temp_bus_data for i in range(self.number_connected_components)]

        self.subgraph_nodes_num=[]
        self.subgraph_edges_num=[]
        for i in range(self.number_connected_components):
            g=self.subgraph[i]
            self.subgraph_nodes_num.append(g.number_of_nodes())
            self.subgraph_edges_num.append(g.number_of_edges())






    def draw(self):
        plt.figure()
        nx.draw(self.net,with_labels=True)
        plt.show()

    def draw_subgraph(self):
        for i in range(self.number_connected_components):
            plt.figure()
            nx.draw(self.subgraph[i],with_labels=True)
            plt.show()

    def generate_subgraph_branches_data(self,subgraph_index):
        branches_num=self.subgraph_edges_num[subgraph_index]
        g=self.subgraph[subgraph_index]
        branches_list=[i for i in g.edges]
        #print(branches_list)
        # print(len(branches_list))
        for i in range(branches_num):
            branch=branches_list[i]
            start=branch[0]
            end=branch[1]
            if len(self.branch_data[self.branch_data['start']==start][self.branch_data['end']==end])==0:
                start,end=end,start
            #self.branch_data_list[subgraph_index]=self.branch_data_list[subgraph_index].append(self.branch_data[self.branch_data.apply(lambda x:x['start']==start and x['end']==end,axis=1)])
            self.branch_data_list[subgraph_index]=self.branch_data_list[subgraph_index].append(self.branch_data[self.branch_data['start']==start][self.branch_data['end']==end].iloc[0])

    def generate_subgraph_nodes_data(self,subgraph_index):
        nodes_num=self.subgraph_nodes_num[subgraph_index]
        g=self.subgraph[subgraph_index]
        nodes_list=[i for i in g.nodes]
        for i in range(nodes_num):
            node=nodes_list[i]
            self.bus_data_list[subgraph_index]=self.bus_data_list[subgraph_index].append(self.bus_data[self.bus_data['num']==node])







    def generate_subgraph_data(self):
        for i in range(self.number_connected_components):
            self.generate_subgraph_branches_data(subgraph_index=i)
            self.generate_subgraph_nodes_data(subgraph_index=i)
        self.subnets_index_list = []#将子网与连续的节点编号映射 方便进行DLPF模块的调用
        for i in range(self.number_connected_components):
            bus_dic = {}
            bus_data = self.bus_data_list[i]
            bus_num = bus_data['num']
            # print('bus_num',bus_num)
            for j in range(len(bus_data)):
                # bus_dic[j+1]=bus_num.iloc[j]
                bus_dic[bus_num.iloc[j]] = j + 1
            self.subnets_index_list.append(bus_dic)

    def pf_judgement_for_subgraph(self,subgraph_index):
        flag=0
        g=self.subgraph[subgraph_index]
        branch_data=self.branch_data_list[subgraph_index]
        bus_data=self.bus_data_list[subgraph_index]
        if len(branch_data)>0:#判断不是孤岛节点
            if 'R' in list(bus_data['type']):#子网有平衡节点可直接潮流计算
                flag=1
                return flag
            if bus_data['p'].sum()>0 and bus_data['p'].sum()<np.max(bus_data['p']):#没有平衡节点时有功注入大于零可认为电源充足 将一个PV节点替换为平衡节点即可
                flag=1
                return flag
        if bus_data['p'].sum()>=np.max(bus_data['p'])>0:#单个pv节点也会被归类到这里
            flag=2#************尝试定义一下需要切机的情况
        return flag#*************逻辑可能还有漏洞 需要梳理***********

    def pf_judgement(self):
        self.pf_flag=[]
        for i in range(self.number_connected_components):
            flag=self.pf_judgement_for_subgraph(subgraph_index=i)
            self.pf_flag.append(flag)

    def run_dlpf_for_subnets(self,subgraph_index):
        subnets_index=self.subnets_index_list[subgraph_index]
        subnets_index_reverse={j:i for i,j in subnets_index.items()}
        bus_data=self.bus_data_list[subgraph_index].copy()
        branch_data=self.branch_data_list[subgraph_index].copy()
        flag=self.pf_flag[subgraph_index]
        if flag==1:#满足潮流计算的判定 即存在平衡节点或者无平衡节点时有功注入大于零
            if 'R' not in list(bus_data['type']):#*********找到第一个pv节点并将其设置为平衡节点 写的是否正确需要将两个子网都可以计算的拓扑输入测试
                # for i in bus_data.index:#index属性可以返回dataframe的索引 对于索引乱序的情况很有帮助
                #     # print(bus_data.index)
                #     # print('bus_data',bus_data)
                #     type=bus_data['type'][i]
                #     if type=='S':
                #         bus_data.loc[i,'type']='R'
                #         bus_data.loc[i,'theta']=0
                #         break#*******************
                idx=bus_data['p'][bus_data['type']=='S'].idxmax()#选取最大的pv节点当做平衡节点
                bus_data.loc[idx,'type']='R'
                bus_data.loc[idx,'theta']=0
            for i in range(len(bus_data)):
                before=bus_data['num'].iloc[i].copy()
                after=subnets_index[before]
                bus_data['num'].iloc[i]=after
            for i in range(len(branch_data)):
                start_before=branch_data['start'].iloc[i].copy()
                end_before=branch_data['end'].iloc[i].copy()
                start_after=subnets_index[start_before]
                end_after=subnets_index[end_before]
                branch_data['start'].iloc[i]=start_after
                branch_data['end'].iloc[i]=end_after
            # print('bus_data',bus_data)
            # print('branch_data',branch_data)
            pf_obj=DLPF(bus_data=bus_data,branch_data=branch_data)
            pf_obj.rundlpf()
            pf_obj.show_result()
            bus_result=pf_obj.bus_result.copy()
            # print(bus_result)
            # print(subnets_index_reverse)
            branch_result=pf_obj.pf_result.copy()
            #print('before',branch_result)
            for i in range(len(bus_result)):
                before=bus_result['num'].iloc[i].copy()
                after=subnets_index_reverse[before]
                bus_result['num'].iloc[i]=after
            #print(bus_result)
            for i in range(len(branch_data)):
                start_before=branch_result['start'].iloc[i].copy()
                end_before=branch_result['end'].iloc[i].copy()
                start_after=subnets_index_reverse[start_before]
                end_after=subnets_index_reverse[end_before]
                branch_result['start'].iloc[i]=start_after
                branch_result['end'].iloc[i]=end_after
            #print('after',branch_result)
            return (bus_result,branch_result)
        if flag==0:#不存在平衡节点且有功注入小于零
            sum_temp=np.sum(bus_data['p'])
            return -sum_temp
        if flag==2:
            sum_temp=np.sum(bus_data['p'])
            return sum_temp

    def run_dlpf(self):
        for i in range(self.number_connected_components):
            flag=self.pf_flag[i]
            if flag==1:
                (bus_result,branch_result)=self.run_dlpf_for_subnets(subgraph_index=i)
                self.bus_result_list.append(bus_result)
                self.pf_result_list.append(branch_result)
            if flag==0:
                curtailment=self.run_dlpf_for_subnets(subgraph_index=i)
                self.curtailment_list.append(curtailment)
            if flag==2:
                generater_tripping=self.run_dlpf_for_subnets(subgraph_index=i)
                self.generator_tripping_list.append(generater_tripping)

    def risk_metircs_calculation(self):
        '''

        难点在于双回线路断开一条的结果在pf_risk_metrics_df的正确显示
        风险计算后直接在pf_risk_metrics、v_risk_metrics、curtailment_list和generator_tripping_list显示
        '''
        self.v_risk_metrics_df=self.bus_data.loc[:,['num']].copy()
        self.pf_risk_metrics_df=self.branch_data.loc[:,['start','end','rating(MVA)']].copy()
        for i in range(len(self.bus_result_list)):
            bus_result=self.bus_result_list[i]
            # self.v_risk_metrics_df=pd.merge(self.v_risk_metrics_df,bus_result,on='num',how='left')
            branch_result=self.pf_result_list[i]
            branch_result['S']=np.sqrt(branch_result['p']**2+branch_result['q']**2)
            # self.pf_risk_metrics_df=pd.merge(self.pf_risk_metrics_df,branch_result,on=['start','end'],how='left')
            #self.pf_risk_metrics_df=pd.merge()##################
            for j in range(len(bus_result)):
                num=bus_result['num'][j]
                v=bus_result['v'][j]
                theta=bus_result['theta'][j]
                idx=self.v_risk_metrics_df[self.v_risk_metrics_df['num']==num].index
                self.v_risk_metrics_df.loc[idx,'v']=v
                self.v_risk_metrics_df.loc[idx,'theta']=theta
            for j in range(len(branch_result)):
                start=branch_result['start'][j]
                end=branch_result['end'][j]
                S=branch_result['S'][j]
                idx=self.pf_risk_metrics_df[self.pf_risk_metrics_df['start']==start][self.pf_risk_metrics_df['end']==end].index
                #length=len(idx)
                length=len(branch_result[branch_result['start']==start][branch_result['end']==end])#检查潮流结果中对于双回线路是否两条导线都在运行
                if length>1:
                #print(idx)
                    self.pf_risk_metrics_df.loc[idx,'S']=S
                else:
                    self.pf_risk_metrics_df.loc[idx[0],'S']=S
            self.pf_risk_metrics_df['S']=self.pf_risk_metrics_df['S'].fillna(value=0)
            self.pf_risk_metrics_df['S_excess']=(self.pf_risk_metrics_df['rating(MVA)']-self.pf_risk_metrics_df['S'])/self.pf_risk_metrics_df['rating(MVA)']
            self.pf_risk_metrics_df['pf_risk_metrics']=self.pf_risk_metrics_df['S_excess'].apply(lambda x:0 if x>0 else -x)
            self.v_risk_metrics_df['v_risk_metrics']=self.v_risk_metrics_df['v'].apply(lambda x:x-1.05 if x>1.05 else (0.95-x if x<0.95 else 0))
            self.v_risk_metrics=self.v_risk_metrics_df.loc[:,['num','v_risk_metrics']]
            self.pf_risk_metrics=self.pf_risk_metrics_df.loc[:,['start','end','pf_risk_metrics']]












    def run(self):
        self.generate_subgraph_data()
        self.pf_judgement()
        self.run_dlpf()
        self.risk_metircs_calculation()



































if __name__=='__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        # branch_data = pd.read_excel('14_bus_test.xlsx', sheet_name=0)
        # bus_data = pd.read_excel('14_bus_test.xlsx', sheet_name=1)
        branch_data = pd.read_excel('rts79_test.xlsx', sheet_name=0)
        bus_data = pd.read_excel('rts79_test.xlsx', sheet_name=1)
        start=time.time()
        # fault_idx=(0,1,2)
        #fault_idx = (4,14,32)
        #fault_idx=(11,15)
        #fault_idx=(2,3)
        #fault_idx=(0,27,29)
        #fault_idx=(31,)
        #fault_idx=(5,9)
        fault_idx=(3,7,9,10)
        obj=DLPFInDisconnectedConditions(branch_data=branch_data,bus_data=bus_data,fault_idx=fault_idx)
        obj.draw()
        obj.draw_subgraph()
        obj.generate_subgraph_data()
        #pg.show(bus_data)
        obj.pf_judgement()
        # obj.run_dlpf_for_subnets()
        #obj.run_dlpf_for_subnets(subgraph_index=0)
        obj.run_dlpf()
        obj.risk_metircs_calculation()
        end=time.time()
        print('运算时间',end-start)




