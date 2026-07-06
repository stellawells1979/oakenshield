
'''
User 类
'''
import time
import json
import logging
from database import sql
from logg import LogManager

log = LogManager('User', logging.ERROR, logging.INFO)

class UserInfo:
    '''
    用户类
    '''
    def __init__(self, data):

        self.skip = []
        self.send_data = []

        self.id = data.get('id')
        self.type = data.get('type', {}).get('@type')
        self.username = data.get('usernames', {}).get('active_usernames', [None])[0]
        self.is_bot = data.get('is_bot')    # 是否为机器人
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.phone = data.get('phone_number')
        self.photo = data.get('profile_photo')
        self.status = data.get('status')

        self.contact = data.get('is_contact')    # 是否为联系人
        self.mutual = data.get('is_mutual_contact')    # 是否双向联系人
        self.premium = data.get('is_premium')    # 是否为高级用户
        self.new_chated = data.get('restricts_new_chats')   # 是否限制新聊天
        self.access = data.get('have_access')   # 是否能获取详细用户信息

        self.description = data.get('bio')
        self.called = data.get('can_be_called')  # 是否支持语音通话
        self.video_calls = data.get('can_be_called')  # 是否支持视频通话

        self.local_user = None


    def add_memuber(self):
        """
        :return:
        """









