# input_method

### 代码需要的修改

- 对于汉字，有对应的拼音，我用了一个字典，用于转换，其实没必要，我觉得更好的写法是str.translate和str.maketrans。这样，逻辑中根本不需要字典，只需要矩阵，因为汉字不再以字符串的形式存在，而仅仅以数存在。这样逻辑会更清晰。因为每次看到rank和字的转换就感觉很烦
- 没有必要把Viterbi封装成一个类，这个算法并不复杂，其实一个函数足够了
- Viterbi算法的实现，T1的初始值不对，实现中初始化为1了，实际上应该是字频，不过这一点在改进中还会说到

### 算法需要的改进

- 从二元到三元，原理没啥变化，时间也没啥变化(目前是这样想的)，但是存储量变大了

- 有些字不可能作为第一个字，因此，建议直接来一个初始字的统计，对于最后一个字也是如此

本实现的优点是：简单，有详细的注释(不过Viterbi算法已经算是足够符合人的直观了，本来就没有什么难理解的地方)

### 实现

其实就是两步，预处理，以便得到Viterbi算法需要的3种概率，以及执行Viterbi算法

预处理极其简单，只有下面几行：

```python
for index in range(len(news_text) - 1):  # -1是因为index+1
    ch = news_text[index]
    if not (ch in self.ch_dic):
        continue
        next_ch = news_text[index + 1]
        if next_ch in self.ch_dic:
            self.transition[self.ch_dic[ch].rank, self.ch_dic[next_ch].rank] += 1
        else:
            self.transition[self.ch_dic[ch].rank, 6763] += 1
```

Viterbi算法看看[维特比算法]([https://zh.wikipedia.org/zh-hans/%E7%BB%B4%E7%89%B9%E6%AF%94%E7%AE%97%E6%B3%95](https://zh.wikipedia.org/zh-hans/维特比算法))即可

用于github搜索：HMM(隐马尔科夫模型) Viterbi(维特比算法)  拼音输入法

