'''
聊天成员类
'''

import logging
from utils.quick import quick
from utils import timestand


from logmanage import DailyLogManager


log = DailyLogManager('Member', logging.ERROR, logging.INFO)


class ChatMember:
    '''
    聊天成员类。此类描述了聊天成员的行为和状态变化
    :return:
    '''
    def __init__(self, bot, data):

        self.bot = bot
        self.chat_id = data.get('chat', {}).get('id')

    def parse_chat_members(self, data):
        '''
        解析聊天成员数据
        :param data:
        :return:
        '''



class MychatMember:
    '''
    机器人在聊天中的状态变化
    :return:
    '''
    def __init__(self, bot, data):
        '''
        实例化基本参数，注意，如果是需要写入数据库的参数，其变量名必须与相应数据库表的字段名一致
        :param bot:
        :param data:
        '''
        data = data.get('my_chat_member', {})
        self.send_data = []
        self.bot = bot


        self.chat_id = data.get('chat', {}).get('id')
        self.chat_type = data.get('chat', {}).get('type')
        self.chat_title = data.get('chat', {}).get('title')
        self.title = data.get('chat', {}).get('title')
        self.name = data.get('chat', {}).get('username')
        self.type = data.get('chat', {}).get('type')

        self.initiator = data.get('from')
        self.date = data.get('date')
        self.message_time = timestand.format_datetime(self.date)

        self.origstatus = data.get('old_chat_member', {}).get('status')     # 机器人此前在群组中的状态
        self.bot_status = data.get('new_chat_member')     # 机器人当前在群组中的状态（管理员或成员）

    def main(self):
        '''

        :param self:
        :return:
        '''
        # 机器人在群组中的凓发生了变化，并将此变化详情记录到日志
        log.warning(f'This bot is {self.bot_status.get("status")} from {self.origstatus} in the {self.title}')


        quick.update_chat(self.bot, self.chat_id, self.chat_type, self.chat_title, self.bot_status)

        return self.send_data


if __name__ == '__main__':

    from test import debugging
    mychatmember = MychatMember('rules', debugging.my_chat_member_02).main()
