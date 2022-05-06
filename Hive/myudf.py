import sys

'''
使用方法：
进入hive交互模式后，先将python文件添加至服务器，然后使用。详见：doc/11.自定义DUF函数使用1.png、12.自定义DFS函数使用2.png
'''

# 单列数据
for s in sys.stdin:
    if int(s) < 300:
        print('bad')
    else:
        print('good')

# 多列数据
for line in sys.stdin:
    detail = line.strip().split('\t')
    if len(detail) < 3:
        continue
    else:
        id = detail[0]
        name = detail[1]
        score = detail[2]
        if int(score) < 300:
            print('\t'.join([id, name, score, 'bad']))
        else:
            print('\t'.join([id, name, score, 'bad']))
