

'''
配置机器人，分别的搜索，规则，验证机器人
包括机器的的基本信息和开发者自定义的描述和行为
开发者应为各种功能机器定义一个独立文档或者函数，
'''

import config
import requests
import json
import logging
from logmanage import DailyLogManager



log = DailyLogManager('Telegram', logging.ERROR, logging.INFO)

class Account:
    '''
    初始化个人账号信息
    '''

    def __init__(self):
        '''
        机器人的基本信息
        '''
        self.base_url = 'https://api.telegram.org/bot'

        account_info = self.init_account()
        if not account_info:
            raise '没有获取到机器人信息'

        # 数据库配置参数
        self.host = account_info.get('host')
        self.port = int(account_info.get('port'))
        self.user = account_info.get('user')
        self.password = account_info.get('password')
        self.charset = 'utf8mb4'




        self.search = {
            'id': account_info.get('search').get('id'),
            'token': account_info.get('search').get('token'),
            'url': f"https://t.me/{account_info.get('search').get('username')}",
            'username': account_info.get('search').get('username'),
            'byname': account_info.get('search').get('by_name'),
            'title': {'text': '百搜机器人', 'entities': [{'type': 'bold', 'text': '百搜机器人'}, ]},
            'description': '百搜机器人，搜遍TG',
            'start_description': {
                'text': "搜群组,搜频道,搜影视,搜资讯,搜遍TG的搜索小能手",
                'entities': [
                    {'type': 'bold', 'text': '小能手'},
                ]
            },
            'help_description': {
                'text': '百搜机器人专注于收集和分享telegram群组链接，集百万个群组，可按你提供的关键字为你分享相关群组链'
                        '接，点击下面的【添加收录】按钮分享你的群组链接，让你的群组暴光率成倍提升,你也可以将我添加到你的群组,分享更多搜索乐趣',
                'entities': [
                    {'type': 'bold', 'text': '百搜机器人'},
                    {'type': 'bold', 'text': '添加收录'},
                ]
            },

        }

        self.rules = {
            'id': account_info.get('rules').get('id'),
            'token': account_info.get('rules').get('token'),
            'url': f"https://t.me/{account_info.get('rules').get('username')}",
            'username': account_info.get('rules').get('username'),
            'byname': account_info.get('rules').get('by_name'),
            'image': '',
            'title': {
                'text': '规则机器人',
                'entities': [
                    {'type': 'bold', 'text': '规则机器人'},
                ]
            },
            'description': '监控群组的每一个动静，按规则做出响应',
            'start_description': {
                'text': f"一个能在你的群组中24小时不间断监视群组活动的机器人，它没有作息时间，你可以设置任意规则来管理你的群组\n\n"
                        f"点击【帮助】了解如何使用本机器",
                'entities': [
                    {'type': 'bold', 'text': '帮助'},
                ]
            },
            'rules_description': {
                'text': f"欢迎使用规则机器人服务，在使用本服务前首先确认你是该群组的创建者或者管理员且拥有相应权限",
                'entities': [
                    {'type': 'bold', 'text': '帮助'},
                ]
            },
            'help_description': {
                'text': '1.首先确保你是某个群组的创建者或者管理员且有相应权限\n2.点击【添加机器人到群组】按钮并进入那个群'
                        '组\n3.在群组的用户列表中搜索找到本机器人，将机器人设为管理员并赋以相应权限\n4.向群里发送【hello wellwen】让机器'
                        '人找到你，稍等片刻机器人会回复一条信息把你带回本聊天或者你直接回到本聊天，即可进入规则设置界面',
                'entities': [
                    {'type': 'bold', 'text': '规则机器人'},
                    {'type': 'bold', 'text': '创建者或者管理员'},
                    {'type': 'bold', 'text': '添加机器人到群组'},
                    {'type': 'bold', 'text': '管理员并赋以相应权限'},
                    {'type': 'bold', 'text': 'hello wellwen'},
                ]
            },
        }

    def init_account(self):
        '''

        :return:
        '''
        with open(config.account_path, encoding='utf-8') as f:
            account_data = f.readlines()

        account_info = {}
        for row in account_data:
            row = row.replace(' ', '').strip()
            if not row:
                continue
            row = row.strip().split('=')
            if not row:
                continue

            if row[0] in ['rules_token', 'search_token']:
                url = f'{self.base_url}{row[1].strip()}/getMe'
                try:
                    response = requests.get(url, proxies=config.proxy, timeout=6)
                    if response.status_code == 200:
                        response = json.loads(response.text).get('result')
                        account_info.update({
                            row[0].split('_')[0]: {
                                'id': response.get('id'),
                                'username': response.get('username'),
                                'by_name': row[0].split('_')[0],
                                'last_name': response.get('last_name'),
                                'token': row[1],
                            }
                        })
                except Exception as e:
                    log.error(e)
            else:
                account_info.update({row[0].strip(): row[1].strip()})
        return account_info

    def attribute(self, bot, option=None):
        '''

        :param bot:
        :param option:
        :return:
        '''
        if not option:
            return self.__dict__.get(bot)

        return self.__dict__.get(bot, {}).get(option)

account = Account()

if __name__ == '__main__':

    print(account.attribute('search', 'title'))

