
'''
关于机器人命令的所有功能在此类中定义
'''

from database import sql

from utils.toolbox import toolbox

from utils.account import account


class Command:

    '''
    应用机器人命令

    '''


    def __init__(self, bot):
        '''
        旨中响应用户的命令消息和解析用户使用 ADD 命脉后输入的收藏信息

        :var self.account 机器有信息集，包含了机器人的全部信息，可能会由其它方法初始化
        :var self.bot 机器人的别名，从 self.account 属性提取
        :var self.command 机器人接收到的带 / 符号的命令，可能会由其它方法初始化
        :var self.user_id 用户 ID，通常是从某个消息中提取，可能会由其它方法初始化
        :var self.chat_id 聊天的标识答，可能会由其它方法初始化
        :var self.method 向 telegram bot api 发起请求时使用的方法
        :var self.inline_keyboard 请求对象中的键盘
        :var self.send_text 请求对象中的文本
        :var self.predefined_entities 向 telegram 请求消息中的富文本对象，这个草稿对象，最终需
            要调用 toolbox 工具箱中的 format_entities 方法将其格式化成合法的 telegram entitie 对象

        '''
        self.bot = bot
        self.bots = account.attribute(bot)
        self.send_text = ''
        self.inline_keyboard = []
        self.predefined_entities = []

    def reply_command(self, bot_command):
        '''
        将机器人的开始命令应用到响应
        机器人需要记录与每个用户的交互状态，将这些信息写入 interact 数据表，
        :param bot_command: 机器人名
        :return:
        '''
        if bot_command == '/start':
            self.start()
        if bot_command == '/help':
            self.help()
        if bot_command == '/add':
            self.reply_collect()

        result = {
            'text': self.send_text,
            'reply_markup': {'inline_keyboard': self.inline_keyboard},
        }
        if self.predefined_entities:
            entities = toolbox.format_entities(self.send_text, self.predefined_entities)
            result.update({'entities': entities})

        return result

    def start(self):
        '''
        响应用户的 start 命令
        :return:
        '''
        self.send_text = self.bots['title']['text']
        self.send_text = f'{self.send_text}\n\n{self.bots["start_description"]["text"]}'
        self.predefined_entities = self.predefined_entities + self.bots['title']['entities']
        self.predefined_entities = self.predefined_entities + self.bots['start_description']['entities']
        if self.bot == 'rules':
            self.inline_keyboard = [

                [
                    {'text': '机器人定制', 'url': 'https://t.me/bigapple699'},
                    {'text': '开始使用机器人', 'callback_data': 'rules|prelude|0|0|0'}
                ],
                [
                    {'text': '添加到群组', 'url': f'{self.bots["url"]}?startgroup=true'},
                    {'text': '帮助', 'callback_data': 'help|0|0|0|0'}
                ],
            ]
        elif self.bot == 'search':
            self.inline_keyboard = [
                [
                    {'text': '热门标签', 'callback_data': 'ST|Tag|all|0|0'},
                    {'text': '热门标签', 'callback_data': 'ST|Tag|all|0|0'},
                ],
                [{'text': '添加收录', 'url': f'{self.bots["url"]}?/add=true'},],
                [{'text': '添加机器人到群组', 'url': f'{self.bots["url"]}?startgroup=true'}],
            ]

    def help(self):
        '''
        定义帮助命令
        :return:
        '''
        self.send_text = self.bots['help_description']['text']
        self.predefined_entities = self.predefined_entities + self.bots['help_description']['entities']
        if self.bot == 'rules':
            self.inline_keyboard = [
                [{'text': '添加到群组', 'url': f'{self.bots["url"]}?startgroup=true'}],
                [{'text': '返回', 'callback_data': 'start|0|0|0|0'}]
            ]
        elif self.bot == 'search':
            self.inline_keyboard = [
                [{'text': '添加到群组', 'url': f'{self.bots["url"]}?startgroup=true'}],
                [{'text': '返回', 'callback_data': 'start|0|0|0|0'}]
            ]


    def reply_collect(self, data=None):
        '''
        响应收藏命令和处理用户提交的收藏信息
        1.  响应用户的 add 命令，提示用户输入收藏信息，此时无需要提供参数
        2.  处理用户提交的收藏信息，此时应该提供所有参数

        3.  校验接连的合法性，查询当前数据库系统是否包含当前拉链，调用方法检查链接详情并将收藏结果返回给用户
        :param data: 参数集，包含了创建 telegram 请求的必要参数，可能为空
        :return:
        '''
        text = ''
        if data:
            # 从工具箱调用 extract_links 方法提取文本中所有的链接
            urls = toolbox.extract_links(data['text'])
            for url in urls:
                if not url.startswith('http//t.me/'):
                    text += f'{url} 不是一个合法的 telegram 群组链接\n'
                    continue

                query = f'SELECT `render`, `create_time` FROM `{sql.table_groups}` WHERE `url`=%s'
                query = sql.query(sql.base_database, query, [url])

                text = f"{text}{url} 收录成功\n' if query else f'{text}{url} 已由 {query[0]['render']}  于 {query[0]['create_time']} 添加\n"
        else:
            text = '请输入你的群组链接'

        self.inline_keyboard = [[{'text': '返回', 'callback_data': f'start|0|0|0|0'}]]
        self.send_text = f'{self.bots["chat_title"]["text"]} >> 群组收录\n\n{text}'
        self.predefined_entities = self.predefined_entities + self.bots["chat_title"]["entities"]


if __name__ == '__main__':

    command = Command('search')
    print(command.reply_command('/start'))





