# coding=utf-8
from hbase import Hbase
from hbase.ttypes import ColumnDescriptor, Mutation
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket

"""
Python API 操作HBase
"""
# 1. 创建连接HBase对象
transport = TSocket.TSocket("mynode3",9090)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Hbase.Client(protocol)
transport.open()

# 2.创建表
# cf1 = ColumnDescriptor("cf1")
# cf2 = ColumnDescriptor("cf2")
# client.createTable("students",[cf1,cf2])

#3. 向表中插入数据
# def put(cli,tbl,rowkey,columns):
#     func = lambda k_v: Mutation(column=k_v[0], value=k_v[1])
#     mutations = list(map(func, columns.items()))
#     cli.mutateRow(tbl,rowkey,mutations)
#
# put(client,"students","rowkey001",{"cf1:name":"zhangsan","cf1:age":"18","cf2:gender":"f","cf2:score":"100"})
# put(client,"students","rowkey002",{"cf1:name":"lisi","cf1:age":"20","cf2:gender":"m","cf2:score":"200"})
# put(client,"students","rowkey001",{"cf1:name":"wangwu","cf1:age":"18","cf2:gender":"f","cf2:score":"100"})

# 4.查询HBase中的表
# print(client.getTableNames())

# 5.获取rowKey记录
# t_row_results = client.getRow("students","rowkey001")
# # for one in t_row_results:
# #     print("rowkey = %s ,columns = %s"%(one.row,one.columns))

# 6.删除记录
# client.deleteAll("students","rowkey001","cf1:name")

#7.删除整个rowkey所有数据
# client.deleteAllRow("students","rowkey001")

#8. 查询表启用情况
# print(client.isTableEnabled("students"))

# 9.启动表、禁用表
# client.enableTable("students")
# client.disableTable("students")
# print(client.isTableEnabled("students"))

# 10.删除表
# client.deleteTable("students")

# transport.close()