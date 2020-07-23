#!python3
# coding=utf8
import numpy as np
import sys
import time
import numpy as np
import json
from os.path import isfile, join, basename
from pypinyin import lazy_pinyin
import pickle
import re


class Chinese_character:
    def __init__(self, name, rank):
        '''
        name就是汉字字符串，rank并不重要，相当于是数和字的映射，frequency初始化为0，根据读入的语料修改，pinyin就是汉字的拼音
        '''
        self.name = name
        self.frequency = 0
        self.pinyin = lazy_pinyin(name)
        self.rank = rank
        # self.next_count=0 #这是为了转移矩阵最后得到概率而不是个次数，其实好像不需要，直接sum(一行即可)

    def __repr__(self):
        return '{}的拼音是{},频率是{},是第{}个字'.format(self.name, self.pinyin, self.frequency, self.rank)


class Analyzer:
    '''
    这个类与算法无关，完全是对文本的处理(频率/转移矩阵的修改/持久化)
    '''

    def __init__(self, deal_list=[]):
        '''
        pin_dict:字典，key:拼音，比如'an'，value:这个拼音的所有汉字(由文件拼音汉字表给出)，这个在初始化后就不变了
        states:汉字列表，由文件一二级汉字表给出，一二级汉字表是按照频率排序的
        transition:dataframe，其中横和列都是汉字，用起来和矩阵一样，相当于一个有名字的矩阵(R中的矩阵本来就可以有名字)，转移矩阵
        ch_dict:字典，key:汉字，字符串，比如'阿'，value:此汉字对应的Chinese_character对象，与pin_dict不同，ch_dict会根据语料变化
        path:str，是资源文件的路径
        storage_path:是存储中间得到的字典文件的路径
        deal_list:要处理的新闻文件名，这个变量作为属性，因为它记录了已经处理的语料名，在需要扩展时避免对同一文本进行重复处理
        '''
        f = open("./resource/一二级汉字表.txt", "r", encoding="gbk")
        self.states = list(f.read())
        f.close()
        self.transition = np.zeros([6763, 6764], dtype='int')
        self.ch_dic = {}  # key就是汉字
        self.pin_dic = {}
        self.deal_list = deal_list
        # 这个将要存的就是经过处理的新闻
        self.pattern = '[^\u4e00-\u9fff]+'  # 用此正则表达式处理新闻
        self.path = "./resource/"
        self.storage_path = "./data/"

    def get_dic(self):
        '''
        得到pin_dict和pin_dic
        dict都是用pickle序列化得到的文件，文件名由下面的filename给出，如果此文件已存在，那么加载，否则创建字典，并且序列化保存到filename中
        '''

        filename = "./data/pin_dic.txt"
        if isfile(filename):
            with open(filename, "rb") as rf:
                self.pin_dic = pickle.load(rf)
        else:
            with open("./resource/拼音汉字表.txt", "r", encoding="gbk") as f:
                input = f.readlines()
                for line in input:
                    line_list = line.split()
                    pinyin = line_list[0]
                    line_list.pop(0)
                    self.pin_dic[pinyin] = line_list
                with open(filename, "wb") as wf:
                    pickle.dump(self.pin_dic, wf)
        filename = "./data/ch_dic.txt"
        filename_f = "./data/ch_dic_frequency.txt"
        if isfile(filename_f):
            with open(filename_f, "rb") as rf:
                self.ch_dic = pickle.load(rf)
        elif isfile(filename):
            with open(filename, "rb") as rf:
                self.ch_dic = pickle.load(rf)
        else:
            for i in range(len(self.states)):
                self.ch_dic[self.states[i]] = Chinese_character(self.states[i], i)  # 初步创立了字典
                with open(filename, "wb") as wf:  # 这里写入不含拼音的dic，逻辑上还是没什么问题
                    pickle.dump(self.ch_dic, wf)


    def dump(self):
        selfname = "./data/analyzer.txt"
        with open(selfname, "wb") as wf:
            pickle.dump(self, wf)
    
    
    def deal_plain_text(self, file):
        '''
        类似于deal_news，但是file就是一个文本，而不是很多新闻，处理起来类似于仅仅只处理一则新闻，而且也没有dump到文件中(没有持久化)
        '''
        filename = self.path + file  # file是Pickle得到的
        # 这个会不会浪费时间
        f = open(filename, "r", encoding="gbk")
        text = f.readlines()
        f.close()
        for index in range(len(text) - 1):
            ch = text[index]
            if not (ch in self.ch_dic):
                continue
            next_ch = text[index + 1]
            if next_ch in self.ch_dic:
                self.transition[self.ch_dic[ch].rank, self.ch_dic[next_ch].rank] += 1
            else:
                self.transition[self.ch_dic[ch].rank, 6763] += 1
    
    
    def deal_news(self, file):
        '''
        我们确保调用这个函数的时候，新闻一定是没有被处理过的
        读取文件中的新闻(有多个新闻，每则新闻是一行，而且是json格式的)，根据这些新闻修改ch_dict和转移矩阵，而且dump到文件中
        文件中不在字典中的字不予以考虑
        也没有特别处理第一个字的情况
        Parameters
        ----------
        file : str
            新闻文件的名字
        '''
        filename = self.path + file  # file是Pickle得到的
        f = open(filename, "r", encoding="gbk")
        text = f.readlines()
        f.close()
        for news in text:  # re处理在里面进行，这是一则新闻
            try:
                news_text = json.loads(news)['html']
                for index in range(len(news_text) - 1):  # -1是因为index+1
                    ch = news_text[index]
                    if not (ch in self.ch_dic):
                        continue
                    next_ch = news_text[index + 1]
                    if next_ch in self.ch_dic:
                        self.transition[self.ch_dic[ch].rank, self.ch_dic[next_ch].rank] += 1
                    else:
                        self.transition[self.ch_dic[ch].rank, 6763] += 1
            except:
                # print("skip")
                pass
        print("{} finish".format(file))
    
    
    def get_frequency(self):
        '''
        由转移表更新ch_dic每个字的频率
        有不准确之处，就是每个新闻的第一个字未考虑
        在每次更新材料后调用
        '''
        frequency = self.transition.sum(axis=1)
        for i in range(len(frequency)):
            self.ch_dic[self.states[i]].frequency = frequency[i]
    
    
    def routine(self):
        '''
        调用例程：首先是初始化字典，然后处理新闻，然后保存持久化
        '''
        self.get_dic()
        for item in self.deal_list:
            self.deal_news(item)
        self.get_frequency()
        self.dump()
    
    def expand(self, deal_list):
        '''
        处理deal_list中未被处理过的新闻名，并更新频率字典ch_dic

        Parameters
        ----------
        deal_list : list of str
            要扩展的新闻列表
        '''
        flag = False
        for item in deal_list:
            if not item in self.deal_list:
                self.deal_plain_text(item)
                self.deal_list.append(item)
                flag = True
        if (flag):
            self.get_frequency()
            self.dump()


class Viterbi:
    '''目前看来处理得不好，本来完全没有必要写成一个类，一个大函数就可'''
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.T1 = [] # T1,T2的每一列由于候选字数的不同(列长为候选字数)，并不是等长的，不是一个矩阵
        self.T2 = []
        self.observations = [] # 拼音列表
        self.candidate = [] # 似乎是，一个二维列表，candidate[i]表示的第i个拼音，有哪些对应的候选字
        self.rows = 6763  # 总的汉字字数
        self.cols = 0 # 拼音数
        self.res = []
        self.pinyin_sentence = ""

    def fill_table(self, sentence):
        '''是维特比算法填表这一部分，填T1和T2表'''
        self.reset(sentence)
        self.observations = self.pinyin_sentence.split()
        self.cols = len(self.observations)  # 就是输入的拼音数
        self.candidate.append(self.analyzer.pin_dic[self.observations[0]])
        self.T1.append([1] * len(self.candidate[0])) # 但是这里T1的第一列感觉不对，应该是字频
        self.T2.append([0] * len(self.candidate[0]))
        for i in range(1, self.cols):
            self.candidate.append(self.analyzer.pin_dic[self.observations[i]])
            self.T1.append([]) # 其实T1,T2本可以是定长列表，会省一些时间，不过这本来也不是效率的瓶颈
            self.T2.append([])
            for j in range(len(self.candidate[i])):
                # 计算T1,T2表的第j列
                last_len = len(self.T1[i - 1])
                count_p = np.zeros(last_len) # 
                for k in range(last_len):
                    count_p[k] = self.T1[i - 1][k] * self.analyzer.transition[
                        self.analyzer.ch_dic[self.candidate[i - 1][k]].rank, self.analyzer.ch_dic[
                            self.candidate[i][j]].rank]
                self.T1[i].append(np.max(count_p))
                self.T2[i].append(np.argmax(count_p))

    def backtrace(self):
        '''是维特比算法回溯这一部分，T1和T2表在fill_table中已经填好'''
        # 现在希望输出状态
        last_state = np.argmax(self.T1[self.cols - 1])
        self.res = []
        for i in range(self.cols - 1, -1, -1): # res倒过来添加的，最后再翻转
            self.res.append(last_state)
            last_state = self.T2[i][last_state]
        self.res = list(reversed(self.res))

    def get_res(self):
        '''返回字符串'''
        ans_str = ""
        for i in range(self.cols):
            ans_str += self.analyzer.pin_dic[self.observations[i]][self.res[i]]
        return ans_str

    def reset(self, sentence):
        '''
        会清空T1和T2，以及candidate，其实这个比较类似于析构函数，清空了一切
        '''
        self.T1 = []
        self.T2 = []
        self.observations = []
        self.candidate = []
        self.cols = 0
        self.res = []
        self.pinyin_sentence = sentence

    def routine(self, sentence):
        '''这个函数是外部调用接口，接受一句拼音，返回字符串'''
        self.reset(sentence)
        self.fill_table(sentence)
        self.backtrace()
        return self.getRes__()


def deal_test_in(input_path, output_path):
    '''处理样例，将正确答案输出到一个文件，错误答案输出到另一个文件'''
    fin = open(input_path, "r")
    test_in = fin.readlines()
    fout_mine = open(output_path, "w") # 输出的文件指针
    for index in range(len(test_in)):
        ans = viterbi.routine(test_in[index].lower().replace('qv', 'qu').replace('xv', 'xu')) # 因为给的标准输入与拼音表的拼音不一致，因此在调用函数前需要先处理 
        fout_mine.write(ans + '\n')
    fout_mine.close()
    fin.close()


def report_right_percentage(output_path):
    '''分别给出单字正确率和整句正确率'''
    fout_right = open(output_path.replace('mine', 'right'), "r")
    fout_mine = open(output_path, "r")
    re_exp = '[^\u4e00-\u9fff]+' # 为了去除汉字以外的字
    # 以下是求单字正确率
    text_right = re.sub(re_exp, '', fout_right.read()) 
    text_mine = re.sub(re_exp, '', fout_mine.read())
    sum = len(text_mine)
    right = 0 # 从这开始的4行，完全可以用sum(text_right==text_mine)替换
    for index in range(sum):
        if (text_right[index] == text_mine[index]):
            right += 1
    # 以下是求单句正确率
    fout_mine.seek(0, 0)
    fout_right.seek(0, 0)
    text_right_list = fout_right.readlines()
    text_mine_list = fout_mine.readlines()
    right_s = 0
    sentence_num = len(text_mine_list)
    # 以下可以用3行搞定，列表生成式用于去汉字，以及上一个注释那样求相同的
    for index in range(sentence_num):
        text_right_s = re.sub(re_exp, '', text_right_list[index])
        text_mine_s = re.sub(re_exp, '', text_mine_list[index])
        if (text_right_s == text_mine_s):
            right_s += 1
    # 输出结果
    print('字正确率：{:.2%}，整句正确率：{:.2%}'.format(right / sum, right_s / sentence_num))
    fout_right.close()
    fout_mine.close()


if __name__ == "__main__":
    selfname = "./data/analyzer.txt"
    if isfile(selfname):
        with open(selfname, "rb") as rf:
            analyzer = pickle.load(rf)
    else:
        num_list = [2, 4, 5, 6, 7, 8, 9, 10, 11]
        news_list = ["2016-{:0>2d}.txt".format(i) for i in num_list]
        analyzer = Analyzer(news_list)
        analyzer.routine()
    viterbi = Viterbi(analyzer)
    # viterbi.analyzer.transition=viterbi.analyzer.transition.astype('float')+0.3
    args = sys.argv
    if (len(args) == 3):
        input = args[1]
        output = args[2]
    else:
        print("输入有误，请给出输入和输出的绝对路径")
    deal_test_in(input, output)
