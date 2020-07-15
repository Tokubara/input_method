import numpy as np
import pandas as pd
from  os.path import isfile, join
from pypinyin import lazy_pinyin
import json
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
        print('{}的拼音是{},频率是{},是第{}个字'.format(self.name, self.pinyin, self.frequency, self.rank))

# states=""
class Analyzer:
    def __init__(self):
        f=open("/Users/quebec/Documents/Program/py/hw1_pinyin/resource/一二级汉字表.txt", "r", encoding="gbk")
        self.states=list(f.read())
        f.close()
        self.transition = pd.DataFrame(index=self.states, columns=self.states, data=np.zeros([6763, 6763]))
        self.ch_dic={} #key就是汉字
        self.pin_dic={}
        # self.content=[] #这个将要存的就是经过处理的新闻
        self.pattern='[^\u4e00-\u9fff]+' #用此正则表达式处理新闻
        self.path="/Users/quebec/Documents/Program/py/hw1_pinyin/resource/"
        self.storage_path="/Users/quebec/Documents/Program/py/hw1_pinyin/data/"

    def getDic(self):
        filename="/Users/quebec/Documents/Program/py/hw1_pinyin/data/pin_dic.txt"
        if isfile(filename):
            with open(filename, "rb") as rf:
                self.pin_dic=pickle.load(rf)
        else:
            with open("/Users/quebec/Documents/Program/py/hw1_pinyin/resource/拼音汉字表.txt", "r", encoding="gbk") as f:
                input = f.readlines()
                for line in input:
                    line_list = line.split()
                    pinyin = line_list[0]
                    line_list.pop(0)
                    self.pin_dic[pinyin]=line_list
                with open(filename, "wb") as wf:
                    pickle.dump(self.pin_dic, wf)

        filename="/Users/quebec/Documents/Program/py/hw1_pinyin/data/ch_dic.txt"
        if isfile(filename):
            with open(filename, "rb") as rf:
                self.ch_dic=pickle.load(rf)
        else:
            for i in range(len(self.states)):
                self.ch_dic[self.states[i]] = Chinese_character(self.states[i], i)  # 初步创立了字典
                with open(filename, "wb") as wf:
                    pickle.dump(self.ch_dic, wf)


    def deal_news(self, file):
        filename = join(self.path, file) #file是Pickle得到的
        filename_p=join(self.storage_path,file.replace('.', '_.'))
        print(filename_p)
        if isfile(filename_p):
            print(file, "exists")
            with open(filename_p, "rb") as rf:
                self.ch_dic = pickle.load(rf) #这个会不会浪费时间
        else:
            f = open(filename, "r")
            text = f.readlines()
            f.close()
            for news in text: #re处理在里面进行，这是一则新闻
                # try:
                news_text=json.loads(news)['html']
                #     news_text = sub(self.pattern, '', news)
                for index in range(len(news_text)-1): #-1是因为index+1
                    ch = news_text[index]
                    if not ch in self.ch_dic:
                        continue
                    next_ch = news_text[index + 1]
                    self.ch_dic[ch].frequency += 1
                    if next_ch in self.ch_dic:
                        # print(ch, next_ch)
                        self.transition.loc[ch, next_ch] += 1

                with open(filename_p, "wb") as wf:
                    pickle.dump(self.ch_dic, wf)
                # except:
                #     print("skip")
                #     pass
        print("{} finish".format(file))

if __name__ == "__main":

    analyzer=Analyzer()

    analyzer.getDic()
    print(analyzer.pin_dic["hei"])
# print(analyzer.ch_dic["大"].frequency)
# print(analyzer.transition.loc["大","家"])
# print(len(analyzer.states))
