
'''
关于机器人命令的所有功能在此类中定义
'''

from database import sql

from utils.tools import tools

from utils.account import account


class Command:

    '''
    应用机器人命令

    '''


    def __init__(self):
        '''
        旨中响应用户的命令消息和解析用户使用 ADD 命脉后输入的收藏信息

        '''
        self.send_text = ''
        self.inline_keyboard = []
        self.predefined_entities = []

    def command_main(self, bot, bot_command, user, message):
        '''
        将机器人的开始命令应用到响应
        机器人需要记录与每个用户的交互状态，将这些信息写入 interact 数据表，
        :param bot:
        :param bot_command: 机器人命令
        :param user
        :param message: 额外参数，用于扩展命令处理逻辑
        :return:
        '''
        result = {}
        if bot_command == '/start':
            result = self.start(bot)
        if bot_command == '/help':
            result = self.help(bot)
        if bot_command == '/add':
            result = self.collect(bot, user, message)

        return result

    @classmethod
    def start(cls, bot):
        '''
        响应用户的 start 命令
        :return:
        '''
        text = f"{account.attribute(bot)['title']['text']}\n\n{account.attribute(bot)['start_description']['text']}"
        entities = account.attribute(bot)['title']['entities'] + account.attribute(bot)['start_description']['entities']
        if bot == 'rules':
            inline_keyboard = [

                [
                    {'text': '机器人定制', 'url': 'https://t.me/bigapple699'},
                    {'text': '刷新群组列表', 'callback_data': 'rules|prelude|0|0|0'}
                ],
                [
                    {'text': '添加到群组', 'url': f'{account.attribute(bot, "url")}?startgroup=true'},
                    {'text': '帮助', 'callback_data': 'help|0|0|0|0'}
                ],
            ]

        else:
            inline_keyboard = [
                [
                    {'text': '分类搜索', 'callback_data': 'ST|0|0|0|0'},
                    {'text': '热门标签', 'callback_data': 'ST|Tag|0|0|0'},
                ],
                [{'text': '添加收录', 'callback_data': 'add|0|0|0|0'}],
                [{'text': '添加到群组', 'url': f'{account.attribute(bot, "url")}?startgroup=true'}],
            ]
        return {
            'text': text,
            'reply_markup': {'inline_keyboard': inline_keyboard},
            'entities': tools.format_entities(text, entities)
        }

    @classmethod
    def help(cls, bot):
        '''
        定义帮助命令
        :return:
        '''
        text = f"{account.attribute(bot)['title']['text']}\n\n{account.attribute(bot)['help_description']['text']}"

        entities = account.attribute(bot)['title']['entities'] + account.attribute(bot)['help_description']['entities']
        if bot == 'rules':
            inline_keyboard = [
                [{'text': '添加到群组', 'url': f'{account.attribute(bot, "url")}?startgroup=true'}],
                [{'text': '返回', 'callback_data': 'start|0|0|0|0'}]
            ]
        else:
            inline_keyboard = [
                [{'text': '添加到群组', 'url': f'{account.attribute(bot, "url")}?startgroup=true'}],
                [{'text': '返回', 'callback_data': 'start|0|0|0|0'}]
            ]

        return {
            'text': text,
            'reply_markup': {'inline_keyboard': inline_keyboard},
            'entities': tools.format_entities(text, entities)
        }

    @classmethod
    def collect(cls, bot, user, message):
        '''
        响应收藏命令和处理用户提交的收藏信息
        1.  响应用户的 add 命令，提示用户输入收藏信息，此时无需要提供参数
        2.  处理用户提交的收藏信息，此时应该提供所有参数

        3.  校验接连的合法性，查询当前数据库系统是否包含当前拉链，调用方法检查链接详情并将收藏结果返回给用户
        :param bot: 此参数应该是一个机器人对象
        :param user: 此参数应该是一个用户ID
        :param message: 此参数应该是一个消息ID
        :return:
        '''
        query = (f"INSERT INTO `{sql.table_interact}` (`bot`,`user`,`waitinput`) VALUES (%s,%s,%s) "
                 f"ON DUPLICATE KEY UPDATE `waitinput`=%s")
        sql.query(sql.database, query, [bot, user, f'search|add|0|0|0', f'search|add|0|0|{message}'])
        text = '🔔 请输入你的群组链接'
        add_description = account.attribute(bot, 'add_description').get('text')
        inline_keyboard = [[{'text': '返回', 'callback_data': f'start|0|0|1|0'}]]
        send_text = f'{account.attribute(bot)["title"]["text"]} >> 群组收录\n\n{add_description}\n\n{text}'
        entities = account.attribute(bot)["title"]["entities"]

        return {
            'text': send_text,
            'reply_markup': {'inline_keyboard': inline_keyboard},
            'entities': tools.format_entities(send_text, entities)
        }




command = Command()

if __name__ == '__main__':

    print(command.command_main('search', '/start', None, None))





