


'''
y
'''


import time
import json
from database import sql
from utils.bots import bots
from utils.rules import Rules
from utils.command import Command
import run_config
from utils.search import Search



class CallbackQuery:
    '''
    r
    '''

    def __init__(self, bot, data):
        '''


        :param bot:
        :param data:
        :var self.inline_keyboard 请求对象中的键盘
        :var self.bots 机器有信息集，包含了机器人的全部信息，可能会由其它方法初始化
        :var self.bot 机器人的别名，从 self.bots 属性提取
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
        self.bot_id = bots.attribute(bot, 'id')
        self.bot_title = bots.attribute(bot, 'title')['text']

        data = data.get('callback_query')
        self.callback_query_id = data.get('id')
        self.user_id = data.get('from', {}).get('id')
        self.user_name = data.get('from', {}).get('username')
        self.first_name = data.get('from', {}).get('first_name')
        self.last_name = data.get('from', {}).get('last_name')
        self.date = data.get('date')
        self.message_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.date))

        self.chat_id = data.get('message').get('chat').get('id')
        self.chat_title = data.get('message').get('chat', {}).get('title')
        self.chat_type = data.get('message').get('chat', {}).get('type')
        self.message_id = data.get('message', {}).get('message_id')


        self.reply_to = {}
        self.send_text = None
        self.send_file = None
        self.inline_keyboard = []
        self.method = None
        self.send_data = []
        self.predefined_entities = []


        self.predefined_entities = bots.attribute(bot, 'title')['entities']

        self.callback_data = data.get('data').split("|")

        self.callback_type = self.callback_data[0]

    def main(self):
        '''

        :return:
        '''
        if self.callback_type in ['help', 'start', 'add']:
            result = Command(self.bot).reply_command(f'/{self.callback_type}')
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

            if self.analysis_verify():
                query = f'SELECT verify FROM restriction WHERE bot=%s and chat=%s'
                query = sql.querys(sql.base_database, query, [self.bot_id, self.chat_id])

                if query and query[0]:
                    verify_data = json.loads(query[0].get('verify'))
                    del verify_data[self.user_id]
                    query = f'UPDATE {sql.table_restriction} SET verify=%s,edited=NOW() WHERE bot=%s and chat=%s'
                    sql.querys(sql.base_database, query, [verify_data, self.bot_id, self.chat_id])


        elif self.callback_type in ['rules'] and self.bot == 'rules':

            return Rules(self.chat_id, self.user_id, self.callback_data, self.message_id).main()

        elif self.callback_type in ['SP', 'ST', 'SG'] and self.bot == 'search':
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
                result = Search(self.user_id, self.callback_data).main()
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

    def analysis_verify(self):
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
            self.predefined_entities.append({'type': 'bold', 'text': self.first_name})
            self.predefined_entities.append({'type': 'text_mention', 'text': self.first_name, 'user': {'id': self.user_id}})
            self.send_data.append([
                'sendMessage',
                {
                    'chat_id': self.chat_id,
                    'text': f'{self.first_name} 你已通过人机验证，欢迎加入【{self.chat_title}】'
                },
                {'delete': run_config.date + 20}
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
            self.predefined_entities.append({'type': 'bold', 'text': self.first_name})
            self.predefined_entities.append({'type': 'text_mention', 'text': self.first_name, 'user': {'id': self.user_id}})
            self.send_data.append([
                'sendMessageText',
                {'chat_id': self.chat_id, 'text': f'{self.first_name} 验证失败，你将被请出群聊'},
                None
            ])
            self.send_data.append([
                'kickChatMember',
                {'chat_id': self.chat_id, 'user_id': self.user_id},
                {'delay': run_config.date + 5}     # 此消息延迟5秒发送
            ])

        return result


if __name__ == '__main__':
    from test import debugging

    telegram = CallbackQuery('rules', debugging.callbackquery_example_9.get('result')[0])
    tt = telegram.main()
    print(tt)










