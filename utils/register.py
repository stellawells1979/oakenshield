

'''
管理算什么消息
'''
import uuid
import json
from datetime import datetime

import run_config
from database import sql
import logging
from logmanage import DailyLogManager

log = DailyLogManager('Register', logging.ERROR, logging.INFO)


class Register:

    '''
    r
    '''

    def __init__(self, register_table):
        '''

        :param register_table: 目标签到数据表
        '''
        self.table = register_table
        query = f'SHOW COLUMNS FROM {sql.base_database}.{self.table}'
        self.table_fileds = sql.querys(sql.base_database, query, None)





    def create_register(self, affiliated, crator, kwargs):
        '''
        在数据库中创建一个签到实例
        :param affiliated:
        :param crator:
        :param kwargs:
        :return:
        '''

        values = [uuid.uuid4(), affiliated, crator, *kwargs]
        for row in self.table_fileds:
            field = row.get('Field')
            if field in ['created', 'edited']:
                values.append(run_config.now_time)
            elif field not in ['id', 'chat', 'creator', 'period', 'explains', 'status']:
                values.append(None)

        fields = list(self.table_fileds.keys())
        query = f'INSERT INTO `{",".join(fields)}` VALUES ({",".join(["%s"]*len(fields))})'
        return sql.querys(sql.base_database, query, values)

    def apply_register(self, chat, user, register_time):
        '''
        应用签到规则
        1. 签到数据表储存了签到规则的必要参数和每个签到日期的用户签到数据，总共储存了31天的签到数据，每个签到日期字段如 RE_1 到 RE_31
        2. 每个签到日期中的签到数据都是一个 dict，以 user_id 为键，值则是一个 list，这个 list 储存了用户在当前签到日期中的签到时间，
            因为有的用户会重复签到，设置一个 list 储存用户当日的所有签到时间，以防恶意签到
        :param chat: 目标群组 ID
        :param user:
        :param register_time: 签到日期
        :return:
        '''

        try:
            query = f"SELECT * FROM `{self.table}` WHERE chat = %s"
            query = sql.querys(sql.base_database, query, [chat])[0]
        except Exception as e:
            log.info(f'apply_register: {e}')
            return None

        # 用签到的起始时间和签到时间计算出现在是第几天签到
        register_date = self.calculate_date(query['created'], register_time)

        # 如果签到日期超出签到周期，则返回空值
        if register_date < 1 or register_date > query['period']:
            return None

        register_ID = query['id']
        register_file = f'RE_{register_date}'   # 拼接出当前签到日期的数据表字段

        # 序列化当前签到日期的签到数据，如果没有数据，则是个空字典
        register_data = json.loads(query[register_file]) if query.get(register_file) else {}

        text = '恭喜签到成功'

        if str(user) in register_data:
            # 如果当前用户已经有签到记录，则计算用户的签到次数次，超过3次的将视为恶意签到，否则提示用户不要重复签到
            user_register = register_data[str(user)]
            if len(user_register) > 3:
                text = '你已涉嫌恶意签到，'
                register_data = None
            elif len(user_register) > 0:
                text = '请勿重复签到'
                user_register.append(register_time)
        else:
            register_data.update({user: [register_time]})

        if register_data:
            query = f"UPDATE `{self.table}` SET `{register_file}`=%s,edited=%s WHERE id='{register_ID}'"
            sql.querys(sql.base_database, query, [json.dumps(register_data), register_time])

        return text

    @classmethod
    def calculate_date(cls, old_date, new_date):
        """
        计算日期时间差
        :param old_date: 旧日期，可以是字符串或 datetime.datetime
        :param new_date: 新日期，可以是字符串或 datetime.datetime
        :return: 日期差值的天数
        """
        # 如果 old_date 是字符串，需要转为 datetime
        if isinstance(old_date, str):
            old_date = datetime.strptime(old_date, "%Y-%m-%d %H:%M:%S")

        # 如果 new_date 是字符串，同样需要转为 datetime
        if isinstance(new_date, str):
            new_date = datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S")

        # 计算日期差值
        return (new_date.date() - old_date.date()).days + 1

register = Register(sql.table_register)

if __name__ == '__main__':
    register = Register('register')
    temp = register.apply_register(-1003606614850, 8598030336, run_config.now_time)
    print(temp)


       




