from mrjob.job import MRJob

'''
把每个用户对应的订单及总金额列出来
user文件中存储了uid、user_name
order文件中存储了uid、orderid、order_price
'''


class UserAndOrderJoin(MRJob):
    def mapper(self, key, value):
        fields = value.strip().split()
        if len(fields) == 2:  # 用户数据
            source = 'U'
            user_id = fields[0]
            user_name = fields[1]
            yield user_id, [source, user_name]
        elif len(fields) == 3:  # 订单数据
            source = 'O'
            user_id = fields[0]
            order_id = fields[1]
            money = fields[2]
            yield user_id, [source, order_id, money]
            yield user_id, ['S', money]
        else:
            pass

    def reducer(self, key, values):
        '''
        重点：mapper后的数据，相同的key会进行一次reduce

        最终得到每个用户的订单列表和总金额
        "01:user1"	["01:80 02:90 05:55", 225]
        "02:user2"	["03:88 04:99", 187]
        "03:user3"	["", 0]

        :param key: 用户ID
        :param values: 列表，分两种类型。
        '''

        user_name = None
        order_list = ''
        money_sum = 0
        for v in values:
            if v[0] == 'U':
                user_name = v[1]
            elif v[0] == 'O':
                order_list = order_list + v[1] + ':' + v[2] + ' '
            elif v[0] == 'S':
                money_sum = money_sum + int(v[1])
        yield ':'.join([key, user_name]), (order_list.strip(), money_sum)


if __name__ == '__main__':
    UserAndOrderJoin.run()
