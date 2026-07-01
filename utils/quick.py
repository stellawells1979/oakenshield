'''
此类集成了获取聊天信息的工具函数
'''

from utils.TGrequest import crave

import logging
from logmanage import DailyLogManager

log = DailyLogManager('ChatInfo', logging.WARNING, logging.INFO)

class ChatInfo:
    '''
    1
    '''

    def __init__(self, bot=None):
        '''

        '''
        self.bot = bot

    @classmethod
    def administrator(cls, bot, group):
        '''
        获取指定群组的管理员
        :param bot:
        :param group:
        :return:
        '''
        response = crave.send(bot, 'getChatAdministrators', {'chat_id': group})
        if response and response['ok']:
            return response['result']
        return []

    @classmethod
    def chat_member(cls, bot, group, user):
        '''
        获取聊天中某个成员的信息
        :param bot:
        :param group:
        :param user:
        :return:
        '''
        response = crave.send(bot, 'getChatMember', {'chat_id': group, 'user_id': user})
        if response:
            return response['result']

        return []

    @classmethod
    def chat_info(cls, bot, group):
        '''
        获取某个聊天的信息
        :param bot:
        :param group:
        :return:
        '''
        response = crave.send(bot, 'getChat', {'chat_id': group})
        if response:
            return response['result']
        return []

    @classmethod
    def get_chatmembercount(cls, bot, group):
        '''
        获取聊天中成员数量
        :param bot:
        :param group:
        :return: int
        '''
        response = crave.send(bot, 'getChatMemberCount', {'chat_id': group})
        if response:
            return response['result']

        return 0

quick = ChatInfo()

