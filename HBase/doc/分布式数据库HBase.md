## 1.HBase介绍

Apache HBase是 Hadoop 数据库，是一个分布式、可伸缩、大数据存储区。当您需要随机、实时读/写访问大数据时，请使用 Apache HBase。 Apache HBase是一个开源的、分布式的、版本化的、非关系的数据库，它参考了 Google 的Bigtable。 正如 Bigtable 利用 Google 文件系统提供的分布式数据存储一样，Apache HBase 在 Hadoop 和 HDFS 之上提供了类似 Bigtable 的功能。

**定义**：HBase 是 Hadoop Database，是一个高可靠性、高性能、面向列、可伸缩、实时读写的分布式 NOSQL 数据库。

**作用**：主要用来存储非结构化、半结构化和结构化的松散数据（列式存储的 NoSQL 数据库）

### 1.1  **HBase数据模型**

逻辑上，HBase 的数据模型同关系型数据库很类似，数据存储在一张表中，有行有列。但从底层物理存储结构（Key-Value）来看，HBase 更像一个 Map。

HBase的逻辑结构如下：![hbase逻辑结构](.\img\hbase逻辑结构.jpg)

HBase的物理结构存储如下：

![](J:\工作资料\Python大数据课程\单独录制视频\05-HBase\03-笔记\img\HBase物理结构.jpg)

### 1.2 名称解释



1. NameSpace
   命名空间，相当于关系型数据库中的 database，每个命名空间下有多个表。Hbase 默认自带的命名空间 hbase 和 default；hbase 中存放的是 HBase 内置的表，default 是用户默认使用的命名空间。

2. Region
    类似关系型数据库的表，不同之处在于 HBase 定义表示只需要声明列族，不需要声明具体的列。列可以动态的按需要指定；HBase 更加适合字段经常变更的场景。开始创建表是一个表对应一个 region，当表增大到一定值是会被拆分为两个 region。
3. Row
    HBase 表中的每行数据被称为 Row，由一个 RowKey 和多个 Column 组成，数据是按照 RowKey 的字典顺序存储的，并且查询是只能根据 RowKey 进行检索，所以 RowKey 的设计很关键。
4. Column
    列是由列族（Column Family）和列限定符（Column Qualifier）进行限定，例如：
    base:name,base:sex。建表示只需定义列族，而列限定符无需预先定义。
5. Cell
    某行中的某一列被称为 Cell（单元格），由{rowkey，column family:columnqualifier,timestamp}确定单元。Cell 中没有具体的类型，全部是字节码的形式（字节数组）存储。
6. TimeStamp
    用于标识数据的不同版本（version），每条数据写入时，如果不指定时间戳，系统会自动为其加上该字段，值为写入 HBase 的时间。

## 2. HBase架构

### 2.1 HBase 架构

![](.\img\HBase架构.jpg)

- client

```
1) 包含访问HBase的接口，对HBase进行访问
2) 客户端通过查询zookeeper中信息获取HBase集群信息。
```

- zookeeper

```
1) 保证任何时候，集群中只有一个master
2) 存贮所有Region的寻址入口。
3) 实时监控RegionServer的上线和下线信息,并实时通知HMaster。
4) 存储HBase的Schema和table元数据
```

- Master

```
1) 为RegionServer分配Region
2) 负责RegionServer的负载均衡
3) 发现失效的RegionServer并重新分配其上的region
4) 管理用户对table的增删改操作
```

- RegionServer

```
1) RegionServer维护region，处理对这些Region的IO请求
2) RegionServer负责切分在运行过程中变得过大的Region　
```

- HLog(WAL Log)

```
1) HLog文件就是一个普通的Hadoop Sequence File，Sequence File的Key是HLogKey对象，HLogKey中记录了写入数据的归属信息，除了table和region名字外，同时还包括sequence number和timestamp，timestamp是"写入时间"，sequence number的起始值为0，或者是最近一次存入文件系 统中sequence number。
2) HLog SequeceFile的Value是HBase的KeyValue对象，即对应HFile中的KeyValue。
```

- Region

```
1） HBase自动把表水平划分成多个区域(region)，每个region会保存一个表里面某段连续的数据；每个表一开始只有一个region，随着数据不断插入表，Region不断增大，当增大到一个阀值的时候，Region就会等分会两个新的Region（裂变）。
2） 当table中的行不断增多，就会有越来越多的Region。这样一张完整的表被保存在多个Regionserver上。
```

- Memstore&StoreFile

```
1) 一个region由多个store组成，一个store对应一个CF（列族）
2) Store包括位于内存中的memstore和位于磁盘的storefile。写操作先写入Memstore，当Memstore中的数据达到某个阈值,HRegionserver会启动flashcache进程写入storefile，每次写入形成单独的一个storefile
3) StoreFile是只读的，一旦创建后就不可以再修改。因此Hbase的更新其实是不断追加的操作。当一个Store中storefile文件的数量增长到一定阈值后，系统会进行合并（minor、 major compaction），在合并过程中会进行版本合并和删除工作（majar），将对同一个key的修改合并到一起，形成更大的storefile。
4) 当一个region所有storefile的大小和超过一定阈值后，会把当前的region分割为两个，并由hmaster分配到相应的regionserver服务器，实现负载均衡。
5) 客户端检索数据，先在memstore找，找不到再找storefile。
6） HRegion是HBase中分布式存储和负载均衡的最小单元。最小单元就表示不同的HRegion可以分布在不同的HRegionServer上。
7) HRegion由一个或者多个Store组成，每个store保存一个columns family。
8) 每个Strore又由一个memStore和0至多个StoreFile组成。
```

### 2.2 HBase写操作流程

 ![](.\img\HBase写数据流程.jpg)

> 步骤一、Client发送请求从Zookeeper中获取HMaster的地址及meta表所在的RegionServer地址，向HRegionServer发出写数据请求。
>
> 步骤二、数据被写入HRegion的MemStore，同时写入到HLog中。
>
> 步骤三、MemStore中的数据被Flush成一个StoreFile
>
> 步骤四、当MemStore达到阈值后把数据刷成一个storefile文件，当多个StoreFile文件达到一定的大小后，会触发Compact合并操作，当compact后，逐渐形成越来越大的storefile。
>
> 步骤五、StoreFile大小超过一定阈值后，触发Split操作，把当前HRegion Split成2个新的HRegion，父HRegion会下线，新Split出的2个子HRegion会被HMaster分配到相应的HRegionServer上，使得原先1个HRegion的压力得以分流到2个HRegion上。
>
> 步骤六、若MemStore中的数据有丢失，则可以从HLog上恢复。

### 2.3 HBase读操作流程

 ![](.\img\HBase读数据流程.jpg)

> 步骤一、client首先从zookeeper找到meta表的region的位置，然后读取meta表中的数据。而meta中又存储了用户表的region信息。
>
> 步骤二、根据namespace、表名和rowkey根据meta表中的数据找到写入数据对于的region信息
>
> 步骤三、找到对应的RegionServer,查找对应的Region，先从Memstore中找数据，如果没有再从StoreFile中读取数据。

### 2.4 HBase minor小合并和major大合并

![](J:/%E5%B7%A5%E4%BD%9C%E8%B5%84%E6%96%99/Python%E5%A4%A7%E6%95%B0%E6%8D%AE%E8%AF%BE%E7%A8%8B/%E5%8D%95%E7%8B%AC%E5%BD%95%E5%88%B6%E8%A7%86%E9%A2%91/05-HBase/03-%E7%AC%94%E8%AE%B0/img/HBase%E6%9E%B6%E6%9E%84.jpg)

当客户端向HBase中写入数据时，首先写入HLog和Memstore中，在一个Store中，当Memstore内存占满后，数据会写入磁盘形成一个新的数据存储文件（StoreFile），随着 memstore 的刷写会生成很多StoreFile,当一个store中的storefile达到一定的阈值后，就会进行一次合并，将对同一个key的修改合并到一起，形成一个大的storefile，当storefile的大小达到一定阈值后，又会对storefile进行split，划分为两个storefile。

由于对表的更新是不断追加的，合并时，需要访问store中全部的storefile和memstore，将它们按row key进行合并，由于storefile和memstore都是经过排序的，并且storefile带有内存中索引，合并的过程还是比较快的。

因为存储文件不可修改，HBase是无法通过移除某个键/值来简单的删除数据，而是对删除的数据做个删除标记，表明该数据已被删除，检索过程中，删除标记掩盖该数据，客户端读取不到该数据。

随着memstore中数据不断刷写到磁盘中，会产生越来越多的storeFile小文件，HBase内部通过将多个文件合并成一个较大的文件解决这一小文件问题，以上过程涉及两种合并，如下： 

**minor小合并**

minor 合并负责合并Store中的多个storeFile文件，当StoreFile文件数量达到hbase.hstore.compaction.min 值（默认值为3）时，将会合并成一个StoreFile大文件。这种合并主要是将多个小文件重写为数量较少的大文件，减少存储文件数量，因为StoreFile的每个文件都是经过归类的，所以合并速度很快，主要受磁盘IO性能影响。

**major大合并**

将一个region中的一个列簇(对应一个Store)的若干个经过minor合并后的大的StoreFile重写为一个新的StoreFile。而且major合并能扫描所有的键/值对，顺序重写全部数据，重写过程中会略过做了删除标记的数据。

### 2.5 HBase 目标表meta表

目录表 hbase:meta 作为HBase表存在，并从 hbase shell 的 list(类似 show tables)命令中过滤掉，但实际上是一个表，就像任何其他表一样。

hbase:meta 表（以前称为.META.），保有系统中所有 region 的列表。hbase:meta位置信息存储在 zookeeper 中，hbase:meta 表是所有查询的入口。

表结构如下：

```
key：
	region的key，结构为：[table],[region start key,end key],[region id]
values:
	info:regioninfo（当前region序列化的HRegionInfo实例）
	info:server（包含当前region的RegionServer的server:port）
	info:serverstartcode（包含当前region的RegionServer进程的开始时间）
```

当表正在拆分时，将创建另外两列，称为 info:splitA 和 info:splitB，这些列代表两个子 region， 这些列的值也是序列化的 HRegionInfo 实例。区域分割后，将删除此行。

```
a,,endkey
a,startkey,endkey
a,startkey,
```

空键用于表示表开始和表结束。具有空开始键的 region 是表中的第一个 region。如果某个 region 同时具有空开始和空结束键，则它是表中唯一的 region。

## 3. HBase集群搭建与测试

### 3.1 HBase集群搭建

HBase搭建分为独立模式、伪分布式、完全分布式模式，实际上，在工作中使用HBase时都是完全分布式，所以这里我们搭建HBase的完全分布式模式。详细搭建步骤如下：

1) **下载HBase 2.2.6**

下载地址：[https://archive.apache.org/dist/hbase/2.2.6/](https://archive.apache.org/dist/hbase/2.2.6/)

![](.\img\下载HBase.jpg)

2) **规划HBase集群节点**

| **节点IP**     | **节点名称** | **HBase服务**        |
| -------------- | ------------ | -------------------- |
| 192.168.179.15 | mynode3      | RegionServer         |
| 192.168.179.16 | mynode4      | HMaster,RegionServer |
| 192.168.179.17 | mynode5      | RegionServer         |

 3) **将下载好的安装包发送到node4节点上,并解压,配置环境变量**

```
#将下载好的HBase安装包上传至node4节点/software下，并解压
[root@mynode4 software]# tar -zxvf ./hbase-2.2.6-bin.tar.gz
```

当前节点配置HBase环境变量

```
#配置HBase环境变量
[root@mysnode4 software]# vim /etc/profile
export HBASE_HOME=/software/hbase-2.2.6/
export PATH=$PATH:$HBASE_HOME/bin

#使环境变量生效
[root@mynode4 software]# source /etc/profile
```

4) **配置$HBASE_HOME/conf/hbase-env.sh**

```
#配置HBase JDK
export JAVA_HOME=/usr/java/jdk1.8.0_181-amd64/

#配置 HBase不使用自带的zookeeper
export HBASE_MANAGES_ZK=false
```

5) **配置$HBASE_HOME/conf/hbase-site.xml**

```
<configuration>
  <property>
        <name>hbase.rootdir</name>
        <value>hdfs://mycluster/hbase</value>
  </property>
  <property>
        <name>hbase.cluster.distributed</name>
        <value>true</value>
  </property>
  <property>
        <name>hbase.zookeeper.quorum</name>
        <value>mynode3,mynode4,mynode5</value>
  </property>
  <!-- 分布式环境设置下设置为false ，防止丢失数据 -->
  <property>
        <name>hbase.unsafe.stream.capability.enforce</name>
        <value>false</value>
  </property>
</configuration>
```

6) **配置$HBASE_HOME/conf/regionservers，配置RegionServer节点**

```
mynode3
mynode4
mynode5
```

7) **配置backup-masters文件**

手动创建$HBASE_HOME/conf/backup-masters文件，指定备用的HMaster,需要手动创建文件，这里写入mynode5,在HBase任意节点都可以启动HMaster，都可以成为备用Master ,可以使用命令：hbase-daemon.sh start master启动。

```
#创建 $HBASE_HOME/conf/backup-masters 文件，写入mynode5
[root@mynode4 conf]# vim backup-masters
mynode5
```

8) **复制hdfs-site.xml到$HBASE_HOME/conf/下**

```
[root@mynode4 conf]# cp /software/hadoop-3.1.4/etc/hadoop/hdfs-site.xml /software/hbase-2.2.6/conf/
```

9) **将HBase安装包发送到mynode3，mynode5节点上，并在mynode3，mynode5节点上配置HBase环境变量**

```
[root@mynode4 software]# cd /software
[root@mynode4 software]# scp -r ./hbase-2.6.2 mynode3:/software/
[root@mynode4 software]# scp -r ./hbase-2.6.2 mynode5:/software/

注意：在mynode3、mynode5上配置HBase环境变量。
```

### 3.2 HBase启动及访问

1）**启动Zookeeper、启动HDFS及启动HBase集群**

```
#启动Zookeeper
zkServer.sh start

#启动HDFS集群
[root@mynode1 software]# start-all.sh 

#启动HBase集群
[root@mynode4 software]# start-hbase.sh 
```

2) **访问HBase WebUI **

登录http://mynode4:16010访问HBase WebUI，如下图：![](.\img\HBase webui.jpg)

如果想要停止HBase集群，可以在**HMaster** 节点上执行"stop-hbase.sh"命令。

### 3.3 测试HBase高可用

目前mynode4为HMaster，在mynode4节点上找到“HMaster”进程进行kill,然后登录mynode5节点，在HBase WebUI中查看新的HMaster为mynode5。![](.\img\HBase MasterHA.jpg)

### 3.4 HBase 基本命令

HBase集群搭建完成之后，在任意一台HBase节点上可以登录HBase并进行操作。

- hbase shell：登录HBase

```
#hbase shell 可以在任意一台HBase节点登录HBase
[root@mynode3 software]# hbase shell
hbase(main):001:0>
```

- help ： 查看命令

```
hbase(main):001:0> help
  HBase Shell, version 2.2.6, r88c9a386176e2c2b5fd9915d0e9d3ce17d0e456e, Tue Sep 15     
  17:36:14 CST 2020
  Type 'help "COMMAND"', (e.g. 'help "get"' -- the quotes are necessary) for help on a   specific command.
  Commands are grouped. Type 'help "COMMAND_GROUP"', (e.g. 'help "general"') for help     on a command group
  ... ...

hbase(main):004:0> help "scan"
hbase> scan 'hbase:meta'
  hbase> scan 'hbase:meta', {COLUMNS => 'info:regioninfo'}
  hbase> scan 'ns1:t1', {COLUMNS => ['c1', 'c2'], LIMIT => 10, STARTROW => 'xyz'}
  hbase> scan 't1', {COLUMNS => ['c1', 'c2'], LIMIT => 10, STARTROW => 'xyz'}
  hbase> scan 't1', {COLUMNS => 'c1', TIMERANGE => [1303668804000, 1303668904000]}
  hbase> scan 't1', {REVERSED => true}
  hbase> scan 't1', {ALL_METRICS => true}

  ... ....


hbase(main):004:0> help "list"
  List all user tables in hbase. Optional regular expression parameter could
  be used to filter the output. Examples:

  hbase> list
  hbase> list 'abc.*'
  hbase> list 'ns:abc.*'
  hbase> list 'ns:.*'

```

- create ：创建HBase表

create的使用语法如下：create  '表名' ,'列族1' , '列族2'，使用如下：

```
#创建表 person，列族为cf
hbase(main):005:0> create 'person','cf'

```

- list： 查看HBase中的表

```
hbase(main):006:0> list
TABLE                                                                                                                                            
person 
```

- put : 向HBase表中插入数据

put向HBase表中插入数据语法：put  '表名' , 'rowkey' , '列族：列名' , '列对应的值'

```
hbase(main):008:0> put 'person','rowkey01','cf:name','zhangsan'
hbase(main):008:0> put 'person','rowkey01','cf:gender','m'
hbase(main):008:0> put 'person','rowkey01','cf:age','18'
hbase(main):008:0> put 'person','rowkey01','cf:score','100'
hbase(main):008:0> put 'person','rowkey02','cf:name','lisi'
hbase(main):008:0> put 'person','rowkey02','cf:gender','f'
hbase(main):008:0> put 'person','rowkey02','cf:age','20'
hbase(main):008:0> put 'person','rowkey02','cf:score','200'
```

- scan : 扫描表中的数据

scan语法为：scan '表名'，扫描表中的数据

```
#扫描表 person中的数据
hbase(main):017:0> scan 'person'
ROW                 COLUMN+CELL                                                          rowkey01           column=cf:age, timestamp=1638261775349, value=18                    rowkey01           column=cf:gender, timestamp=1638261775311, value=m                  rowkey01           column=cf:name, timestamp=1638261716730, value=zhangsan              rowkey01           column=cf:score, timestamp=1638261776022, value=100                  rowkey02           column=cf:age, timestamp=1638262031651, value=20                    rowkey02           column=cf:gender, timestamp=1638262031607, value=f                  rowkey02           column=cf:name, timestamp=1638262031567, value=lisi                  rowkey02           column=cf:score, timestamp=1638262032302, value=200            
```

- get : 获取某rowkey对应的数据

get的语法如下：get  '表名' , 'rowkey'

```
hbase(main):013:0> get 'person','rowkey02'
COLUMN                    CELL                                                          cf:age                   timestamp=1638262031651, value=20                              cf:gender                timestamp=1638262031607, value=f                              cf:name                  timestamp=1638262031567, value=lisi                           cf:score                 timestamp=1638262032302, value=200     
```

- drop:删除某张表

drop 语法如下：drop '表名'

```
#在删除表之前首先将表禁用，语法如下
hbase(main):014:0> disable 'person'

#删除表 person
hbase(main):015:0> drop 'person'

#查看表
hbase(main):016:0> list

```

- quit ： 退出hbase

```
#退出HBase
hbase(main):030:0> quit
```

## 4 HBase特点

HBase具备以下特点：

1. 强大的一致读/写：HBase 不是“最终一致”的 DataStore。它非常适合高速计数器聚合等任务。
2. 自动分片：HBase 表通过 region 分布在群集上，并且随着数据的增长，region 会自动分割和重新分配。自动的 RegionServer 故障转移。
3. Hadoop/HDFS 集成：HBase 支持 HDFS 作为其分布式文件系统。
4. MapReduce：HBase 支持通过 MapReduce 进行大规模并行处理，将 HBase 当做数据来源和保存数据存储的数据库。
5. Java 客户端 API：HBase 支持易于使用的 Java API 以进行编程访问。
6. Thrift/REST API：HBase 还支持非 Java 前端的 Thrift 和 REST。
7. 块缓存和布隆过滤器：HBase 支持块缓存和布隆过滤器，以实现大容量查询优化。
8. 运维管理：HBase 提供内置网页，用于运维监控和 JMX 指标。
9. HBase 不支持行间事务。

## 5 HBase Python API

HBase是由Java写的，原生的支持Java接口，对python人员不友好，那么针对这种情况，HBase提供了thrift接口服务器，可以采用其他语言编写HBase代码通过thrift接口连接操作HBase。

启动HBase Thrift服务的方式如下：

```
#在HBase任意一台节点上启动Thrift服务器
[root@mynode3 bin]# cd /software/hbase-2.2.6/bin
[root@mynode3 bin]# hbase-daemon.sh start thrift
```

#### 5.1 准备环境

在编写HBase代码客户端安装python依赖包，这里使用IDEA或者Pycharm编写python代码，那么就是在对应使用的python环境中安装依赖包：

```
#在使用python环境中安装如下两个依赖包
pip install thrift
pip install hbase-thrift
```

这里我使用IDEA 编写Python代码，对应的python在“D:\ProgramData\Anaconda3\envs\python37”,在Window中对应的python路径中安装对应的两个依赖包：

```
D:\ProgramData\Anaconda3\envs\python37\Scripts>pip install  thrift
D:\ProgramData\Anaconda3\envs\python37\Scripts>pip install hbase-thrift
```

由于这里使用python3版本，安装的hbase-thrift对于python3有一些不兼容，需要替换2个python文件，这个文件名字为：“Hbase.py”和“ttypes.py”，分别将以上两个文件替换到$PYTHON_HOME/Lib/site-packages/hbase下。

#### 5.2编写Python HBase代码

- 创建链接

```python
# coding=utf-8
from hbase.ttypes import ColumnDescriptor, Mutation
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from hbase import Hbase

transport = TSocket.TSocket('mynode3', 9090)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Hbase.Client(protocol)
transport.open()

#后期使用完成transport对象后，可以关闭对象
transport.close()
```

- 创建表

```python
# 1.创建表，无返回值：createTable(tableName,columnFamilies)
cf1 = ColumnDescriptor("cf1")
cf2 = ColumnDescriptor("cf2")
client.createTable('students',[cf1,cf2])
```

- 获取所有表

```python
# 2.获取所有表：getTablesName()
all_tables = client.getTableNames()
print(all_tables)
```

- 向表中插入数据

```python
# 3.向表中插入数据:mutateRow(tableName,rowkey,mutations),tableName:表名称,mutations指的是多行数据
def put(cli,tbl,rowkey,columns):
    func = lambda k_v: Mutation(column=k_v[0], value=k_v[1])
    mutations = list(map(func, columns.items()))
    cli.mutateRow(tbl,rowkey,mutations)

put(client,"students","rowkey001",{"cf1:name":"zhangsan","cf1:age":"18","cf2:gender":"f","cf2:score":"100"})
put(client,"students","rowkey002",{"cf1:name":"lisi","cf1:age":"20","cf2:gender":"m","cf2:score":"200"})
put(client,"students","rowkey001",{"cf1:name":"wangwu","cf1:age":"20","cf2:gender":"m","cf2:score":"200"})
```

- 获取rowkey记录

```python
# 4.获取rowkey记录：getRow(tableName,rowkey)
t_row_results = client.getRow("students","rowkey001")
for row in t_row_results:
    print("rowkey:%s , columns = %s"%(row.row,row.columns))
```

- 删除记录

```python
# 5.删除记录 : deleteAll(tableName,rowkey,deleteCol): tableName:表名称，deleteCol:要删除的列族:列
client.deleteAll("students","rowkey001","cf1:name")
```

- 删除rowkey所有记录

```python
#6. 删除rowkey对应的记录：deleteAllRow(tableName,rowkey)
client.deleteAllRow("students","rowkey001")
```

- 启用表、禁用表

```python
#7. 启用表，无返回值：enabledTable(tableName)
client.enableTable('students')

#8. 禁用表，无返回值：disableTable(tableName)
client.disableTable('students')
```

- 验证表是否被启用

```python
#9. 验证表是否被启用，返回一个bool值:isTableEnabled(tableName)
print(client.isTableEnabled('students'))
```

- 删除表

```python
#10. 删除表，无返回值deleteTable(tableName)
client.deleteTable('students')
```