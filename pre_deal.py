import numpy as np
import pandas as pd
from  os.path import isfile, join
from pypinyin import lazy_pinyin
import json
import pickle

class Chinese_character:
    def __init__(self,name,rank):
        self.name=name 
        self.frequency=0 # 出现的频率=0
        self.pinyin=lazy_pinyin(name) # 自动获得汉字的拼音
        self.rank=rank
        #self.next_count=0 #这是为了转移矩阵最后得到概率而不是个次数，其实好像不需要，直接sum(一行即可)
    def __repr__(self):
        print('{}的拼音是{},频率是{},是第{}个字'.format(self.name, self.pinyin, self.frequency, self.rank))

class Analyzer:
    def __init__(self):
        '''
        pin_dict:字典，key:拼音，比如'an'，value:这个拼音的所有汉字(由文件拼音汉字表给出)，这个在初始化后就不变了
        states:汉字列表，由文件一二级汉字表给出，一二级汉字表是按照频率排序的
        transition:dataframe，其中横和列都是汉字，用起来和矩阵一样，相当于一个有名字的矩阵(R中的矩阵本来就可以有名字)，转移矩阵
        ch_dict:字典，key:汉字，字符串，比如'阿'，value:此汉字对应的Chinese_character对象，与pin_dict不同，ch_dict会根据语料变化
        path:str，是资源文件的路径
        storage_path:是存储中间得到的字典文件的路径
        '''
        f=open("/Users/quebec/Documents/Program/py/hw1_pinyin/resource/一二级汉字表.txt", "r", encoding="gbk")
        self.states=list(f.read()) # 所有的汉字，由
        f.close()
        self.transition = pd.DataFrame(index=self.states, columns=self.states, data=np.zeros([6763, 6763]))
        self.ch_dic={}
        self.pin_dic={}
        self.pattern='[^\u4e00-\u9fff]+' #用此正则表达式处理新闻
        self.path="/Users/quebec/Documents/Program/py/hw1_pinyin/resource/"
        self.storage_path="/Users/quebec/Documents/Program/py/hw1_pinyin/data/"

    def getDic(self):
        '''
        得到pin_dict和pin_dic
        dict都是用pickle序列化得到的文件，文件名由下面的filename给出，如果此文件已存在，那么加载，否则创建字典，并且序列化保存到filename中
        '''
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
                self.ch_dic[self.states[i]] = Chinese_character(self.states[i], i)
                with open(filename, "wb") as wf:
                    pickle.dump(self.ch_dic, wf)


    def deal_news(self, file):
        '''
        读取文件中的新闻(有多个新闻，每则新闻是一行，而且是json格式的)，根据这些新闻修改ch_dict和转移矩阵
        文件中不在字典中的字不予以考虑
        Parameters
        ----------
        file : str
            新闻文件的名字
        '''
        filename = join(self.path, file)
        filename_p=join(self.storage_path,file.replace('.', '_.'))
        # print(filename_p)
        if isfile(filename_p):
            print(file, "exists")
            with open(filename_p, "rb") as rf:
                self.ch_dic = pickle.load(rf)
        else:
            f = open(filename, "r")
            text = f.readlines()
            f.close()
            for news in text: #re处理在里面进行，这是一则新闻
                # try:
                news_text=json.loads(news)['html']
                for index in range(len(news_text)-1): # -1与next_ch有关
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
# print(analyzer.pin_dic["hei"])
# print(analyzer.ch_dic["大"].frequency)
# print(analyzer.transition.loc["大","家"])
# print(len(analyzer.states))
