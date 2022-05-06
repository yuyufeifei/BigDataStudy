# 计算test.txt文件中，有多少字符、单词、行数
# PS D:\GZH\PycharmProjects\BigDataStudy\MapReduce> ..\..\..\..\Development\Anaconda3\envs\big_data\python.exe WordCount1.py test.txt > output1.txt
# 这种方式和hadoop集群没有关系，是本地运行
from mrjob.job import MRJob


class WordCount(MRJob):
    # mapper函数是一个自动循环递归调用，每行数据调用一次
    def mapper(self, key, value):   # key为该行数据在文件中的偏移量，value为该行的内容
        # print(key, value)  # 运行时需注释掉
        yield 'chars', len(value)   # 统计字符数
        yield 'words', len(value.split())   # 统计单词数
        yield 'lines', 1    # 行数

    # 也是循环调用的函数，每组数据调用一次
    def reducer(self, key, values):     # values：代表一组数据的所有值
        yield key, sum(values)

if __name__ == '__main__':
    WordCount.run()