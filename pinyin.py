#!python3
#coding=utf8
import numpy as np
import sys
import time
import numpy as np
import json
from  os.path import isfile, join, basename
from pypinyin import lazy_pinyin
import pickle
import re
class Chinese_character:
    def __init__(self,name,rank):
        self.name=name
        self.frequency=0
        self.pinyin=lazy_pinyin(name)
        self.rank=rank
        #self.next_count=0 #这是为了转移矩阵最后得到概率而不是个次数，其实好像不需要，直接sum(一行即可)
    def __repr__(self):
       return '{}的拼音是{},频率是{},是第{}个字'.format(self.name, self.pinyin, self.frequency, self.rank)
class Analyzer:
    def __init__(self,deal_list=[]):
        f=open("./resource/一二级汉字表.txt", "r", encoding="gbk")
        self.states=list(f.read())
        f.close()
        self.transition = np.zeros([6763, 6764],dtype='int')
        self.ch_dic={} #key就是汉字
        self.pin_dic={}
        self.deal_list=deal_list
        #这个将要存的就是经过处理的新闻
        self.pattern='[^\u4e00-\u9fff]+' #用此正则表达式处理新闻
        self.path="./resource/"
        self.storage_path="./data/"
    def getDic__(self):
        filename="./data/pin_dic.txt"
        if isfile(filename):
            with open(filename, "rb") as rf:
                self.pin_dic=pickle.load(rf)
        else:
            with open("./resource/拼音汉字表.txt", "r", encoding="gbk") as f:
                input = f.readlines()
                for line in input:
                    line_list = line.split()
                    pinyin = line_list[0]
                    line_list.pop(0)
                    self.pin_dic[pinyin]=line_list
                with open(filename, "wb") as wf:
                    pickle.dump(self.pin_dic, wf)
        filename="./data/ch_dic.txt"
        filename_f="./data/ch_dic_frequency.txt"
        if isfile(filename_f):
            with open(filename_f, "rb") as rf:
                self.ch_dic=pickle.load(rf)
        elif isfile(filename):
            with open(filename, "rb") as rf:
                self.ch_dic=pickle.load(rf)
        else:
            for i in range(len(self.states)):
                self.ch_dic[self.states[i]] = Chinese_character(self.states[i], i)  #初步创立了字典
                with open(filename, "wb") as wf: #这里写入不含拼音的dic，逻辑上还是没什么问题
                    pickle.dump(self.ch_dic, wf)
    def dump__(self):
        selfname = "./data/analyzer.txt"
        with open(selfname, "wb") as wf:
            pickle.dump(self, wf)
    def deal_plain_text__(self, file):
        filename = self.path+ file #file是Pickle得到的
        #这个会不会浪费时间
        f = open(filename, "r", encoding="gbk")
        text = f.readlines()
        f.close()
        for index in range(len(text)-1): #-1是因为index+1
            ch = text[index]
            if not (ch in self.ch_dic):
                continue
            next_ch = text[index + 1]
            if next_ch in self.ch_dic:
                self.transition[self.ch_dic[ch].rank,self.ch_dic[next_ch].rank] += 1
            else:
                self.transition[self.ch_dic[ch].rank,6763] += 1
    def deal_news__(self, file): #我们确保调用这个函数的时候，新闻一定是没有被处理过的
        filename = self.path+ file #file是Pickle得到的
        #这个会不会浪费时间
        f = open(filename, "r", encoding="gbk")
        text = f.readlines()
        f.close()
        for news in text: #re处理在里面进行，这是一则新闻
            try:
                news_text = json.loads(news)['html']
                for index in range(len(news_text)-1): #-1是因为index+1
                    ch = news_text[index]
                    if not (ch in self.ch_dic):
                        continue
                    next_ch = news_text[index + 1]
                    if next_ch in self.ch_dic:
                        self.transition[self.ch_dic[ch].rank,self.ch_dic[next_ch].rank] += 1
                    else:
                        self.transition[self.ch_dic[ch].rank,6763] += 1
            except:
                print("skip")
                pass
        print("{} finish".format(file))
    def getFrequency__(self):
        frequency=self.transition.sum(axis=1)
        for i in range(len(frequency)):
            self.ch_dic[self.states[i]].frequency=frequency[i]
    def routine(self):
        self.getDic__()
        for item in self.deal_list:
            self.deal_news__(item)
        self.getFrequency__()
        self.dump__()
    def expand(self, deal_list):
        flag = False
        for item in deal_list:
            if not item in self.deal_list:
                self.deal_plain_text__(item)
                self.deal_list.append(item)
                flag=True
        if(flag):
            self.getFrequency__()
            self.dump__()
class Viterbi:
    def __init__(self, analyzer): #这个就是Analyzer类，里面的数据应当完全封装好好了，不做修改，但是有个问题，这个类只处理一句话？那么何必封装成类呢？
        self.analyzer=analyzer
        self.T1=[]
        self.T2=[]
        self.observations=[]
        self.candidate=[]
        self.rows=6763 #这就是总的汉字字数
        self.cols=0
        self.res=[]
        self.pinyin_sentence=""
    def fillTable__(self, sentence):
        '''是维特比算法填表这一部分，填T1和T2表'''
        self.reset__(sentence) #会清空T1和T2，以及candidate
        self.observations=self.pinyin_sentence.split()
        self.cols = len(self.observations) #就是输入的拼音数
        self.candidate.append(self.analyzer.pin_dic[self.observations[0]])
        # self.T1.append(list(map(lambda x:self.analyzer.ch_dic[x].frequency,self.candidate[0])))
        self.T1.append([1]*len(self.candidate[0]))
        self.T2.append([0]*len(self.candidate[0]))
        for i in range(1, self.cols):
            self.candidate.append(self.analyzer.pin_dic[self.observations[i]])
            self.T1.append([])
            self.T2.append([])
            for j in range(len(self.candidate[i])):
                last_len = len(self.T1[i-1])
                count_p = np.zeros(last_len)
                for k in range(last_len):
                    count_p[k] = self.T1[i-1][k] * self.analyzer.transition[self.analyzer.ch_dic[self.candidate[i-1][k]].rank,self.analyzer.ch_dic[self.candidate[i][j]].rank]
                self.T1[i].append(np.max(count_p))
                self.T2[i].append(np.argmax(count_p))
    def backTrack__(self):
        '''是维特比算法回溯这一部分，T1和T2表在fillTable中已经填好'''
        #现在希望输出状态
        last_state = np.argmax(self.T1[self.cols-1])
        self.res = []
        for i in range(self.cols - 1, -1, -1):
            self.res.append(last_state)
            last_state = self.T2[i][last_state]
        self.res=list(reversed(self.res))
    def getRes__(self):
        '''返回字符串'''
        ans_str=""
        for i in range(self.cols):
            ans_str+=self.analyzer.pin_dic[self.observations[i]][self.res[i]]
        return ans_str
    def reset__(self, sentence):
        self.T1=[]
        self.T2=[]
        self.observations=[]
        self.candidate=[]
        self.cols=0
        self.res=[]
        self.pinyin_sentence=sentence
    def routine(self, sentence):
        '''这个函数是外部调用接口，接受一句拼音，返回字符串'''
        self.reset__(sentence)
        self.fillTable__(sentence)
        self.backTrack__()
        return self.getRes__()
def deal_test_in(input_path,output):
    '''这个函数的功能是：处理样例，将正确答案输出到一个文件，错误答案输出到另一个文件'''
    filename=basename(input_path).split('.')[0]
    output_path=output
    fin=open(input_path, "r")
    test_in=fin.readlines()
    # fout_right=open("./data/pinyin_test_right{}_{}.txt".format(no, filename),"w")
    fout_mine=open(output_path,"w")
    # for index in range(0,len(test_in),2):
    for index in range(len(test_in)):
        ans=viterbi.routine(test_in[index].lower().replace('qv','qu').replace('xv','xu'))
        fout_mine.write(ans+'\n')
        # fout_right.write(test_in[index+1])
    fout_mine.close()
    # fout_right.close()
    fin.close()
    # if not isfile(output_path):
    #     fin=open(input_path, "r")
    #     test_in=fin.readlines()
    #     fout_right=open("./data/pinyin_test_right{}_{}.txt".format(no, filename),"w")
    #     fout_mine=open(output_path,"w")
    #     for index in range(0,len(test_in),2):
    #         ans=viterbi.routine(test_in[index].lower().replace('qv','qu').replace('xv','xu'))
    #         fout_mine.write(ans+'\n')
    #         fout_right.write(test_in[index+1])
    #     fout_mine.close()
    #     fout_right.close()
    #     fin.close()
    # report_right_percentage(output_path)

def report_right_percentage(output_path):
    '''此函数的功能就是分别给出单字正确率和整句正确率，参数no是第几次调用此函数的记录，目的是输出文件名不重复'''
    # print("output_path=",output_path)
    right_path=output_path.replace('mine','right')
    fout_right=open(right_path,"r")
    fout_mine=open(output_path,"r")
    re_exp = '[^\u4e00-\u9fff]+'
    text_right = re.sub(re_exp, '', fout_right.read())
    text_mine = re.sub(re_exp, '', fout_mine.read())
    with open("/Users/quebec/Desktop/compare_a.txt", "w") as f:
        f.write(text_right)
    with open("/Users/quebec/Desktop/compare_b.txt", "w") as f:
        f.write(text_mine)
    print("len(text_right)={}".format(len(text_right)))
    print("len(text_mine)={}".format(len(text_mine)))
    # for index in range(len(text_mine)):
    #     if(lazy_pinyin(text_right[index])!=lazy_pinyin(text_mine[index])):
    #         print(index)
    #         print(text_right[index], text_mine[index])
    fout_mine.seek(0,0)
    fout_right.seek(0,0)
    text_right_list=fout_right.readlines()

    text_mine_list=fout_mine.readlines()
    print("len(text_right_list)={}".format(len(text_right_list)))
    print("len(text_mine_list)={}".format(len(text_mine_list)))
    right_s=0
    sentence_num=len(text_mine_list)
    sum=len(text_mine)
    # print(sentence_num,sum)
    for index in range(sentence_num):
        text_right_s=re.sub(re_exp, '', text_right_list[index])
        text_mine_s=re.sub(re_exp, '', text_mine_list[index])
        # text_mine_s=re.sub(re_exp, '', text_mine)
        if(text_right_s==text_mine_s):
            right_s+=1
    
    right=0
    for index in range(sum):
        if(text_right[index]==text_mine[index]):
            right+=1
    print('字正确率：{:.2%}，整句正确率：{:.2%}'.format(right/sum,right_s/sentence_num))
    fout_right.close()
    fout_mine.close()
if __name__=="__main__":
    selfname = "./data/analyzer.txt"
    if isfile(selfname):
        with open(selfname, "rb") as rf:
            analyzer = pickle.load(rf)
    else:
        num_list = [2, 4, 5, 6, 7, 8, 9, 10, 11]
        news_list = ["2016-{:0>2d}.txt".format(i) for i in num_list]
        analyzer=Analyzer(news_list)
        analyzer.routine()
    viterbi=Viterbi(analyzer)
    # viterbi.analyzer.transition=viterbi.analyzer.transition.astype('float')+0.3
    args=sys.argv
    if(len(args)==3):
        input=args[1]
        output=args[2]
    else:
        print("输入有误，请给出输入和输出的绝对路径")
    # elif len(args)==2:
    #     input=args[1]
    #     output="result.txt"
    deal_test_in(input,output)


    
    