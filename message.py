

'''
处理 message 消息
'''


import json
from utils.account import account
from database import sql
from utils.command import command
from utils.tools import tools
from utils.rules import Rules
from utils.register import register
from utils.search import Search
from utils.quick import quick
from utils.WholeTime import wholetime
import logging
from logmanage import LogManager

log = LogManager('Message', logging.WARNING, logging.INFO)


def rule_handler(rule_name, order=100, stop_on_hit=True):
    '''
    群组规则处理器装饰器。

    这个装饰器不直接执行方法，它只负责给方法打上“规则标记”，
    后续 register_tasks() 会扫描这些标记，并将符合条件的方法注册为待执行任务。

    :param rule_name:
        规则名称，必须和 self.rules 中的规则字段名一致。
        例如：
            self.rules['text']
            self.rules['photo']
            self.rules['link']

        如果数据库中的规则字段叫 link，但实际处理方法叫 parse_entities，
        也可以通过 @rule_handler('link') 进行绑定。

    :param order:
        执行顺序，数字越小越先执行。
        建议按照你的数据表字段顺序或者业务优先级设置。
        例如：
            intelligent -> 10
            link        -> 20
            text        -> 30
            photo       -> 40

    :param stop_on_hit:
        当前规则命中后，是否停止执行后续规则。

        True:
            命中后立即停止。
            适合大多数违规检测，例如 text/photo/video/link。
            因为一条消息只需要按一个规则处理即可。

        False:
            命中后继续执行后续规则。
            适合只做记录、不做最终拦截的规则。
            例如某些统计类、日志类、特征收集类规则。

    :return:
        返回原函数本身，但会给函数附加三个自定义属性：
            rule_name
            rule_order
            rule_stop_on_hit
    '''
    def decorator(func):
        '''
        记录此方法对应哪一个规则
        :param func:
        :return:
        '''
        func.rule_name = rule_name

        # 记录此方法的执行顺序
        func.rule_order = order

        # 记录此方法命中后是否停止执行后续规则
        func.rule_stop_on_hit = stop_on_hit

        return func

    return decorator

class Message:
    '''
    创建类实例
    调用相关方法协助解析 message
    '''

    def __init__(self, bot, data):
        '''
        初始化消息实例，提取常用属性
        :param data: message 消息主体
        '''
        self.bot = bot
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
        self.message_time = wholetime.datetime(Unix=self.date)
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

        self.waitinput, self.exchange = self.interact(self.user_id, self.bot)  # 从交互数据表提取等待用户提交的信息

    def init_rules(self):
        '''
        初始化群组的管理规则，只有超级群组才需要规则参数
        从 rules 是提取生效的规则
        :return:
        '''

        result = {}

        if self.chat_type != 'supergroup':
            # 跳过非群组聊天
            return result


        table = sql.table_rules if self.bot == 'rules' else sql.table_search
        query = f"SELECT * FROM `{table}` WHERE `chat`=%s"
        current_chat = sql.query(sql.database, query, [self.chat_id]) or []
        if not current_chat:

            # 记录机器人所在群组，基于telegram bot 的策略，此方法是获取机器人所在群组的最直接方法
            quick.update_chat(self.bot, self.chat_id, self.chat_type, self.chat_title)

            return result

        current_rules = current_chat[0]
        if self.chat_title != current_rules.get('title'):
            query = f"UPDATE {table} SET `title`=%s WHERE `chat`=%s"
            sql.query(sql.database, query, [self.chat_title, self.chat_id])


        if self.bot != 'rules':
            return result

        bot_status = current_rules.get('bot_status')

        if not bot_status or bot_status.get('status') != 'administrator' or not bot_status.get('can_manage_chat'):
            # 检查机器人是否当前群组的管理员且是否拥有相应权限
            log.info(f"Bot is not administrator in chat {self.chat_title}, skipping rules")
            return result

        # 读取有效规则
        for key, value in current_rules.items():
            if value is None or key in ['chat', 'title', 'type', 'number', 'initiator', 'created', 'edited']:
                # 跳过非规则字段
                continue
            if key == 'bot_status':
                # 如果机器人不是管理员，则所有规则无效
                if value.get('status') != 'administrator':
                    return {}
            elif key in ['administrators', 'newcomer']:
                # 管理员和新人管理字段不管实际是否有效都被直接视为有效，
                result.update({key: value})

            elif key == 'register' and value.get('status') == 'Run':
                # 读取签到规则，只有进行中的签到项目才被视为有效规则
                result.update({key: value})

            elif key == 'intelligent' and value.get('mode') and value.get('level'):
                # 读取智能反广告规则，只有设置了检测模式和处理级别的才被视为有效规则
                result.update({key: value})

            elif value.get('level'):
                # 其它的规则也是只有设置了处理级别的才被视为有效规则
                result.update({key: value})
        return result

    @classmethod
    def interact(cls, user, bot):
        '''
        获取机器人与用户的交互信息
        :return:
        '''
        query = f"SELECT `waitinput`,`exchange` FROM `{sql.table_interact}` WHERE `user`=%s AND `bot`=%s"
        query = sql.query(sql.database, query, [user, bot]) or []

        result = [None, None]
        for row in query:
            if not row:
                continue
            if row['waitinput']:
                result[0] = row['waitinput'].split('|')
            elif row['exchange']:
                result[1] = row['exchange']
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
        super().__init__(bot, data)
        self.send_data = []

    def private_message(self):
        '''
        主程序
        :return:
        '''
        # 处理富文本对象
        if self.entities:
            self.parse_message_entitie()
        else:
            self.parse_message()

        return self.send_data

    def parse_message(self):

        if self.waitinput and self.waitinput[0] == 'rules':
            # 检查是否等待用户输入

            result = Rules(
                self.chat_id,
                self.user_id,
                ['rules', self.waitinput[1], self.waitinput[2], 0, self.waitinput[3]],
                self.waitinput[4]
            ).set_rules_params(self.text)

            self.send_data.extend(result)
        else:
            result = Search(self.user_id, ['SP', self.text, 'all', 0, self.user_id]).search_main()
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

    def parse_message_entitie(self):
        '''
        解析富文本内容
        :return:
        '''
        for entitie in self.entities:
            if entitie.get('type') == 'bot_command':
                result = command.command_main(self.bot, self.text, self.user_id, self.message_id)
                self.send_data.append([
                    'sendMessage',
                    {'chat_id': self.chat_id, **result},
                    None
                ])

            elif entitie.get('type') == 'url' and self.waitinput and self.waitinput[1] == 'add':

                self.reply_collect()

    def reply_collect(self):
        '''
        响应收藏命令和处理用户提交的收藏信息
        1.  响应用户的 add 命令，提示用户输入收藏信息，此时无需要提供参数
        2.  处理用户提交的收藏信息，此时应该提供所有参数
        3.  校验接连的合法性，查询当前数据库系统是否包含当前拉链，调用方法检查链接详情并将收藏结果返回给用户
        :return:
        '''
        text = ''
        casual_entity = account.attribute(self.bot, 'title').get('entities')
        # 从工具箱调用 extract_links 方法提取文本中所有的链接
        urls = tools.extract_links(self.text)
        for url in urls:
            if not url.startswith('https://t.me/'):
                text += f'⚠️ {url} 不是一个合法的 telegram 分享链接\n'

            else:

                query = f'SELECT `render`, `created` FROM `{sql.table_shares}` WHERE `url`=%s'
                query = sql.query(sql.database, query, [url])
                if query and query[0] and query[0]['render']:
                    text += f"⚠️ {text}{url} 已由 {query[0]['render']}  于 {query[0]['created']} 添加\n"
                else:
                    text += f"🔔 {text}{url} 收录成功\n"
            casual_entity.append({'text': text, 'type': 'bold'})

        # 定义消息头，此消息应该是机器人的标题
        bot_title = account.attribute(self.bot, 'title').get('text')
        add_description = account.attribute(self.bot, 'add_description').get('text')

        text = f"{bot_title} >> 群组收录\n\n{add_description}\n\n{text}"
        entity = tools.format_entities(text, casual_entity)
        self.send_data.append([
            'editMessageText',
            {
                'chat_id': self.chat_id,
                'message_id': int(self.waitinput[-1]),
                'text': text,
                'disable_web_page_preview': True,
                'reply_markup': {'inline_keyboard': [[{'text': '返回', 'callback_data': f'start|0|0|0|0'}]]},
                'entities': entity
            },
            None
        ])


class SuperGroup(Message):

    def __init__(self, bot, data):
        '''
        初始化机器人补修
        :param bot: 机器人名，rules or search
        :param data: 消息主体

        :var self.rules: 储存当前群组的管理规则，由 self.init_rules() 方法赋值
        :var self.tasks: 一个函数容器，接收 register_tasks() 方法注册的函数，以便统一运行
        '''
        super().__init__(bot, data)
        self.bot_id = account.attribute(bot, 'id')
        self.bot_url = account.attribute(bot, 'url')
        self.rules = self.init_rules()
        self.is_admin = self.is_administrator()
        self.send_data = []

    def register_tasks(self):
        '''
        注册当前消息需要执行的规则检测任务。

        工作流程：
        1. 遍历当前实例中的所有属性；
        2. 找出被 @rule_handler 装饰器标记过的方法；
        3. 读取方法上的 rule_name / rule_order / rule_stop_on_hit；
        4. 根据 self.rules 判断该规则是否已经启用；
        5. 将启用的规则方法加入任务列表；
        6. 根据 rule_order 从小到大排序；
        7. 返回排序后的任务列表。

        返回的数据结构：
        [
            {
                'name': 'text',
                'order': 30,
                'stop_on_hit': True,
                'handler': self.parse_text
            },
            ...
        ]

        :return:
        '''
        tasks = []

        # dir(self) 可以拿到当前实例上所有属性和方法名
        # 包括 parse_text、parse_photo、main、permissions 等
        for attr_name in dir(self):

            # 根据属性名取出实际对象
            attr = getattr(self, attr_name)

            # 只处理可调用对象，也就是方法
            # 普通属性例如 self.text、self.rules、self.chat_id 会被跳过
            if not callable(attr):
                continue

            # 读取装饰器写入到方法上的规则名称
            # 没有被 @rule_handler 装饰的方法，这里会得到 None
            rule_name = getattr(attr, 'rule_name', None)



            # 如果没有 rule_name，说明它不是规则处理方法，跳过
            if not rule_name:
                continue

            # 如果 self.rules 中没有这条规则，说明当前群组没有启用该规则，跳过
            if not self.rules.get(rule_name):
                continue

            # 读取规则执行顺序
            # 如果装饰器没有提供 order，默认使用 200
            rule_order = getattr(attr, 'rule_order', 200)

            # 读取命中后是否停止执行后续规则
            # 如果装饰器没有提供 stop_on_hit，默认 True
            stop_on_hit = getattr(attr, 'rule_stop_on_hit', True)

            # 将规则处理方法加入任务列表
            tasks.append({
                'name': rule_name,
                'order': rule_order,
                'stop_on_hit': stop_on_hit,
                'handler': attr
            })

        # 按 order 升序排序，数字越小越先执行
        tasks.sort(key=lambda item: item['order'])

        return tasks

    def execute_rule_tasks(self):
        '''
        统一执行当前消息需要应用的规则检测任务。

        工作流程：
        1. 调用 register_tasks() 获取当前已启用规则的处理方法；
        2. 按照装饰器中的 order 顺序逐个执行；
        3. 每个规则方法返回 None，表示未命中违规；
        4. 每个规则方法返回 tuple/list，表示命中违规，例如：
                ('text', '消息违规【长度超出限制】')
                ('photo', '消息违规【包含了图片】')
        5. 命中违规后调用 self.rules_message() 生成处理动作；
        6. 如果该规则 stop_on_hit=True，则停止执行后续规则；
        7. 如果 stop_on_hit=False，则继续执行后续规则。

        注意：
        当前大多数规则命中后都应该停止继续检测，
        因为同一条消息通常只需要触发一次删除、警告、禁言等处理。

        :return:
        '''
        tasks = self.register_tasks()

        for task in tasks:
            handler = task['handler']
            stop_on_hit = task['stop_on_hit']
            # 执行具体规则方法，例如：
            # self.parse_text()
            # self.parse_photo()
            # self.parse_entities()
            result = handler()

            # 规则方法返回 None，表示没有命中违规，继续执行下一条规则
            if not result:
                continue

            # 规则方法返回结果，表示命中违规
            # 约定 result[0] 是规则名称，例如 text/photo/link
            # 约定 result[1] 是默认提示文本
            self.rules_message(result[0], result[1])

            # 如果当前规则命中后要求停止，则终止整个规则检测流程
            if stop_on_hit:
                break

    def group_message(self):
        '''
        主程序
        :return:
        '''
        if (self.new_chat_members or self.left_chat_member) and self.rules.get('newcomer'):

            # 响应群组中成员加入或离开的信息
            self.parse_members(self.rules.get('newcomer'))

        elif self.text == '签到' and self.rules.get('register'):

            result = register.parse_register(
                self.rules.get('register').get('regi_id'),
                self.chat_id,
                self.users,
                self.date,
                self.message_id,
            )
            self.send_data.extend(result)


        elif self.text == 'hello rules' and self.bot == 'rules':
            self.hello_rules()

        # elif self.is_admin and self.bot == 'rules':
        #
        #     log.warning(f'来自管理员的消息--{self.user_id}--{self.text}')
        #     return self.send_data

        elif self.rules and self.bot == 'rules':
            # 按 @rules_handler 装饰器定义的顺序批量执行规则检测方法

            self.execute_rule_tasks()

        elif self.bot == 'search' and self.entities:
            pass

        elif self.bot == 'search' and self.text and len(self.text) > 30:
            self.send_data.append([
                'sendMessage',
                {'text': f'{self.first_name} 搜索不得超过20个字符', 'chat_id': self.chat_id},
                None
            ])
        elif self.bot == 'search' and self.text:
            result = Search(self.user_id, ['SG', self.text, 'all', 0, self.user_id]).search_main()
            self.send_data.append([
                'sendMessage',
                {'chat_id': self.chat_id, 'reply_to_message_id': self.message_id, 'disable_web_page_preview': True, **result},
                None
            ])
        return self.send_data

    def hello_rules(self):
        '''
        响应 hello_wellwen 消息，这是一个特殊消息，当机器人在某个群组收到此消息时，
        1， 获取当前群组管理员，查看管理员列表是否包含了当前用户和机器人，如果是，则为当前群组创建规则数据
        2， 调用 Rules 类的 rules_start 方法将当前群组以按钮形式展示到与用户的私人聊天中
        :return:
        '''

        administrators = None
        entity = []
        bot_status = quick.chat_member(self.bot, self.bot_id, self.chat_id)

        if not bot_status:
            send_text = f"无法获取机器人状态，请确保机器人在当前群组中且是群组的管理员"

        elif bot_status.get('status') != 'administrator':
            send_text = f"机器人不是当前群组的管理员"

        else:
            administrators = quick.get_administrators(self.bot, self.chat_id)
            if not administrators:
                send_text = f"获取群组管理员信息失败"
            else:
                user_status = None
                for user in administrators:
                    if user.get('user').get('id') == self.user_id and user.get('status') in ['creator', 'administrator']:
                        user_status = user.get('status')

                if not user_status:
                    send_text = f"你不是当前群组管理员"
                else:
                    send_text = f'已为当前群组创建管理规则【点击此处编辑你的规则】'
                    entity.append({'type': 'text_link', 'text': '点击此处编辑你的规则', 'url': self.bot_url})

        self.send_data.append([
            'sendMessage',
            {
                'chat_id': self.chat_id,
                'text': send_text,
                'reply_to_message_id': self.message_id,
                'disable_web_page_preview': True,
                'entities': tools.format_entities(send_text, entity)
            },
            None
        ])

        if administrators and bot_status:
            administrators = json.dumps(administrators, ensure_ascii=False)
            bot_status = json.dumps(bot_status, ensure_ascii=False)

        query = (f"INSERT INTO {sql.table_rules} (`chat`,`title`,`type`,`administrators`,`bot_status`) VALUES (%s,%s,%s,%s,%s) "
                 f"ON DUPLICATE KEY UPDATE `title`=%s,`administrators`=%s,`bot_status`=%s")
        values = [self.chat_id, self.chat_title, self.chat_type, administrators, bot_status, self.chat_title, administrators, bot_status]
        sql.query(sql.database, query, values)

    def parse_members(self, rules):
        '''
        处理新成员加入群组的方法
        :return:
        '''
        if self.new_chat_members and rules['tip_join']:
            # 移除新人加入的系统消息
            self.send_data.append([
                'deleteMessage',
                {'chat_id': self.chat_id, 'message_id': self.message_id},
                None
            ])


        if self.left_chat_member and rules['tip_leave']:
            # 删除用户离群的系统提示
            self.send_data.append([
                'deleteMessage',
                {'chat_id': self.chat_id, 'message_id': self.message_id},
                None
            ])

        if self.new_chat_members and rules['verify_join']:

            # 查询当前群组的成员验证数据
            query = f'SELECT verify FROM {sql.table_constra} WHERE bot=%s and chat=%s'
            query = sql.query(sql.database, query, [self.bot_id, self.chat_id])
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
                    {'chat_id': self.chat_id, 'user_id': member_id, 'permissions': quick.permissions(True)},
                    None
                ])

                # 调用 toolbox.create_verify() 方法生成一条验证消息
                result = tools.create_verify(member, self.chat_id)
                # 向群组推送这条验证消息
                self.send_data.append([
                    'sendMessage',
                    {'chat_id': self.chat_id, **result},
                    None
                ])
            query = (f'INSERT INTO {sql.table_constra} (bot,chat,verify) VALUES (%s,%s,%s) '
                     f'ON DUPLICATE KEY UPDATE verify=%s, edited=NOW()')
            sql.query(sql.database, query, [self.bot_id, self.chat_id, json.dumps(verify_data), json.dumps(verify_data)])

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
                log.warning(f"【{self.chat_title}】{self.first_name} {self.last_name} 邀请了 {members_names}")

                text = rules['welcome']
                if text and text.find('@@') != -1:
                    # 如果欢迎语中包含了 @@ 的点位符，则将其替换成用户的名字（self.first_name）
                    text.replace('@@', members_names, 1)
                elif text:
                    text = f"{members_names} {text}"

                    # 创建富文本对象
                    entitles = tools.format_entities(text, entitle_pamrams)

                    # 构建请求对象并添加到请求容器
                    self.send_data.append([
                        'sendMessage',
                        {'chat_id': self.chat_id, 'text': text, 'entities': entitles},
                        None
                    ])

    @rule_handler('intelligent', order=10)
    def parse_intelligent(self):
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
        result = None
        intelligent = []

        query = f'SELECT `intelligent` FROM `{sql.table_constra}` WHERE `chat`=%s AND `bot`=%s'
        query = sql.query(sql.database, query, [self.chat_id, self.bot_id])
        if query and query[0]:
            intelligent = query[0].get('intelligent') or []

        intelligent.append([self.date, self.message_id, self.user_id, self.text if self.text else None])

        # 维护消息特征数据，
        if mode == '时长':
            # 超出时间的消息特征将被删除
            while len(intelligent) > 1 and (self.date - intelligent[0][0]) > (scope * 60):
                del intelligent[0]
        else:
            # 超出消息量的消息特征将被删除
            while len(intelligent) > scope:
                del intelligent[0]
        delete_message = []     # 储存可能需要删除的消息容器
        for index, nodes in enumerate(intelligent):
            if nodes[3] == self.text and nodes[2] == self.user_id:
                delete_message.append(index)

        if len(delete_message) > allow:
            delete_message_ids = []
            for index in delete_message:
                # 一旦涉嫌违规，则删除当前用户下的所有这类消息，包括之前的
                if intelligent[index][1]:
                    # 将要删除的消息ID追加到 delete_message_ids 并将当前记录的消息ID置 None,以免后续重复追加这些ID
                    delete_message_ids.append(intelligent[index][1])
                    intelligent[index][1] = None
            self.send_data.append([
                'deleteMessages',
                {'chat_id': self.chat_id, 'message_ids': delete_message_ids},
                None
            ])

            result = 'intelligent', '发布消息过于频繁'
        # 将最新的消息特征数据更新到 restriction 数据表
        query = (f'INSERT INTO `{sql.table_constra}` (`bot`,`chat`,`intelligent`) VALUES (%s,%s,%s) ON DUPLICATE '
                 f'KEY UPDATE `intelligent`=%s, `edited`=NOW()')
        sql.query(sql.database, query, [self.bot_id, self.chat_id, json.dumps(intelligent), json.dumps(intelligent)])

        return result

    @rule_handler('link', order=20)
    def parse_entities(self):
        '''
        解析富文本对象
        :return:
        '''

        if not self.entities or not self.rules.get('link'):
            return None
        for entitle in self.entities:
            if entitle['type'] == 'url' and self.rules.get('link'):
                return 'link', '消息违规【包含链接】'
            if entitle['type'] == 'bot_command' and self.text == '/start@ADDBOT true':
                return 'addbot',


        return None

    @rule_handler('text', order=30)
    def parse_text(self):
        '''
        解析文本消息
        :return:
        '''
        if not self.text or not self.rules.get('text'):
            return None
        length = self.rules.get('text')['len']
        height = self.rules.get('text').get('high')
        if length != 0 and len(self.text) > length:
            return 'text', f'消息违规【长度超出{length}字的长度限制】'
        elif height != 0 and self.text.count('\n') > height:
            return 'text', f'消息违规【行数超出{height}行的行数限制】'

        if self.rules.get('text').get('key'):
            key = self.check_key(self.text, self.rules.get('text').get('key').split(','))

            if key:
                return 'text', f'消息违规【包含了违规关键字"{key}"】'

        return None

    @rule_handler('photo', order=40)
    def parse_photo(self):
        '''

        :return:
        '''

        if self.rules.get('document') or self.rules.get('photo'):
            if self.photo or (self.document and self.document.get('mime_type').startswith('image/')):
                return 'photo', f'消息违规【包含了图片】'
        return None

    @rule_handler('video', order=50)
    def parse_video(self):
        '''

        :return:
        '''
        if not self.video or not self.rules.get('video'):
            return None
        return 'video', f'消息违规【包含了视频】'

    @rule_handler('voice', order=60)
    def parse_voice(self):
        '''

        :return:
        '''
        if not self.voice or not self.rules.get('voice'):
            return None
        return 'voice', f'消息违规【包含了语音】'

    @rule_handler('contact', order=70)
    def parse_contact(self):
        '''

        :return:
        '''
        if not self.contact or not self.rules.get('contact'):
            return None
        return 'contact', f'消息违规【包含了名片】'

    @rule_handler('document', order=80)
    def parse_document(self):
        '''

        :return:
        '''
        if not self.document or not self.rules.get('document'):
            return None
        return 'document', f'消息违规【包含了文件】'

    @rule_handler('forward', order=90)
    def parse_forward(self):
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
        mute_time = self.rules.get(rules_option).get('mute_time')  # 禁言措施中的禁言时长参数

        # 从受限制数据表（restriction）中获取当前群组违规用户的违规详情，并反序列化为 python 对象
        query = f'SELECT `rules_limit` FROM `{sql.table_constra}` WHERE `chat`=%s AND `bot`=%s AND `rules_limit` IS NOT NULL'
        rules_limit = sql.query(sql.database, query, [self.chat_id, self.bot_id])

        if rules_limit and rules_limit[0]:
            rules_limit = rules_limit[0].get('rules_limit') or {}
        else:
            rules_limit = {}
        limit_count = rules_limit.get(rules_option, {}).get(str(self.user_id))  # 获取当前用户的违规次数，此值可能为空
        if not limit_count:
            if rules_option not in rules_limit:
                rules_limit[rules_option] = {}  # 初始化为一个空字典
            limit_count = 0

        # 只要是违规消息就要删除(intelligent 规则在解析时已经构建了删除消息的请求)
        if rules_option != 'intelligent':
            self.send_data.append([
                'deleteMessage',
                {'chat_id': self.chat_id, 'message_id': self.message_id},
                None
            ])

        restrict_message = []   # 初始化一个请求容器，往下的代码可能会产生多个请求
        violator = self.first_name + self.last_name     # 定义违规者名称

        # 解析渐进式限制规则并应用到群组
        if level in ['stage_kick', 'stage_ban']:
            # 渐进式限制规则是一次警告二次禁言1小时三次禁言24小时四次移出或拉黑

            # 首次违规不会采取任何限制措施
            if limit_count == 0:
                # 设定警告语
                default_wan = f'{violator} {default_wan}，如多次违规将被移出群聊{"" if level == "stage_kick" else "并拉黑"}'

                # 记录用户的违规次数
                rules_limit[rules_option].update({str(self.user_id): 1})

            # 多次违规就要采取相应措施了，分别是禁言一小时和禁言24小时
            elif limit_count in [1, 2]:

                # 累计用户的违规记录
                rules_limit[rules_option].update({str(self.user_id): limit_count + 1})

                # 设定禁言时长(Unix时间戳)
                mute_unix = {1: self.date + 3600, 2: self.date + (24 * 3600)}[limit_count]

                # 设定警告语告知用户将被禁言到 until_date (将until_date Unix时间戳转换成直观的日期时间格式，包含时区信息)
                default_wan = f'{violator} {default_wan}，已被禁言至{wholetime.datetime(Unix=mute_unix)}'

                # 设定限制规则，将当前用户禁言到 until_date
                restrict_message.append([
                    'restrictChatMember',
                    {'chat_id': self.chat_id, 'user_id': self.user_id, 'permissions': quick.permissions(True), 'until_date': mute_unix},
                    None
                ])

            elif limit_count > 2:
                # 设定警告语
                default_wan = f'{violator} {default_wan}，已被被移出群聊{"" if level == "stage_kick" else "并拉黑"}'

                # 设定限制规则，从当前群组移出或拉黑该用户
                restrict_message.append([
                    ['kickChatMember' if level == 'stage_kick' else 'banChatMember', {'chat_id': self.chat_id, 'user_id': self.user_id}]
                ])
                # 将用户的违规记录删除，因为用户已不在当前群组中了
                del rules_limit[rules_option][str(self.user_id)]

        elif level == 'delete':
            default_wan = f'{violator} {default_wan}，此消息已被删除'

        elif level == 'mute':

            if limit_count >= allow:

                # 将当前用户违规记录删除
                if rules_limit.get(rules_option).get(str(self.user_id)):
                    del rules_limit[rules_option][str(self.user_id)]

                # 如果限制措施是禁言，则需要搂 mute_time 参数设置禁言时长，mute_time 是从群组的规则参数中提取
                # mute_time 有5种状态，永久，10分钟，1小时，24小时和一周，你需要用上述状态计算出禁言终止的时间戳
                mute_unix = {
                    '永久': 0,
                    '10分钟': self.date + 600,
                    '1小时': self.date + 3600,
                    '24小时': self.date + (24 * 3600),
                    '一周': self.date + (7 * 24 * 3600)
                }.get(mute_time)

                # 设定警告语告知用户将被禁言到 until_date (将until_date Unix时间戳转换成直观的日期时间格式，包含时区信息)
                until_time = wholetime.datetime(Unix=mute_unix)
                default_wan = f'{violator} {default_wan}，且多次违规，已被{"禁言" if mute_unix == 0 else "禁言到" + until_time}'

                # 对用户采取禁言的限制措施，
                restrict_message.append([
                    level,
                    {'chat_id': self.chat_id, 'user_id': self.user_id, 'permissions': quick.permissions(True), 'until_date': mute_unix}
                ])
            else:
                # 如果未达到规则次数上限，则更新违规次数
                rules_limit[rules_option].update({str(self.user_id): limit_count + 1})
                default_wan = f'{violator} {default_wan}，多次违规将被禁言'

        elif limit_count >= allow:
            # 将当前用户违规记录删除
            if rules_limit.get(rules_option).get(str(self.user_id)):
                del rules_limit[rules_option][str(self.user_id)]
            # 移出或拉黑用户，
            default_wan = f'{violator} {default_wan}，且多次违规，已被移出群聊{"" if level == "kick" else "并拉黑"}'
            restrict_message.append([
                f'{level}ChatMember',
                {'chat_id': self.chat_id, 'user_id': self.user_id, }
            ])
        else:
            rules_limit[rules_option].update({str(self.user_id): limit_count + 1})
            default_wan = f'{violator} {default_wan}，多次违规将被禁言'

        self.send_data.append([
            'sendMessage',
            {
                'chat_id': self.chat_id,
                'text': default_wan,
                'entities': tools.format_entities(
                    default_wan,
                    [
                        {'type': 'text_mention', 'text': violator, 'user': self.users}
                    ]
                )
            },
            {'delete': wholetime.unix() + 30}  # 此消息将在30秒后删除，timezone.unix() 会返回当前Unix时间戳
        ])

        # 将新的限制数据更新到 restriction 数据表
        query = (f'INSERT INTO `{sql.table_constra}` (`bot`,`chat`,`rules_limit`) VALUES (%s,%s,%s) '
                 f'ON DUPLICATE KEY UPDATE `rules_limit`=%s')
        rules_limit = json.dumps(rules_limit)
        sql.query(sql.database, query, [self.bot_id, self.chat_id, rules_limit, rules_limit])

        return self.send_data + restrict_message

    def is_administrator(self):
        '''
        检查用户是否管理员
        :return:
        '''
        if not self.rules:
            return False
        for admin in self.rules.get('administrators', []):
            if self.user_id == admin.get('user').get('id'):
                return admin.get('status')
        return False

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

        return Private(bot, datas['message']).private_message()

    return SuperGroup(bot, datas['message']).group_message()





if __name__ == '__main__':

    from test import debugging

    re = message_filter('rules', debugging.message_21)
    print(6666666666666666, re)



