#!python3
#coding=utf8
# print('hello, world!')
import re
import sys
import pandas as pd
import time
import json
import numpy as np
from  os.path import isfile, join,basename
from pypinyin import lazy_pinyin
from difflib import SequenceMatcher
# import sys

# -*- coding: utf-8 -*-

from pypinyin import pinyin, lazy_pinyin, Style
import jieba

def foobar(char):
    return 'fuck'

# A = open('answer.txt', 'r', encoding='gbk')
# I = open('input.txt', 'w')

# while True:
# line = A.readline()
line="今天的天气真好啊"
# if not line:
#     break
# I.write(+'\n')
# print(' '.join(lazy_pinyin(jieba.cut(line, cut_all=False), errors=foobar)))
# A.close()
# I.close()

# input="/Users/quebec/Documents/Program/py/hw1_pinyin/resource/test_news_1.txt"
# print(basename(input))
# with open(r"./resource/input.txt", "r") as f:
#     print(f.read())
# print(sys.argv)
# print(line)
print(sys.argv)