

'''
处理 message 消息
'''


import json
import time
from utils.account import account
from database import sql

from utils.command import Command

from utils.toolbox import toolbox
from utils.rules import Rules

from utils.register import register
from utils.search import Search

import config
import logging
from logmanage import DailyLogManager


log = DailyLogManager('message', logging.ERROR, logging.INFO)

class Message:
    '''
    创建类实例
    调用相关方法协助解析 message
    '''

    def __init__(self, data):
        '''
        初始化消息实例，提取常用属性
        :param data: message 消息主体
        '''

        self.message_id = data.get('message_id')
        self.chat_id = data.get('chat').get('id')
        self.chat_type = data.get('chat').get('type')
        self.chat_title = data.get('chat').get('title')

        self.users = data.get('from')
        self.is_bot = data.get('from').get('is_bot')
        self.user_id = data.get('from').get('id')
        self.user_name = data.get('from', {}).get('username')
        self.first_name = data.get('from', {}).get('first_name')
        self.last_name = data.get('from', {}).get('last_name', '')

        self.date = data.get('date')
        self.message_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.date))
        self.text = data.get('text')
        self.caption = data.get('caption')
        self.photo = data.get('photo')
        self.document = data.get('document')
        self.video = data.get('video')
        self.voice = data.get('voice')
        self.audio = data.get('audio')
        self.contact = data.get('contact')
        self.forward = data.get('forward_origin', data.get('forward_from'))

        self.entities = data.get('entities', [])
        self.new_chat_members = data.get('new_chat_members', None)
        self.left_chat_member = data.get('left_chat_member', None)


    def init_rules(self, bot):
        '''
        初始化群组的管理规则，只有超级群组才需要规则参数
        从 rules 是提取生效的规则
        :return:
        '''

        if bot != 'rules':
            return {}

        result = {}
        query = f"SELECT * FROM rules WHERE chat=%s"
        query = sql.query(sql.base_database, query, [self.chat_id])
        if query:
            for key, value in query[0].items():
                if value is None or key in ['chat', 'title', 'created', 'edited']:
                    continue
                value = json.loads(value)
                if key in ['administrators', 'newcomer']:
                    result.update({key: value})
                elif key == 'register' and value.get('status') == 'Run':
                    result.update({key: value})
                elif key == 'intelligent' and value.get('mode') and value.get('level'):
                    result.update({key: value})
                elif value.get('level'):
                    result.update({key: value})
        return result

class Private(Message):
    '''
    处理机器人与用户的个人聊天
    在本地数据库创建了一个机器人与用户交互的数据表，根据这此数据与用户交互
    '''
    def __init__(self, bot, data):
        '''
        初始化机器人属性
        :param bot: 机器人名，主要响应用户的 bot_command
        :param data: 消息的主体
        '''
        super().__init__(data)
        self.bot = bot
        self.bot_id = account.attribute(bot, 'id')
        self.waitinput = self.interact(self.chat_id, self.bot_id)   # 从交互数据表提取等待用户提交的信息
        self.send_data = []

    def main(self):
        '''
        主程序
        :return:
        '''
        if self.waitinput:
            if self.waitinput[0] == 'rules':
                return Rules(
                    self.chat_id,
                    self.user_id,
                    ['rules', self.waitinput[1], self.waitinput[2], 0, self.waitinput[3]],
                    self.waitinput[4]
                ).apply_rules_params(self.text)

        if self.entities:
            # 处理富文本对象
            for entitie in self.entities:
                if entitie.get('type') == 'bot_command':
                    result = Command(self.bot).reply_command(self.text)
                    self.send_data.append([
                        'sendMessage',
                        {'chat_id': self.chat_id, **result},
                        None
                    ])

                elif entitie.get('type') == 'url' and self.waitinput and self.waitinput[0] == 'add':
                    result = Command(self.bot).reply_collect(self.text)
                    self.send_data.append([
                        'editMessageTxt',
                        {'chat_id': self.chat_id, 'message_id': self.waitinput[-1], **result},
                        None
                    ])

        if not self.send_data:
            result = Search(self.user_id, ['SP', self.text, 'all', 0, self.user_id]).main()
            self.send_data.append([
                'sendMessage',
                {
                    'chat_id': self.chat_id,
                    'reply_to_message_id': self.message_id,
                    'disable_web_page_preview': True,
                    **result
                },
                None
            ])

        return self.send_data

    @classmethod
    def interact(cls, user, bot):
        '''
        获取机器人与用户的交互信息
        :return:
        '''
        query = f"SELECT `waitinput` FROM `interact` WHERE `user`=%s AND `bot`=%s"
        query = sql.query(sql.base_database, query, [user, bot])
        if query and query[0]:
            return query[0]['waitinput'].split('|')
        return []



class SuperGroup(Message):

    def __init__(self, bot, data):
        '''
        初始化机器人补修
        :param bot: 机器人名，rules or search
        :param data: 消息主体

        :var self.rules: 储存当前群组的管理规则，由 self.init_rules() 方法赋值
        :var self.tasks: 一个函数容器，接收 register_tasks() 方法注册的函数，以便统一运行
        '''
        super().__init__(data)
        self.bot = bot
        self.bot_id = account.attribute(bot, 'id')
        self.bot_url = account.attribute(bot, 'url')
        self.rules = self.init_rules(self.bot)
        self.is_admin = self.is_administrator()
        self.send_data = []

    def register_tasks(self):
        '''
        扫描当前类的所有实例的函数

        :return:
        '''
        result = []
        for row in self.rules.keys():
            for attr_name in dir(self):  # 遍历实例的属性和方法
                attr = getattr(self, attr_name)
                if callable(attr) and attr_name.startswith('analysis') and attr_name.endswith(row):
                    result.append(attr)
        return result

    def main(self):
        '''
        主程序
        :return:
        '''

        if (self.new_chat_members or self.left_chat_member) and self.rules.get('newcomer'):

            # 响应群组中成员加入或离开的信息
            self.analysis_members(self.rules.get('newcomer'))

        elif self.text == '签到' and self.rules.get('register'):

            result = register.apply_register(self.chat_id, self.user_id, self.message_time)
            if result == '你已涉嫌恶意签到，':
                self.send_data.append([
                    'restrictChatMember',
                    {
                        'chat_id': self.chat_id,
                        'user_id': self.user_id,
                        'permissions': self.permissions(True),
                        'until_date': self.date + 300
                    },
                    None
                ])
            if result:
                text = f"{self.first_name} {result}！！"
                input(self.rules['register'])
                if result == '恭喜签到成功':
                    text = f"{text}🎉🎉\n{self.rules['register']['explain']}"
                input(text)
                self.send_data.append([
                    'sendMessage',
                    {
                        'chat_id': self.chat_id,
                        'text': text,
                        'entities': toolbox.format_entities(
                            text,
                            [{'type': 'text_mention', 'text': self.first_name, 'user': self.users}]
                        )
                    },
                    {'delete': run_config.date + 30}  # 此消息将在30秒后删除
                ])

        elif self.text == 'hello wellwen' and self.bot == 'rules':
            self.hello_wellwen()

        elif self.is_admin and self.bot == 'rules':
            log.info('这是管理员的消息')
            return self.send_data

        elif self.rules and self.bot == 'rules':
            # 批量执行函数
            tasks = self.register_tasks()
            for task in tasks:
                result = task()
                if result:
                    self.rules_message(result[0], result[1])
                    break

        elif self.bot == 'search' and self.text and len(self.text) > 20:
            self.send_data.append([
                'sendMessage',
                {'text': f'{self.first_name} 搜索不得超过20个字符', 'chat_id': self.chat_id,},
                None
            ])
        elif self.bot == 'search' and self.text:
            result = Search(self.user_id, ['SG', self.text, 'all', 0, self.user_id]).main()
            self.send_data.append([
                'sendMessage',
                {'chat_id': self.chat_id, 'reply_to_message_id': self.message_id, 'disable_web_page_preview': True, **result},
                None
            ])

        return self.send_data

    def hello_wellwen(self):
        '''
        响应 hello_wellwen 消息，这是一个特殊消息，当机器人在某个群组收到此消息时，
        1， 获取当前群组管理员，查看管理员列表是否包含了当前用户和机器人，如果是，则为当前群组创建规则数据
        2， 调用 Rules 类的 rules_start 方法将当前群组以按钮形式展示到与用户的私人聊天中
        :return:
        '''
        # 获取管理员列表
        administrators = toolbox.get_administrator(self.bot, self.chat_id)
        creator = None
        administrator = None
        bot_administrators = None

        for admin in administrators:
            # 查看管理员列表是否包含当前用户和机器人
            if admin.get('user').get('id') == self.user_id:
                if admin.get('status') == 'creator':
                    creator = True
                else:
                    administrator = True

            elif admin.get('user').get('id') == self.bot_id:
                bot_administrators = True

        if (creator or administrator) and bot_administrators:
            # 为当前群组创建规则数据，并将管理员更新到规则数据的管理员规则项
            query = (f'INSERT INTO {sql.table_rules} (`chat`, `title`, `administrators`) VALUES (%s,%s,%s) '
                     f'ON DUPLICATE KEY UPDATE `administrators`=%s, edited=NOW()')
            administrators = json.dumps(administrators, ensure_ascii=False)
            sql.query(sql.base_database, query, [self.chat_id, self.chat_title, administrators, administrators])

            text = f'{self.first_name}\n\n已为当前群组创建管理规则【点击此处编辑你的规则】'

            # 创建富文本对象
            entities = toolbox.format_entities(
                text,
                [
                    {'type': 'text_mention', 'text': self.first_name, 'user': self.users},
                    {'type': 'text_link', 'text': '点击此处编辑你的规则', 'url': self.bot_url},
                ]
            )

            # 构建发送消息对象
            self.send_data.append([
                'sendMessage',
                {'chat_id': self.chat_id, 'text': text, 'entities': entities},
                None
            ])

            # 从用户与机器人的交互数据表（interact）中获取机器人与用户最后一次交互的信息，并从中提取出 message_id
            query = f'SELECT interact FROM {sql.table_interact} WHERE user=%s AND bot=%s'
            query = sql.query(sql.base_database, query, [self.user_id, self.bot_id])
            try:
                interact_message_id = query[0]['interact']
            except Exception:
                interact_message_id = None

            if interact_message_id:
                result = Rules(
                    self.user_id,
                    self.user_id,
                    ['rules', 'prelude', 0, 0, 0],
                    interact_message_id
                ).main()

                self.send_data = self.send_data + result

    def analysis_members(self, rules):
        '''
        处理新成员加入群组的方法
        :return:
        '''

        if self.new_chat_members and rules['tip_join']:
            # 移除新人加入的系统消息
            self.send_data.append([
                'deleteMessage',
                {'chat_id': self.chat_id, 'message_ids': self.message_id},
                None
            ])


        if self.left_chat_member and rules['tip_leave']:
            # 删除用户离群的系统提示
            self.send_data.append([
                'deleteMessage',
                {'chat_id': self.chat_id, 'message_ids': self.message_id},
                None
            ])

        if self.new_chat_members and rules['verify_join']:

            # 查询当前群组的成员验证数据
            query = f'SELECT verify FROM {sql.table_restriction} WHERE bot=%s and chat=%s'
            query = sql.query(sql.base_database, query, [self.bot_id, self.chat_id])
            verify_data = {}
            if query and query[0]:
                verify_data = query[0].get('verify', {})
                if verify_data:
                    verify_data = json.loads(verify_data)

            for member in self.new_chat_members:
                member_id = member.get('id')
                if member.get('is_bot'):
                    continue
                verify_data.update({member_id: self.date + 120})

                # 在用户完成验证之前，你应该先将用户禁言
                self.send_data.append([
                    'restrictChatMember',
                    {'chat_id': self.chat_id, 'user_id': member_id, 'permissions': self.permissions(True)},
                    None
                ])

                # 调用 toolbox.create_verify() 方法生成一条验证消息
                result = toolbox.create_verify(member, self.chat_id)
                # 向群组推送这条验证消息
                self.send_data.append([
                    'sendMessage',
                    {'chat_id': self.chat_id, **result},
                    None
                ])
            query = (f'INSERT INTO {sql.table_restriction} (bot,chat,verify) VALUES (%s,%s,%s) '
                     f'ON DUPLICATE KEY UPDATE verify=%s, edited=NOW()')
            sql.query(sql.base_database, query, [self.bot_id, self.chat_id, json.dumps(verify_data), json.dumps(verify_data)])

        elif self.new_chat_members:
            members_names = ''
            entitle_pamrams = []
            for member in self.new_chat_members:
                if member.get('is_bot'):
                    continue
                name = f"{member['first_name']}{member.get('last_name', '')}"
                members_names = f"{members_names}{name}，"
                entitle_pamrams.append({'type': 'text_mention', 'text': name, 'user': member})

            if members_names:
                text = rules['welcome']
                if not text:
                    text = f"{members_names} 欢迎加入 {self.chat_title}"
                elif text and text.find('@@') != -1:
                    # 如果欢迎语中包含了 @@ 的点位符，则将其替换成用户的名字（self.first_name）
                    text.replace('@@', members_names, 1)
                else:
                    text = f"{members_names} {text}"

                # 创建富文本对象
                entitles = toolbox.format_entities(text, entitle_pamrams)

                # 构建请求对象并添加到请求容器
                self.send_data.append([
                    'sendMessage',
                    {'chat_id': self.chat_id, 'text': text, 'entities': entitles},
                    None
                ])

    def analysis_entities(self):
        '''
        解析富文本对象
        :return:
        '''

        if not self.entities or not self.rules.get('link'):
            return None
        for entitle in self.entities:
            if entitle['type'] == 'url' and self.rules.get('link'):
                return 'link', '消息违规【包含链接】'

        return None

    def analysis_intelligent(self):
        '''
        应用智能反广告规则（intelligent），此规则一旦生效，它必须记录最近消息的消息的特征，所以在处理规则消
        息时应当将此项规则放在最前面。

        本规则虽然会记录所有最近消息的特征，但仅对消息中的文本对象有效，基本的逻辑如下：
        1. 为最近的消息生成一个消息特征：如果消息中包括文本对象，则检查文本消息是琐规则，并根据检查结果设置违规特征，
            最终生成一个包含 self.date, self.message_id, self.user_id, violate_feature 的消息特征对象，
        2. 将消息特征对象储存到 restriction 数据表。
        3。 迭代从数据获取的所有消息特征，统计每个消息特征中的违规特征，如果违规特征数量超过用户设定的允许次数（allow），
            当前消息即被视为违规，将调用规则处理方法响应
        :return:
        '''
        mode = self.rules.get('intelligent').get('mode')
        scope = self.rules.get('intelligent').get('scope')
        allow = self.rules.get('intelligent').get('count')

        if not scope or scope < 1:
            return None


        # 构建消息特征
        intelligent = [[self.date, self.message_id, self.user_id, self.text if self.text else None]]

        query = f'SELECT intelligent FROM {sql.table_restriction} WHERE chat=%s AND bot=%s'
        query = sql.query(sql.base_database, query, [self.chat_id, self.bot_id])
        if query and query[0]:
            intelligent = json.loads(query[0]['intelligent']) + [intelligent]

        # 维护消息特征数据，
        if mode == '时长':
            # 超出时间的消息特征将被删除
            while len(intelligent) > 1 and (self.date - intelligent[0][0]) > (scope * 60):
                del intelligent[0]
        else:
            # 超出消息量的消息特征将被删除
            while len(intelligent) > scope:
                del intelligent[0]

        duplicate = []
        delete_message = []
        for index, nodes in enumerate(intelligent):
            if nodes[3] in duplicate and nodes[2] == self.user_id:
                delete_message.append(index)
            else:
                duplicate.append(nodes[3])

        delete_message_ids = []
        if len(delete_message) > allow:
            for index in delete_message:

                if intelligent[index][1]:
                    delete_message_ids.append(intelligent[index][1])
                    intelligent[index][1] = None
            self.send_data.append([
                'deleteMessages',
                {'chat_id': self.chat_id, 'message_ids': delete_message_ids},
                None
            ])
            return 'intelligent', '发布消息过于频繁'

        # 将最新的消息特征数据更新到 restriction 数据表
        query = (f'INSERT INTO {sql.table_restriction} (bot,chat,intelligent) VALUES (%s,%s,%s) ON DUPLICATE '
                 f'KEY UPDATE intelligent=%s, edited=NOW()')
        sql.query(sql.base_database, query, [self.bot_id, self.chat_id, json.dumps(intelligent), json.dumps(intelligent)])

        return None

    def analysis_text(self):
        '''
        解析文本消息
        :return:
        '''
        if not self.text or not self.rules.get('text'):
            return None
        length = self.rules.get('text')['len']
        height = self.rules.get('text').get('high')
        if len(self.text) > length:
            return 'text', f'消息违规【长度超出{length}字的长度限制】'
        elif self.text.count('\n') > height:
            return 'text', f'消息违规【行数超出{height}行的行数限制】'

        if self.rules.get('text').get('key'):
            key = self.check_key(self.text, self.rules.get('text').get('key').split('，'))

            if key:
                return 'text', f'消息违规【包含了违规关键字"{key}"】'

        return None

    def analysis_photo(self):
        '''

        :return:
        '''
        if not self.photo or not self.rules.get('photo'):
            return None
        return 'photo', f'消息违规【包含了图片】'

    def analysis_video(self):
        '''

        :return:
        '''
        if not self.video or not self.rules.get('video'):
            return None
        return 'video', f'消息违规【包含了视频】'

    def analysis_voice(self):
        '''

        :return:
        '''
        if not self.voice or not self.rules.get('voice'):
            return None
        return 'voice', f'消息违规【包含了语音】'

    def analysis_contact(self):
        '''

        :return:
        '''
        if not self.contact or not self.rules.get('contact'):
            return None
        return 'contact', f'消息违规【包含了名片】'

    def analysis_document(self):
        '''

        :return:
        '''
        if not self.document or not self.rules.get('document'):
            return None
        return 'document', f'消息违规【包含了文件】'

    def analysis_forward(self):
        '''

        :return:
        '''
        if not self.forward or not self.rules.get('forward'):
            return None
        return 'forward', '消息违规【转发其它聊天的消息】'

    def rules_message(self, rules_option, default_wan):
        '''
        按规则处理群组消息
        :return:
        '''
        allow = self.rules.get(rules_option).get('allow')
        level = self.rules.get(rules_option).get('level')
        restrict = self.rules.get(rules_option).get('restrict')  # 禁言措施中的禁言时长参数

        # 从受限制数据表（restriction）中获取当前群组违规用户的违规详情，并反序列化为 python 对象
        query = f'SELECT rules_limit FROM {sql.table_restriction} WHERE chat=%s AND bot=%s AND rules_limit IS NOT NULL'
        rules_limit = sql.query(sql.base_database, query, [self.chat_id, self.bot_id])

        if rules_limit and rules_limit[0]:
            rules_limit = json.loads(rules_limit[0]['rules_limit'])
        else:
            rules_limit = {}
        limit_count = rules_limit.get(rules_option, {}).get(str(self.user_id))  # 获取当前用户的违规次数，此值可能为空
        if not limit_count:
            if rules_option not in rules_limit:
                rules_limit[rules_option] = {}  # 初始化为一个空字典
            limit_count = 0

        # 只要是违规消息就要删除
        self.send_data.append([
            'deleteMessage',
            {'chat_id': self.chat_id, 'message_id': self.message_id},
            None
        ])

        restrict_message = []

        # 解析渐进式限制规则并应用到群组
        if level in ['gradually(kick)', 'gradually(block)']:
            # 渐进式限制规则是一次警告二次禁言1小时三次禁言24小时四次移出或拉黑

            # 首次违规不会采取任何限制措施
            if limit_count == 0:
                # 设定警告语
                default_wan = f'{self.first_name} {default_wan}，如多次违规将被移出群聊{"" if level == "gradually(kick)" else "并拉黑"}'

                # 记录用户的违规次数
                rules_limit[rules_option].update({str(self.user_id): 1})

            # 多次违规就要采取相应措施了，分别是禁言一小时和禁言24小时
            elif limit_count in [1, 2]:

                # 累计用户的违规记录
                rules_limit[rules_option].update({str(self.user_id): limit_count + 1})

                # 设定禁言时长
                until_date = {1: self.date + 3600, 2: self.date + (24 * 3600)}[limit_count]

                # 设定警告语告知用户将被禁言到 until_time 时间
                until_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(until_date))
                default_wan = f'{self.first_name} {default_wan}，已被禁言至{until_time}'

                # 设定限制规则，将当前用户禁言到 until_date
                restrict_message.append([
                    'restrictChatMember',
                    {'chat_id': self.chat_id, 'user_id': self.user_id, 'permissions': self.permissions(True), 'until_date': until_date},
                ])

            elif limit_count > 2:
                # 设定警告语
                default_wan = f'{self.first_name} {default_wan}，已被被移出群聊{"" if level == "gradually(kick)" else "并拉黑"}'

                # 设定限制规则，从当前群组移出或拉黑该用户
                restrict_message.append([
                    ['kickChatMember' if level == 'gradually(kick)' else 'banChatMember', {'chat_id': self.chat_id, 'user_id': self.user_id}]
                ])
                # 将用户的违规记录删除，因为用户已不在当前群组中了
                del rules_limit[rules_option][str(self.user_id)]

        elif level == 'deleteMessage':
            default_wan = f'{self.first_name} {default_wan}，此消息已被删除'

        elif level == 'restrictChatMember':
            if limit_count >= allow:

                # 将当前用户违规记录删除
                if rules_limit.get(rules_option).get(str(self.user_id)):
                    del rules_limit[rules_option][str(self.user_id)]

                # 如果限制措施是禁言，则需要搂 restrict 参数设置禁言时长，restrict 是从群组的规则参数中提取
                # restrict 有5种状态，永久，10分钟，1小时，24小时和一周，你需要用上述状态计算出禁言终止的时间戳
                until_date = {
                    '永久': 0,
                    '10分钟': self.date + 600,
                    '1小时': self.date + 3600,
                    '24小时': self.date + (24 * 3600),
                    '一周': self.date + (7 * 24 * 3600)
                }.get(restrict)

                # 将 until_date 时间戳转换成普通的日期时间格式并设定警告语告知用户将被禁言到 until_time 时间
                until_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(until_date))
                default_wan = f'{self.first_name} {default_wan}，且多次违规，已被{"禁言" if until_date == 0 else "禁言到" + until_time}'
                # 对用户采取禁言的限制措施，
                restrict_message.append([
                    level,
                    {'chat_id': self.chat_id, 'user_id': self.user_id, 'permissions': self.permissions(True), 'until_date': until_date}
                ])
            else:
                rules_limit[rules_option].update({str(self.user_id): limit_count + 1})
                default_wan = f'{self.first_name} {default_wan}，多次违规将被禁言'

        elif limit_count >= allow:
            # 将当前用户违规记录删除
            if rules_limit.get(rules_option).get(str(self.user_id)):
                del rules_limit[rules_option][str(self.user_id)]
            # 移出或拉黑用户，
            default_wan = f'{self.first_name} {default_wan}，且多次违规，已被移出群聊{"" if level == "kickChatMember" else "并拉黑"}'
            restrict_message.append([
                level,
                {'chat_id': self.chat_id, 'user_id': self.user_id, }
            ])
        else:
            rules_limit[rules_option].update({str(self.user_id): limit_count + 1})
            default_wan = f'{self.first_name} {default_wan}，多次违规将被禁言'

        self.send_data.append([
            'sendMessage',
            {
                'chat_id': self.chat_id,
                'text': default_wan,
                'entities': toolbox.format_entities(default_wan, [{'type': 'bold', 'text': self.first_name}])
            },
            {'delete': run_config.date + 30}  # 此消息将在30秒后删除
        ])

        # 将新的限制数据更新到 restriction 数据表
        query = (f'INSERT INTO {sql.table_restriction} (bot,chat,rules_limit) VALUES (%s,%s,%s) '
                 f'ON DUPLICATE KEY UPDATE rules_limit=%s')
        rules_limit = json.dumps(rules_limit)
        sql.query(sql.base_database, query, [self.bot_id, self.chat_id, rules_limit, rules_limit])

        return self.send_data + restrict_message

    def is_administrator(self):
        '''
        检查用户是否管理员
        :return:
        '''
        if not self.rules:
            return False
        for admin in self.rules.get('administrator', []):
            if self.user_id == admin.get('user').get('id'):
                return admin.get('user').get('status')
        return False

    @classmethod
    def permissions(cls, restrict=None):
        '''
        限制和解除限制
        :param restrict: 些参数有效时为添加限制
        :return:
        '''
        return {
            'can_send_messages': False if restrict else True,
            'can_send_audios': False if restrict else True,
            'can_send_documents': False if restrict else True,
            'can_send_photos': False if restrict else True,
            'can_send_videos': False if restrict else True,
            'can_send_video_notes': False if restrict else True,
            'can_send_voice_notes': False if restrict else True,
            'can_send_polls': False if restrict else True,
            'can_send_other_messages': False if restrict else True,
            'can_add_web_page_previews': False if restrict else True,
            'can_change_info': False if restrict else True,
            'can_invite_users': False if restrict else True,
            'can_pin_messages': False if restrict else True,
            'can_manage_topics': False if restrict else True,
        }

    @classmethod
    def check_key(cls, text, keys):
        '''
        检查字串中是不回包含子串
        :return:
        '''
        if not text or not keys:
            return False
        for key in keys:
            if key in text:
                return key
        return False


def message_filter(bot, datas):
    '''

    :param bot:
    :param datas:
    :return:
    '''
    message_type = datas.get('message').get('chat').get('type')
    if message_type == 'private':
        telegram = Private(bot, datas['message'])

    else:
        telegram = SuperGroup(bot, datas['message'])

    return telegram.main()



if __name__ == '__main__':

    from test import debugging

    ty = message_filter('rules', debugging.message_example_9['result'][0])

    print(ty)


































