import heapq

from mrjob.job import MRJob, MRStep

'''
统计文件中单词出现次数最多的两个
PS D:\GZH\PycharmProjects\BigDataStudy\MapReduce> ..\..\..\..\Development\Anaconda3\envs\big_data\python.exe TopNWordCount.py test.txt
结果不对？
'''


class TopNWords(MRJob):
    def mapper(self, _, line_value):  # 参数名可以修改，但是参数个数不能变
        if line_value.strip() != '':
            for word in line_value.strip().split():
                yield word, 1

    # combiner 是介于mapper和reduce之间的聚合，可以把mapper输出的数据做一次临时的聚合来减少数据量
    def combiner_temp(self, word, values):  # 函数名也可以修改，但是需要在steps函数里配置
        yield word, sum(values)

    def reducer_sum(self, word, values):
        # 注：这里要把单词出现的次数放在前面，方便下一步使用heapq.nlargest，否则排序不正确
        yield None, (sum(values), word)  # 输出的key可以不要，把单词和单词出现的次数作为value

    # 实现TopN的排序和取值，排序采用Python标准库中的heapq
    def top_n_reducer(self, _, word_count):  # word_count是一个包含多个元组的迭代器
        for word, count in heapq.nlargest(2, word_count):  # nlargest的参数：第一个是个数，第二个是迭代器
            yield word, count

    # 实现steps函数，用于指定自定义的函数，
    def steps(self):
        return [
            # 一个MRStep代表一个完整的MapReduce过程，可以指定自己定义的函数
            MRStep(mapper=self.mapper, combiner=self.combiner_temp, reducer=self.reducer_sum),
            MRStep(reducer=self.top_n_reducer)
        ]


if __name__ == '__main__':
    TopNWords.run()
