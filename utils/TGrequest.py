


'''
与 telegram bot api 的通信模块
'''

import requests
import json

import config
from utils.account import account
import logging
from logmanage import DailyLogManager

log = DailyLogManager('TGrequest', logging.ERROR, logging.INFO)

class Request:
    '''
    m
    '''
    def __init__(self):
        '''
        :var self.base_url telegram bot api 的基础链接地址
        :var self.proxy 定义一个代理，确保在特殊网络环境下能够正常通信
        :var self.error_descriptions 收集中的 api 错误信息，
        '''
        self.base_url = 'https://api.telegram.org/bot'
        self.proxy = config.proxy
        self.tokens = {
            'rules': account.attribute('rules', 'token'),
            'search': account.attribute('search', 'token')
        }

        self.error_descriptions = {
            'Bad Request: chat not found': '无法找到指定的聊天，(chat_id)',

            'Bad Request: message to delete not found': '无法找到要删除的消息(message_id)',

            'Bad Request: message is not modified': '你传入的消息内容与之前的内容相同',

            'Bad Request: message is too long': '消息过长，Telegram 对消息长度有限制',

            'Bad Request: reply message not found': '无法找到回复的消息(reply_to_message_id)',

            'Bad Request: reply markup is not a valid inline keyboard': '回复标记不是有效的内联键盘',

            'Bad Request: file to send is empty': '要发送的文件为空',

            'Bad Request: message text is empty': '发送消息时，消息内容为空',

            'Bad Request: message text is missing': '发送消息时，消息内容缺失',

            'Bad Request: user not found': '无法找到指定的用户(user_id)',

            'Forbidden: bot was blocked by the use': '用户已屏蔽了你的机器人，无法向用户发送消息',

            'Forbidden: user is deactivated': '目标用户已停用其 Telegram 账户',

            'Forbidden: chat write forbidden': '机器人在该聊天中无法发送消息（可能被禁止）',

            'Circular reference detected': '检测到循环引用',

            'Not Found': '未找到，你应该检查 method',

            'Bad Request: message is not modified: specified new message content '
            'and reply markup are exactly the same as a current'
            ' content and reply markup of the message': '与上一条消息高度一致'

        }

    def send(self, bot, method, body=None, file=None):
        '''
        向 telegram bot api 请求任何响应
        :param bot: 机器人的唯一密钥，本实例被设计为调用多个机器人 token 获取相应的更新
        :param method: api 说法
        :param body: 向服务器请求的参数
        :param file: 此参数将携带一个文件上伟至客户端的某个聊天
        :return:
        '''

        token = self.tokens.get(bot)
        url = f'{self.base_url}{token}/{method}'
        try:
            if file:
                response = requests.post(url, data=body, files=file, proxies=self.proxy, timeout=10)
            else:
                response = requests.post(url, json=body, proxies=self.proxy, timeout=10)
            result = json.loads(response.text)
        except requests.exceptions.Timeout:
            result ={'ok': False, 'description': 'Request Timeout'}
        except requests.exceptions.ConnectionError as e:
            result = {'ok': False, 'description': 'Request ConnectionError'}
        except Exception as e:
            result = {'ok': False, 'description': f'Unkown: {e}'}

        return result

    def error(self, description):
        '''

        :param description:
        :return:
        '''

        return self.error_descriptions.get(description, description)

crave = Request()



if __name__ == '__main__':

    telegram = Request()



