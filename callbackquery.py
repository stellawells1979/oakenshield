


'''
y
'''


import json
from database import sql
from utils.account import account
from utils.rules import Rules
from utils.command import command
from utils import timestand
from utils.search import Search

import logging
from logmanage import DailyLogManager

log = DailyLogManager('CallbackQuery', logging.WARNING, logging.INFO)

class CallbackQuery:
    '''
    r
    '''

    def __init__(self, bot, data):

        '''
        :param bot:
        :param data:
        :var self.inline_keyboard 请求对象中的键盘
        :var self.account 机器的信息集，包含了机器人的全部信息，可能会由其它方法初始化
        :var self.bot 机器人的别名，从 self.account 属性提取
        :var self.bot_title 机器人标题，以粗体字显示在消息顶部（一般应用于个人聊天）
        :var self.user_id 用户 ID，通常是从某个消息中提取，可能会由其它方法初始化
        :var self.chat_id 聊天的标识答，可能会由其它方法初始化
        :var self.method 向 telegram bot api 发起请求时使用的方法
        :var self.inline_keyboard 请求对象中的键盘
        :var self.send_text 请求对象中的文本

        :var self.predefined_entities 向 telegram 请求消息中的富文本对象，这只是个草稿对象，最终需
            要调用 toolbox 工具箱中的 format_entities 方法将其格式化成合法的 telegram entitie 对象
        :var self.send_data list 一个负责收集请求对象的请求容器，由各方法生成的添加对象添加到此容器，最终返回这个容器
        '''
        self.bot = bot
        self.bot_id = account.attribute(bot, 'id')
        self.bot_title = account.attribute(bot, 'title')['text']

        data = data.get('callback_query')
        self.callback_query_id = data.get('id')
        self.user_id = data.get('from', {}).get('id')
        self.user_name = data.get('from', {}).get('username')
        self.first_name = data.get('from', {}).get('first_name')
        self.last_name = data.get('from', {}).get('last_name')
        self.date = data.get('date')
        self.message_time = timestand.format_datetime(self.date)

        self.chat_id = data.get('message').get('chat').get('id')
        self.chat_title = data.get('message').get('chat', {}).get('title')
        self.chat_type = data.get('message').get('chat', {}).get('type')
        self.message_id = data.get('message', {}).get('message_id')

        self.reply_to = {}
        self.send_file = None
        self.send_data = []
        self.entity = []

        self.entity = account.attribute(bot, 'title')['entities']

        self.callback_data = self.parse_callback_data(data.get('data'))

        self.callback_type = self.callback_data[0]

        if self.chat_type == 'private':
            # 从数据库获取与用户的交互信息
            query = (f"INSERT INTO `{sql.table_interact}` (`bot`,`user`,`exchange`) VALUES (%s,%s,%s)"
                     f"ON DUPLICATE KEY UPDATE `exchange`=%s, edited=NOW()")
            sql.query(sql.database, query, [self.bot, self.user_id, self.message_id, self.message_id])

    def callback_message(self):
        '''
        :return:
        '''
        if self.callback_type in ['help', 'start', 'add']:
            result = command.command_main(self.bot, f'/{self.callback_type}', self.user_id, self.message_id)
            self.send_data.append([
                'editMessageText',
                {
                    'chat_id': self.chat_id,
                    'message_id': self.message_id,
                    **result
                },
                None
            ])

        elif self.callback_type == 'verify' and self.bot == 'rules':

            if self.parse_verify():
                query = f'SELECT verify FROM restriction WHERE bot=%s and chat=%s'
                query = sql.query(sql.database, query, [self.bot_id, self.chat_id])

                if query and query[0]:
                    verify_data = json.loads(query[0].get('verify'))
                    del verify_data[self.user_id]
                    query = f'UPDATE {sql.table_constra} SET verify=%s,edited=NOW() WHERE bot=%s and chat=%s'
                    sql.query(sql.database, query, [verify_data, self.bot_id, self.chat_id])

        elif self.callback_type in ['rules'] and self.bot == 'rules':

            return Rules(self.chat_id, self.user_id, self.callback_data, self.message_id).maintenance()


        elif self.callback_type in ['SP', 'ST', 'SG'] and self.bot == 'search':
            # SP 来自个人聊天的搜索，ST 来自个人聊天的分类搜索，SG 来自群组聊天的搜索
            if self.chat_type == 'supergroup' and int(self.callback_data[4]) != self.user_id:
                self.send_data.append([
                    'answerCallbackQuery',
                    {
                        'callback_query_id': self.callback_query_id,
                        'message_id': self.message_id,
                        'show_alert': False,
                        'text': '你无法操作别人的搜索记录'
                    },
                    None
                ])
            else:
                result = Search(self.user_id, self.callback_data).search_main()
                self.send_data.append([
                    'editMessageText',
                    {
                        'chat_id': self.chat_id,
                        'message_id': self.message_id,
                        'disable_web_page_preview': True,
                        **result
                    },
                    None
                ])

        return self.send_data

    def parse_verify(self):
        '''

        :return:
        '''
        result = True

        verify_answer = self.callback_data[1]
        verify_user_id = self.callback_data[2]
        if self.user_id != verify_user_id:
            self.send_data.append([
                'answerCallbackQuery',
                {
                    'callback_query_id': self.callback_query_id,
                    'message_id': self.message_id,
                    'show_alert': False,
                    'text': '这不是你的验证信息'
                },
                None
            ])
            result = False

        elif verify_answer == 'Y':
            self.entity.append({'type': 'bold', 'text': self.first_name})
            self.entity.append({'type': 'text_mention', 'text': self.first_name, 'user': {'id': self.user_id}})
            self.send_data.append([
                'sendMessage',
                {
                    'chat_id': self.chat_id,
                    'text': f'{self.first_name} 你已通过人机验证，欢迎加入【{self.chat_title}】'
                },
                {'delete': timestand.unix() + 20}
            ])
            self.send_data.append([
                'restrictChatMember',
                {
                    'chat_id': self.chat_id,
                    'user_id': self.user_id,
                    'permissions': {
                        'can_send_messages': True,
                        'can_send_audios': True,
                        'can_send_documents': True,
                        'can_send_photos': True,
                        'can_send_videos': True,
                        'can_send_video_notes': True,
                        'can_send_voice_notes': True,
                        'can_send_polls': True,
                        'can_send_other_messages': True,
                        'can_add_web_page_previews': True,
                        'can_change_info': True,
                        'can_invite_users': True,
                        'can_pin_messages': True,
                        'can_manage_topics': True,
                    }
                },
                None
            ])
        elif verify_answer == 'N':
            self.entity.append({'type': 'bold', 'text': self.first_name})
            self.entity.append({'type': 'text_mention', 'text': self.first_name, 'user': {'id': self.user_id}})
            self.send_data.append([
                'sendMessageText',
                {'chat_id': self.chat_id, 'text': f'{self.first_name} 验证失败，你将被请出群聊'},
                None
            ])
            self.send_data.append([
                'kickChatMember',
                {'chat_id': self.chat_id, 'user_id': self.user_id},
                {'delay': timestand.unix() + 5}     # 此消息延迟5秒发送
            ])

        return result

    @classmethod
    def parse_callback_data(cls, char):
        '''
        解析callback_data参数
        左一次右三次拆分字串，以避免被混淆的分隔影响
        :return:
        '''

        first, rest = char.split('|', 1)
        second, third, fourth, fifth = rest.rsplit('|', 3)
        return first, second, third, fourth, fifth


if __name__ == '__main__':

    from test import debugging
    temp = CallbackQuery('search', debugging.callablequery_14).callback_message()
    print(temp)







