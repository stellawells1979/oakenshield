

'''
群组管理机器人的管理规则实例
关于规则的描述：
    本文档由 config 文档中的 rules_example 参数定义一个规则框架，框架内包含了多个选项，本项目约定
    称之为规则，每个规则下面又包含多个子规则，称之为子规则，这些子规则都有相应的参数，称之为子规则参数，

    规则框架只是一个规则蓝本，所有规则和子规则，包括子规则参数都是默认，本文档的功能就是响应用户对规则
    的创建，编辑等操作，

'''

import copy
from utils.register import register
import config
from database import sql
from utils.tools import tools
from utils.quick import quick
from utils.account import account
import json
import logging
from logmanage import DailyLogManager

log = DailyLogManager('Rules', logging.ERROR, logging.INFO)


class Rules:

    '''
    向用户展示规则
    :var rules_description dict 规则描述，包含了规则框架，规则选项的描述
    :var support_param dict 提示用户输入参数的提示语句集合
    '''

    text_1 = '\n\r允许次数：允许此类消息的次数，0表示不允许'
    text_3 = ('\n\r处理规则：包括删除消息，禁言，移出，拉黑，叠加限制'
              '\n叠加限制是指 一次警告二次禁言1小时三次禁言24小时四次移出或拉黑')
    rules_description = {
        # 基础规则描述，当向用户展示规则框架是将同时展示此段文本描述
        'base_description': account.attribute('rules', 'start_description')['text'],

        'register': '签到管理，为群组设置一个签到规则，帮你统计群组的活跃程度，点击相应按钮可设置签到规则，机器人会每30分钟'
                    '轮循发布你的签到项目，你也可以点击【轮循时间】控制轮循发布频率。设置好后会弹出【启动签到按钮】，每个群组只'
                    '能运行一个签到规则，启动后无法修改签到规则',

        'newcomer': '新人管理规则，针对新加入群组的成员的管理规则，比如对新人的加入表示欢迎，人机验证，清除加入或退出时的系统提示消息',

        'text': f'文本消息规则设置\n\r长度：限制消息的字符数量\n\r高度：即消息的行数，限制行数可杜绝霸屏，'
                f'\n\r关键字词：设置你希望禁止展示的某些字符{text_1}{text_3}',

        'photo': f'设置是否允许用户在群组中发布图片消息，{text_1}{text_3}',

        'video': f'设置是否允许用户在群组中发布视频消息{text_1}{text_3}',

        'voice': f'设置是否允许用户在群组中发布音频（包括语音）消息{text_1}{text_3}',

        'link': f'设置是否允许用户在群组中发布包含链接的消息{text_1}{text_3}',

        'document': f'设置是否允许用户在群组中发布包含文件的消息{text_1}{text_3}',

        'multimedia': f'设置是否允许用户在群组中发布包含多媒体的消息{text_1}{text_3}',

        'contact': f'设置是否允许用户在群组中发布包含名片（联系人）的消息{text_1}{text_3}',

        'forward': f'设置是否允许转发消息到本群\n\r{text_1}{text_3}',

        'checkname': f'设置你认为的违规字符，机器人会检测用户名是否包含了这些字符，{text_1}{text_3}',

        'intelligent': '如果你对广告零容忍，此项设置非常有用，实时检测群组中的每一条消息，如果某个用户在'
                       '设定的时间范围内（或者在指定的消息数量内）多次发布相同的消息，则被视为违规\n'
                       '检测模式：可选择时间范围和消息量两种模式\n设置范围：设置时间范围或消息数量(时间单位：分钟)\n'
                       '设置次数：在指定的范围内允许发布相同消息的次数，超出此值则视为违规',
        'history': '查看和管理当前群组的签到项目，最多保存10个签到项目的数据，点击项目按钮可以看到指定签到项目的概况，如果需要更新详细'
                   '的签到数据可以点击【获取签到详细】，我们将向你发送一个包含全部签到数据的Excel数据表'
    }

    support_param = {
        # 当机器人识别到用户需要输入参数时向用户提示输入参数
        'welcome': '请输入对新人表示欢迎的语句，用两个@@做为新人用户名的点位符',
        'len': '请输入限制消息长度的参数',
        'high': '即行数，限制行数即限制了高度（霸屏消息），请输入限制消息行数的参数',
        'key': '请输入你要限制的关键字词，多个字词间用半角逗号分隔',
        'scope': '请输入{}参数',
        'mute': '请输入禁言时长',
        'warn': '请输入警告语，用两个@@做为用户名的点位符',
        'allow': '请设置允许次数，超出你设置的值会触发后面的处理规则',
        'count': '设置在指定的时间范围或消息数量内允许发布相同消息的次数',
        'describe': '请输入签到描述，长度120字以内',
        'period': '请输入签到周期，以天为单位，最多设置31天的签到周期',
        'regi_name': '你正在创建新的签到项目，请输入签到项目名称，长度20字以内',
        'timing': '请输入签到轮循时间，以分钟为单位，最多设置1440分钟（24小时）',
    }

    def __init__(self, chat, user, callback_data, message_id=None):
        '''
        初始化规则类，用于处理用户在群组中的各种规则设置和操作
        :param chat: 群组信息
        :param user: 用户信息
        :param callback_data: 回调数据
        :param message_id: 消息ID
        '''

        self.bot = account.rules['byname']
        self.bot_url = account.rules['url']
        self.title_text = account.rules['title']['text']
        self.user = user
        self.chat = chat
        self.message_id = message_id

        self.option = callback_data[1]
        self.details = callback_data[2]
        self.extra = callback_data[3]
        self.group = int(callback_data[4])

        self.rules = self.init_rules()      # 从规则数据表读取当前规则参数

        # 以下是用于构建请求的参数
        self.entity = []
        self.send_data = []     # 主参数，构建好请求储存在此容器中，本方法最终是返回此容器
        self.main_button = []      # 主键盘
        self.guid_button = []   # 导航按钮
        self.main_text = ''     # 主文本
        self.param_text = ''  # 用于描述规则参数的文本，本项目将此段文本格式化成 blockquote 的富文本
        self.extra_text = ''    # 这是个用于补充描述的文本变量，本项目将此文本内容格式化为 bold 的富文本

        # 为标题文本添加富文本样式
        self.entity.extend(account.rules['title']['entities'])

        # 设置一些控制函数
        self.change = False      # 此变量控制是否更新规则数据表

    def create_request(self):
        '''
        构建telegram bot 请求
        :return:
        '''
        # 将更新的规则写入规则数据表
        print(f"是否更新规则：{self.change}")
        if self.change:
            log.info(f"更新rules中的 {self.option} 规则")
            query = f"UPDATE `{sql.table_rules}` SET {self.option}=%s,edited=NOW() WHERE `chat`=%s"
            sql.query(sql.database, query, [json.dumps(self.rules), self.group])

        text = self.title_text + '\n'
        if self.main_text:
            text = text + '\n' + self.main_text
        if self.param_text:
            text = text + '\n' + self.param_text
            self.entity.append({'type': 'blockquote', 'text': self.param_text})
        if self.extra_text:
            text = text + '\n' + self.extra_text
            self.entity.append({'type': 'bold', 'text': self.extra_text})

        entities = tools.format_entities(text, self.entity)

        if not self.guid_button:
            log.error('Error：你没有设置返回按钮')

        keyboard = self.main_button + self.guid_button
        if len(keyboard) > 5:
            keyboard = [keyboard[i:i + 2] for i in range(0, len(keyboard), 2)]
        else:
            keyboard = [[item] for item in keyboard]

        self.send_data.append([
            'editMessageText' if self.message_id else 'sendMessage',
            {
                'chat_id': self.chat,
                **({'message_id': self.message_id} if self.message_id else {}),
                'text': text,
                **({'entities': entities} if entities else {}),
                'reply_markup': {'inline_keyboard': keyboard},
            },
            None
        ])
        return self.send_data

    def maintenance(self):
        '''

        :return:
        '''
        # 响应 self.extra 参数，此参数一般由返回按钮携带，告诉机器人执行一此额外的操作，比如清除机器人与用户的交互信息
        self.menu_extra()


        if self.option == 'prelude':
            # 响应刷群组列表的按钮
            self.prelude()

        elif self.option in ['register'] and self.details and self.details != '0':
            # 签到规则有一套独立的解析逻辑
            self.register_rules()

        # 响应规则参数设置按钮
        elif self.details and self.details != '0':
            # 调用 self.menu_details() 方法响应用户的设置操作并将用户的设置更新到规则数据表
            self.menu_details()

        elif self.option in ['0', 'administrators']:
            # 调用 self.menu_main() 方法向用户展示规则框架
            self.menu_main(self.group)

        # 响应用户点击的某个规则选项按键
        elif self.option:
            # 调用 self.menu_option() 方法向用户展示某个规则选项下的规则参数
            self.menu_option()

        return self.create_request()

    def menu_extra(self):
        '''
        响应可能的 self.extra 参数，此参数一般由返回按钮携带，告诉机器人执行一此额外的操作，比如清除机器人与用户的交互信息
        后续应该还有更多额外操作
        :return:
        '''
        # 重置用户与机器人的交互信息
        if self.extra == '1':
            query = f"UPDATE `{sql.table_interact}` SET `waitinput`=%s WHERE `bot`=%s and `user`=%s"
            sql.query(sql.database, query, [None, self.bot, self.user])

    def menu_details(self):
        '''
        响应用户的规则参数设置请求
        当用户点击了规则参数设置时，调用此方法响应用户的操作
        1. 当用户点击了 welcome，len，key 等需要用户自行提供参数的选项时，开发者应该
            从父类中调用对应的交互消息发送给用户,并将该交互属性更新到 interact 数据表
        2. 当用户点击了清除规则（clear） 时，你应该将当前群组规则框架中的对应规则选项清空
        3. 当用户点击的是可切换的开关式规则参数时，应调用父类的 self.switch_level() 方法
            为用户切换规则参数，并将新的规则参数更新到规则数据表
        最后根据参数决定你还需要向用户展示哪个界面，并附加相应的提示消息以增加与用户的交互体验
        :return:
        '''
        if self.details in self.support_param:

            waitinput = f'rules|{self.option}|{self.details}|{self.group}|{self.message_id}'
            # 将有效交互信息更新到数据库
            query = (f'INSERT INTO {sql.table_interact} (bot,user,waitinput) VALUES (%s,%s,%s) '
                     f'ON DUPLICATE KEY UPDATE waitinput=%s, edited=NOW()')
            sql.query(sql.database, query, [self.bot, self.user, waitinput, waitinput])

            # 设置补充发送文本提示用户输入参数，这些提示文本在父类中已经定义
            if not self.extra_text:
                self.extra_text = self.support_param[self.details]
                if self.details == 'scope':
                    self.extra_text = self.support_param[self.details].format(self.rules['mode'])

            # 设置返回按钮，此时的返回按钮应当携带一个告诉机器人清空交互信息的参数，即返回按键中 callback_data 键的字串值中的第四位为 1
            self.guid_button = [{'text': '返回', 'callback_data': f'rules|0|0|1|{self.group}'}]

        # 响应用户的切换式规则选项
        elif self.details in ['level', 'tip_join', 'tip_leave', 'mute_time', 'mode', 'verify_join']:

            # 调用 recursive_switch 类方法切换规则参数
            recursive = self.recursive_switch(self.details, self.rules.get(self.details))

            self.rules.update({self.details: recursive})

            # 设置补充发送文本提示用户操作结果
            self.extra_text = f'{config.translation[self.details]}： 设置成功'
            if recursive == 'mute':
                self.extra_text = '点击【禁言时长】按钮设置禁言时长'

            self.change = True

        elif self.details == 'clear':
            # 响应用户清空规则选项
            self.rules = config.rules_example[self.option]

            # 设置补充发送文本提示用户操作结果
            self.extra_text = '已清空当前规则'

            self.change = True


        self.menu_option()

    def menu_option(self):
        '''
        向用户展示规则选项下的规则参数，此方法有可能被其它方法调用
        1. 调用父类的 uphold_rules() 方法获取 option 规则的参数选项展示给用户,
        2. 将参数集以文本消息的形式向用户展示并展示相应的设置的功能按钮
        3. 将相应规则描述文本赋值给 self.send_text
        4. 编辑机器人标题文本（增加规则步骤）
        :return:
        '''
        param_text_head = '📌当前规则参数\n\n'    # 规则参数的前置文本
        self.param_text = ''
        for key, value in self.rules.items():
            if key in ['administrators', 'regi_id']:
                continue
            if key == 'mute_time' and self.rules.get('level') != 'mute':
                # 如果处理规则不是禁言，就不应显示禁言时长参数
                continue
            # 构建规则参数文本
            if key == 'regi_count':
                param_text_head = '📌当前群组还没有创建任何签到项目\n'
                if value > 0:
                    param_text_head = f"📌当前群组共有{value}个签到项目，"
                    param_text_head += f"{'一个进行中的签到项目' if self.rules.get('regi_id') else '没有进行中的签到项目'}\n\n"
                continue
            if type(value) == bool:
                disp_value = '🟢' if value else '🔘'
            elif key in ['origin', 'expired'] and value:
                disp_value = f"{value} {config.time_zone}"
            else:
                disp_value = "" if value is None else config.translation.get(value, value)

            self.param_text += f'{config.translation[key]}： {disp_value}\n'

        # 构建完整的规则参数文本

        self.param_text = param_text_head + self.param_text.strip()

        # 构建规则键盘
        for key, value in config.rules_keyboard.get(self.option, {}).items():

            if key == '禁言时长' and self.rules.get('level') != 'mute':
                continue
            if key == '启动签到' and self.rules.get('status') != 'Read':
                continue
            if key == '关闭签到' and self.rules.get('status') != 'Run':
                continue

            self.main_button.append({
                'text': key, 'callback_data': f'rules|{self.option}|{value}|0|{self.group}'
            })

        # 在确保其它方法中没有设置导航按钮的情况下设置导航按钮
        if not self.guid_button:
            self.guid_button = [{'text': '返回', 'callback_data': f'rules|0|0|1|{self.group}'}]

        # 将相应规则描述文本赋值给 self.send_text
        if not self.main_text:
            self.main_text = self.rules_description[self.option]

    def menu_main(self, group):
        '''
        生成主菜单，包括键盘属性
        1. 调用父类的规则框架，生成由键盘阵列组成的界面向用户展示规则主菜单，本方法定义的键盘阵列为两个按钮为一行，
        2. 将规则描述文本赋值给 self.send_text
        3. 如果是响应用户的更新管理员操作，还需要调用 self.get_administrator() 将群组的管理员更新到数据表
            并设置补充文本向用户表明更新结果
        :return:
        '''

        for key in config.rules_example.keys():

            self.main_button.append({
                'text': config.translation[key],      # 向用户展示翻译后的中文文本
                'callback_data': f'rules|{key}|0|0|{group}'
            })

        self.main_button.append({'text': '帮助', 'callback_data': f'help|0|0|0|{self.group}'})

        # 设置导航按钮
        self.guid_button = [{'text': '返回', 'callback_data': f'start|0|0|0|{self.group}'}]

        self.main_text = self.rules_description['base_description']
        # 额外操作，如果用户点击了更新管理员按钮
        if self.option == 'administrators':
            admin = quick.get_administrators(self.bot, self.group)
            self.extra_text = '❌ 更新管理员失败，请重试'
            if admin:
                self.change = True
                self.rules = admin
                self.extra_text = '✅ 更新管理员成功'

    def register_rules(self):
        '''
        将签到规则做为一个单独的模块来解析
        :return:
        '''

        if self.details == 'history':
            # 此步骤与规则无关，你必须明确将self.change置Flase，并独立构建键盘以及相应的请求参数，不再走self.menu_option()构建请求参数
            # 此步骤有可能返回文件对象

            result = register.history(self.chat, self.group, self.extra)
            # 返回主键盘，导航键盘，参数文本，额外文本以及可能存在的文件对象
            self.main_button, self.guid_button, self.param_text, self.extra_text, file_obj = result

            # 构建主文本
            self.main_text = self.rules_description['history']

            # 添加发送文件的请求
            if file_obj:
                self.send_data.append(file_obj)

            # 此步骤与规则参数无关，你必须将self.change置Flase，避免将历史数据履盖规则参数
            self.change = False
        else:

            result = register.set_register(self.user, self.group, self.message_id, self.rules, self.details)
            # 返回更新后的规则和额外的说明文本
            self.rules, self.extra_text = result

            # 设置返回按钮，此时的返回按钮应当携带一个告诉机器人清空交互信息的参数，即返回按键中 callback_data 键的字串值中的第四位为 1
            self.guid_button = [{'text': '返回', 'callback_data': f'rules|0|0|1|{self.group}'}]
            self.change = True
            self.menu_option()

    def prelude(self):
        '''
        响应用户刷新群组信息的按钮
        从数据查询所有群组，尝试获取这些群组的管理员信息，查看群组管理员列表是否包含当前用户及机器人

        :return:
        '''

        # 从规则数据表中提取所有群组信息
        query = f"SELECT `chat`,`title`,`type`,`administrators`,`bot_status` FROM {sql.table_rules}"
        groups = sql.query(sql.database, query, None) or []
        if not self.extra_text:
            self.extra_text = ('⚠️ 没有查找到你的群组，请确保你是群组的管理员，且已将机器人添加到群组并赋予机器人管理员权限\n'
                               '然后点击【刷新群组列表】，或点击【帮助】查看如果使用本服务')
        for group in groups:
            if not group or not group.get('bot_status'):
                continue

            bot_status = group.get('bot_status', {}).get('status')
            if bot_status != 'administrator':
                continue
            administrators = group.get('administrators') or []

            for admin in administrators:
                if admin.get('status') in ['administrator', 'creator'] and admin.get('user').get('id') == self.user:
                    text = group.get('title')
                    emoji = '📢' if group.get('type') == 'channel' else '👥'
                    self.main_button.append({
                        'text': f"{emoji} {text if len(text) < 15 else text[:12] + '...'}",
                        'callback_data': f"rules|0|0|0|{group.get('chat')}"
                    })
        if self.main_button:
            self.extra_text = '当前为你找到以下群组，点击可查看群组的规则详情，如果没有你期望的群组，请点击【帮助】按钮查看解决方案'

        self.guid_button = [
            {'text': '刷新群组列表', 'callback_data': 'rules|prelude|0|0|0'},
            {'text': '添加机器人到群组', 'url': f'{self.bot_url}?startgroup=true'},
            {'text': '帮助', 'callback_data': 'help|0|0|0|0'},
            {'text': '返回', 'callback_data': 'start|0|0|0|0'}
        ]

    def set_rules_params(self, params):
        '''
        应用规则设置参数
        接收由 Message 函数传递的参数处理用户以消息形式发来的设置参数，参规则进行编辑更新，并最终返回一个消息对象给 Message 函数

        只有校验成功的参数才会被写入规则数据表

        :param params 用户传递的参数
        :return:
        '''
        params = self.check_rules_params(params)

        if params is not None:
            # 更新相应规则选项参数
            if self.option == 'register':
                # 签到规则的设置需要与签到项目的的参数一致，所有要走独立的设置逻辑
                self.rules = register.set_regiser_param(self.rules, self.details, params)
            else:
                self.rules.update({self.details: params})
            # 设置补充文本提示用户设置成功
            self.extra_text = f'{config.translation[self.details]}： 设置成功'

            # 明确需要将新的规则参数更新到规则数据表
            self.change = True

        # 此参数在本方法中必须置 None 否则影响发送文本格式
        self.details = None

        # 返回 maintenance 方法生成的消息参数，此结果是返回给message类的
        return self.maintenance()

    def check_rules_params(self, params):
        '''
        检查参数是否符合预期
        :param params:
        :return:
        '''
        if self.is_empty_or_whitespace(params):
            # 检测空串
            params = None
            self.extra_text = '无法为你更新设置，参数为空'

        if self.details in config.rules_param_int and not params.isnumeric():
            # 检查参数类型是否符合预期，一些选项只接收数值整型参数
            params = None
            self.extra_text = '无法为你更新设置，此选项只接收数值整型参数'

        elif self.details in config.rules_param_int:
            # 格式化成整型参数
            params = int(params)
            if self.details == 'period' and params > 31:
                params = None
                self.extra_text = '最大的签到周期是31天'

        elif self.details in config.rules_param_restrict and len(params) > config.rules_param_restrict[self.details]:
            # 你应该对用户自定义的描述语句适当限制
            params = None
            self.extra_text = f'{self.details} 参数长度不得超过{config.rules_param_restrict[self.details]}字'

        return params

    def init_rules(self):
        '''
        初始化当前群组的规则
        定义群组标题
        :return:
        '''

        if self.option in ['0', 'prelude'] or not self.group:
            # 如果是刷群组的操作，则无需执行往下的代码
            return None

        filed = '`title`' if self.option == '0' else f'`title`, `{self.option}`'

        # 按 filed 字段查询规则，
        query = f"SELECT {filed} FROM `{sql.table_rules}` WHERE `chat`=%s"
        result = sql.query(sql.database, query, [self.group])
        if not result:
            self.option = 'prelude'
            self.details = '0'
            self.extra_text = '⚠️ 没有查询到当前群组规则，请查看帮助了解怎样使用机器人服务'
            return None

        # 构建机器人消息的标题，如果群组标题超长则截取前面部分字符
        title = result[0].get('title')
        self.title_text = f"{self.title_text}  >>  {title if len(title) < 15 else title[:12] + '...'}"
        self.title_text += f'  >>  {config.translation.get(self.option)}'


        result = result[0].get(self.option)

        if not result:
            # 如果此项规则为空，则返回默认的规则参数
            return copy.deepcopy(config.rules_example[self.option])

        if self.option == 'administrators':
            return result

        if self.option == 'register':
            # 签到规则的参数必须与签到数据表中的参数一致，
            print(result)
            result = register.register_status(self.group, result)

        result = {key: result[key] for key in config.rules_example[self.option].keys()}
        return result

    @classmethod
    def recursive_switch(cls, details, recursive):
        '''
        切换参数
        :param details:
        :param recursive:
        :return:
        '''

        switch_example = {
            'mute_time': [0, '10分钟', '1小时', '24小时', '一周'],
            'mode': [None, '消息数量', '时间范围'],
            'level': [None, 'delete', 'mute', 'kick', 'ban', 'stage_kick', 'stage_ban'],
            'status': ['begin', 'RUN']
        }
        if details in ['tip_join', 'tip_leave', 'verify_join']:
            return False if recursive else True
        switchs = switch_example[details]
        for row, switch in enumerate(switchs):
            if recursive == switchs[-1]:
                return switchs[0]
            if switch == recursive:
                return switchs[row + 1]

        raise 'Error：没有设置切换参数'

    @classmethod
    def is_empty_or_whitespace(cls, text):
        """
        检测字符串是否为空或仅包含空白字符（空格、制表符等）。
        """
        return text.strip() == ''  # 如果去除空白后是空字符串，就返回 True


if __name__ == '__main__':

    rules = Rules(123456789, 2182545792, ['rules' ,'register', '0', '0', -1003606614850])



















