

'''
群组管理机器人的管理规则实例
关于规则的描述：
    本文档由 config 文档中的 rules_example 参数定义一个规则框架，框架内包含了多个选项，本项目约定
    称之为规则，每个规则下面又包含多个子规则，称之为子规则，这些子规则都有相应的参数，称之为子规则参数，

    规则框架只是一个规则蓝本，所有规则和子规则，包括子规则参数都是默认，本文档的功能就是响应用户对规则
    的创建，编辑等操作，

'''
import copy

from utils.register import Register
import run_config
from database import sql
from utils.toolbox import toolbox
from utils.account import account
import json
import logging
from logmanage import DailyLogManager

log = DailyLogManager('Rules', logging.ERROR, logging.INFO)

# 初始化一个签到管理器
mage_register = Register(sql.table_register)

class FormulateRules:

    '''
    缶用户展示规则
    :var rules_description dict 规则描述，包含了规则框架，规则选项的描述
    :var input_description dict 提示用户输入参数的提示语句集合
    '''

    text_1 = '\n\r允许次数：当用户发布违规消息次数超限会执行处理规则，默认0，立即执行'
    text_3 = ('\n\r处理规则：包括删除消息，禁言，移出，拉黑，叠加限制'
              '\n叠加限制：一次警告二次禁言1小时三次禁言24小时四次移出或拉黑')
    rules_description = {
        # 基础规则描述，当向用户展示规则框架是将同时展示此段文本描述
        'base_description': account.attribute('rules', 'start_description')['text'],

        'register': '签到管理，为群组设置一个签到规则，帮你统计群组的活跃程度，点击相应按钮可设置签到规则，'
                    '设置好后会弹出【启动签到按钮】，每个只能运行一个签到规则，启动后无法修改签到规则',

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
                       '设置次数：在指定的范围内允许发布相同消息的次数，超出此值则视为违规'
    }

    input_description = {
        # 当机器人识别到用户需要输入参数时向用户提示输入参数
        'welcome': '请输入对新人表示欢迎的语句，用两个@@做为新人用户名的点位符',
        'len': '请输入限制消息长度的参数',
        'high': '即行数，限制行数即限制了高度（霸屏消息），请输入限制消息行数的参数',
        'key': '请输入你要限制的关键字词，多个字词间用全角逗号分隔',
        'scope': '请输入{}参数',
        'restrictChatMember': '请输入禁言时长',
        'warn': '请输入警告语，用两个@@做为用户名的点位符',
        'allow': '请设置允许次数，超出你设置的次数据 会触发后面的处理规则',
        'count': '设置在指定的时间范围或消息数量内允许发布相同消息的次数',
        'explain': '请输入签到描述',
        'period': '请输入签到周期，以天为单位，最多设置31天的签到周期'
    }

    def __init__(self):

        '''
        data 参数定义了用户操作规则设置的详细步骤

        '''
        self.bot = account.rules['byname']
        self.bot_id = account.rules['id']
        self.bot_title = account.rules['title']['text']
        self.predefined_entities = account.rules['title']['entities']

    @classmethod
    def recursive_switch(cls, details, recursive):
        '''
        切换参数
        :param details:
        :param recursive:
        :return:
        '''

        switch_example = {
            'restrict': ['10分钟', '1小时', '24小时', '一周', '永久'],
            'mode': ['消息数量', '时间范围'],
            'level': ['deleteMessage', 'restrictChatMember', 'kickChatMember', 'banChatMember', 'gradually(kick)', 'gradually(block)'],
            'status': ['begin', 'RUN']
        }
        if details in ['tip_join', 'tip_leave', 'verify_join']:
            return False if recursive else True
        switchs = switch_example[details]
        for row, switch in enumerate(switchs):
            if not recursive or recursive == switchs[-1]:
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


class Rules(FormulateRules):
    '''
        规则应用，响应用户的规则管理消息
        需要构建以下组件：
        1. 构建请求对象中的请求文本（self.send_text）,该对象由三部分组成
            1.1 机器人标题文本（self.bot_title），顶置天消息，由父类初始化，并有可能在某个方法中被重新赋值
            1.2 请求文本主体（self.send_text）,由当前类初始化，在调用方法处理时会赋与不同的值
            1.3 补充说明文本（self.send_supplement），由当前类初始化，追加在主体文本后面，主要直到提示用户的作用
            1.4 最终的主体文本在 apply_rules 方法中拼接，并添加富文本效果
        2. 构建富文本对象（self.predefined_entities），由当前类初始化，特别说明，此参数并非最终的 telegram entities对象，
            它只是储存了预定义的富文本实体，最后调用 toolbox 工具箱的 format_entities 方法构建 entities 实体
        3. 构建键盘阵列（self.inline_keyboard）
        '''

    def __init__(self, chat, user, callback_data, message_id=None):

        super().__init__()

        self.user = user
        self.chat = chat
        self.message_id = message_id
        self.option = callback_data[1]
        self.details = callback_data[2]
        self.reset = int(callback_data[3])
        self.group = int(callback_data[4])

        self.group_title = None
        self.change = False
        self.rules = self.init_rules()
        self.send_data = []
        self.inline_keyboard = []
        self.guide_button = []
        self.send_supplement = ''
        self.send_text = ''
        self.rules_param_text = ''





    def main(self):
        '''
        主方法，解析规则参数，调用相应方法定义消息文本和键盘阵列，
        本函数会直接生成一个完整的消息对象，可使用合法身份向 telegram 服务器请求
        1. 当 self.details 不等 0 时，说明用户已经点击了某个规则选项下的规则参数，本方法会
            调用 self.menu_details() 方法响应用户的设置操作并将用户的设置更新到规则数据表
        2. 当 self.option 为 0 时，本方法会调用 self.menu_main() 方法向用户展示规则框架
        3. 当 self.option 不等 0 时，说明用户点击了规则框架下的某个规则选项，本方法会调用
            self.menu_option() 方法向用户展示某个规则选项下的规则参数,
            !!!! 这里有个特殊，如果用户点击了更新群组管理员（administrator）规则选项时，由于
            该规则项只是个功能，只需调用方法将群组的管理员更新到规则数据表，并提示用户更新结果、
            但你依然需要向用户展示规则框架界面而不是当前规则选项下的规则参数
        :return:
        '''

        # 响应 self.reset 此参数一般由返回按钮携带，告诉机器人执行一此额外的操作，比如清除机器人与用户的交互信息
        if self.reset != 0:
            # 重置用户与机器人的交互信息
            if self.reset == 1:
                # 重置等待用户输入参数的交互信息为 None
                query = f"UPDATE `{sql.table_interact}` SET waitinput=%s WHERE bot={self.bot_id} and user={self.user}"
                sql.query(sql.base_database, query, [None])

        # 响应开始使用规则机器人按钮
        if self.option == 'prelude':
            self.rules_prelude()

        # 响应规则参数设置按钮
        elif self.details and self.details != '0':
            # 调用 self.menu_details() 方法响应用户的设置操作并将用户的设置更新到规则数据表
            self.menu_details(self.group)

        # 在响应用户点击的某个规则选项按键之前，你必须提前识别用户是否点击了【更新管理员】选项，
        # 因为【更新管理员】选项并没有详细的规则参数，你应该执行更新管理员操作并提示用户操作结果，
        # 且依旧是向用户展示规则框架，当然如果用户未点击任何规则选项按钮（self.option=0）的情况
        # 下，你必须向用户展示规则框架的
        elif self.option in ['0', 'administrators']:
            # 调用 self.menu_main() 方法向用户展示规则框架
            self.menu_main(self.group)

        # 响应用户点击的某个规则选项按键
        elif self.option:
            # 调用 self.menu_option() 方法向用户展示某个规则选项下的规则参数
            self.menu_option()

        '''
        # 以下是汇总处理环节，前面的代码逻辑已经完成对相应实例属性的赋值定义
        # 汇总处理就是将这些实例属性拼接成请求实体，确保向 telegram 服务器请求成功
        '''
        if self.change:
            query = f"UPDATE `{sql.table_rules}` SET {self.option}=%s,edited=NOW() WHERE `chat`=%s"
            sql.query(sql.base_database, query, [json.dumps(self.rules), self.group])

        # 对请求实体预处理（拼接请求文本，添加文本的美化效果等操作）
        self.send_text = f"{self.bot_title}\n\n{self.send_text}"

        if self.rules_param_text:
            self.send_text = f"{self.send_text}\n{self.rules_param_text}"
            self.predefined_entities.append({'type': 'blockquote', 'text': self.rules_param_text})


        if self.send_supplement:
            # 为补充文本添加粗体文本样式，增加交互体验（当前只是预定义参数，需调用其它方法格式化成 entitie 对象）
            self.predefined_entities.append({'type': 'bold', 'text': self.send_supplement})
            self.send_supplement = '🔔 ' + self.send_supplement
            if self.rules_param_text:
                self.send_text = f"{self.send_text}{self.send_supplement}"
            else:
                self.send_text = f"{self.send_text}\n\n{self.send_supplement}"
        if self.guide_button:
            self.inline_keyboard += self.guide_button
        else:
            log.error('Error：你没有设置返回按钮')

        # 构建键盘阵列，如果按钮超过数量超过5个，则每行显示两个按钮
        if len(self.inline_keyboard) > 5:
            inline_keyboard = [self.inline_keyboard[i:i + 2] for i in range(0, len(self.inline_keyboard), 2)]
        else:
            inline_keyboard = [[item] for item in self.inline_keyboard]

        # 构建请求对象
        result = {
            'chat_id': self.chat,
            **({'message_id': self.message_id} if self.message_id else {}),
            'text': self.send_text,
            'reply_markup': {'inline_keyboard': inline_keyboard},
        }

        # 如果你对请求消息的文本部分添加了富文本属性，你还需要调用 toolbox 工具箱的 format_entities 方法
        # 构建完整的 entities 对象并追加到请求对象中
        if self.predefined_entities:
            entities = toolbox.format_entities(self.send_text, self.predefined_entities)
            result.update({'entities': entities})

        self.send_data.append([
            'editMessageText' if self.message_id else 'sendMessage',
            result,
            None
        ])


        # 返回请求对象
        return self.send_data

    def menu_details(self, group):
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
        # 响应用户自行提供参数的规则选项
        if self.details in ['welcome', 'len', 'high', 'key', 'scope', 'allow', 'count', 'explain', 'period']:
            # 生成机器人与用户的交互信息并更新到数据库
            waitinput = f'rules|{self.option}|{self.details}|{self.group}|{self.message_id}'
            query = (f'INSERT INTO {sql.table_interact} (bot,user,waitinput) VALUES (%s,%s,%s) '
                     f'ON DUPLICATE KEY UPDATE waitinput=%s, edited=NOW()')
            sql.query(sql.base_database, query, [self.bot_id, self.user, waitinput, waitinput])


            # 设置补充发送文本提示用户输入参数，这些提示文本在父类中已经定义
            if not self.send_supplement:
                if self.details == 'scope':
                    self.send_supplement = self.input_description[self.details].format(self.rules['mode'])
                else:
                    self.send_supplement = self.input_description[self.details]

            # 设置返回按钮，此时的返回按钮应当携带一个告诉机器人清空交互信息的参数，返回按键
            # 中 callback_data 键的字串值中的第四位为 1
            self.guide_button = [{'text': '返回', 'callback_data': f'rules|0|0|1|{group}'}]


        # 响应用户清空规则选项
        elif self.details == 'clear':

            self.rules = run_config.rules_example[self.option]
            if self.option == 'register':
                query = f'UPDATE {sql.table_register} SET `status`=%s WHERE `chat`=%s'
                sql.query(sql.base_database, query, ['End', self.group])

            self.change = True
            # 设置补充发送文本提示用户操作结果
            self.send_supplement = '已清空当前规则'

        elif self.details == 'begin':
            self.rules.update({'status': 'Run'})
            # 在租到数据表中创建一个签到实例
            mage_register.create_register(
                self.group,
                self.bot_id,
                [self.rules['period'], self.rules['explain'], self.rules['status']]
            )
            self.change = True

            if not self.guide_button:
                self.send_supplement = '已启动签到'

        # 响应用户的切换式规则选项
        elif self.details in ['level', 'tip_join', 'tip_leave', 'restrict', 'mode', 'verify_join']:
            # 调用 recursive_switch 类方法切换规则参数
            recursive = self.recursive_switch(self.details, self.rules.get(self.details))

            self.rules.update({self.details: recursive})
            self.change = True

            # 设置补充发送文本提示用户操作结果
            self.send_supplement = f'{run_config.translation[self.details]}： 设置成功'
            if recursive == 'restrictChatMember':
                self.send_supplement = '点击【禁言时长】按钮设置禁言时长'

        # 你还需要调用 menu_option 方法向用户展示其它设置选项
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
        # 这段代码逻辑设定了签到规则的按钮显示规则，详细设置应该显示或隐藏哪些按钮
        if self.option == 'register':
            if self.rules['status'] == 'Run':
                # 如果签到规则正在进行，则隐藏【启动按钮】
                self.rules['begin'] = 'disabled'

            elif bool(self.rules['period']) and bool(self.rules['explain']):
                # 当这两个参数有效时，将签到状态设为就绪（Ready），并将启动按键（begin）设为可见（display）
                self.rules['status'] = 'Ready'
                self.rules['begin'] = 'display'

            else:
                # 否则将签到状态设为未知（Unknown），并隐藏将启动按键（begin）隐藏（disabled）
                self.rules['status'] = None
                self.rules['begin'] = 'disabled'
        for key, value in self.rules.items():

            # 每个 key 是一个按钮，但有些按钮需要根据其值（value）来决定显示或隐藏
            # status 签到规则中的状态按钮是不显示的，disabled 通用的隐藏值，
            display_button = True
            display_param_text = True
            if key in ['status'] or value in ['disabled']:
                display_button = False
            if key == 'restrict':
                if self.rules['level'] == 'restrictChatMember':
                    if not self.send_supplement:
                        self.send_supplement = '点击【禁言时长】按钮设置禁言时长'
                else:
                    display_button = False
                    display_param_text = False

            # 定义规则参数文本（self.rules_param_text），当参数值为 None 或者 0 时，不显示该参数和参数值
            if not value or key in ['view', 'begin', 'clear']:
                display_param_text = False

            if display_button:
                # 针对按钮的显示规则，其中 disabled 的逻辑是不管任何按钮，只要是 disabled 就将该按钮隐藏
                # RUN 的逻辑是当签到规则在运行状态是不会显示启动按钮
                self.inline_keyboard.append({
                    'text': f'{run_config.translation[key]}', 'callback_data': f'rules|{self.option}|{key}|0|{self.group}'
                })

            if display_param_text:
                self.rules_param_text += f'{run_config.translation[key]}： {run_config.translation.get(value, value)}\n'

        # 在确保其它方法中没有设置导航按钮的情况下设置导航按钮
        if not self.guide_button:
            self.guide_button = [{'text': '返回', 'callback_data': f'rules|0|0|1|{self.group}'}]

        # 将相应规则描述文本赋值给 self.send_text
        if not self.send_text:
            self.send_text = self.rules_description[self.option]

        # 更新机器人标题文本
        self.bot_title += f' >> {run_config.translation[self.option]}'

    def menu_main(self, group):
        '''
        生成主菜单，包括键盘属性
        1. 调用父类的规则框架，生成由键盘阵列组成的界面向用户展示规则主菜单，本方法定义的键盘阵列为两个按钮为一行，
        2. 将规则描述文本赋值给 self.send_text
        3. 如果是响应用户的更新管理员操作，还需要调用 self.get_administrator() 将群组的管理员更新到数据表
            并设置补充文本向用户表明更新结果
        :return:
        '''

        for key in self.rules:

            self.inline_keyboard.append({
                'text': run_config.translation[key],      # 向用户展示翻译后的中文文本
                'callback_data': f'rules|{key}|0|0|{group}'
            })

        self.inline_keyboard.append({'text': '帮助', 'callback_data': f'help|0|0|0|{self.group}'})

        # 设置导航按钮
        self.guide_button = [{'text': '返回', 'callback_data': f'start|0|0|0|{self.group}'}]

        # 额外操作，如果用户点击了更新管理员按钮
        self.send_text = self.rules_description['base_description']

        if self.option == 'administrators':
            admin = toolbox.get_administrator(self.bot, self.group)
            if admin:
                # 如果获取到管理员参数则调用父类的 uphold_rules() 方法将管理员更新到 rules 数据表
                query = f'UPDATE `{sql.table_rules}` SET administrators=%s WHERE `chat`=%s'
                sql.query(sql.base_database, query, [json.dumps(admin), group])
                self.send_supplement = '更新管理员成功'
            else:
                self.send_supplement = '更新管理员失败，请重试'

    def apply_rules_params(self, params):
        '''
        应用规则设置参数
        接收由 Message 函数传递的参数处理用户以消息形式发来的设置参数
        格式化交互信息和调用 data 重新初始化某些类属性
        依据交互信息规则对用户发送来的参数进行校验，只有校验成功的参数才会被写入规则数据表

        :param params 参数集，包含了聊天的参数，由 Message 函数传递
        :return:
        '''
        # 如果用户尝试更改签到规则，则检查当前签到规则是否正在进行，如果是，则提示用户无法更改进行中的签到规则
        if self.option == 'register' and self.rules['status'] == 'RUN':
            self.send_supplement = '无法修改正在进行的签到项目'

        elif self.details in ['len', 'high', 'scope', 'restrictChatMember', 'allow', 'count', 'period']:
            if not params.isnumeric():
                # 此选项只接收数值整型参数
                self.send_supplement = '无法为你更新设置，此选项只接收数值整型参数'
            else:
                # 格式化成整型参数
                params = int(params)

                if self.details == 'period' and params > 31:
                    self.send_supplement = '最大的签到周期是31天'
                else:
                    self.change = True

        elif self.is_empty_or_whitespace(params):
            # 检测空串
            self.send_supplement = '无法为你更新设置，参数为空'

        elif self.details in ['welcome', 'warn', 'key', 'explain']:
            # 你应该对用户自定义的描述语句适当限制
            if self.details in ['welcome', 'warn'] and len(params) > 150:
                self.send_supplement = '长度不得超过150字'
            else:
                self.change = True

        if self.change:
            # 更新相应规则选项参数并将更新好的规则参数更新到数据表
            self.rules.update({self.details: params})


            # 设置补充文本提示用户设置成功
            self.send_supplement = f'{run_config.translation[self.details]}： 设置成功'


        # 此参数在本方法中必须置 None 否则影响发送文本格式
        self.details = None

        # 返回 apply_rules 方法生成的消息参数
        return self.main()

    def rules_prelude(self):
        '''
        :return:
        '''
        # 查询数据表是否储存当前用户的群组（在 rules 表中查询所有群组的管理员，看管理员列表中是否有当前用户）
        query = f"SELECT `chat`, `title`, `administrators` FROM rules"
        groups = sql.query(sql.base_database, query, None)


        for group in groups:
            if not group.get('administrators'):
                continue
            users = json.loads(group.get('administrators'))
            for u in users:
                if u['user']['id'] == self.user:

                    self.inline_keyboard.append({
                        'text': group.get('title') if len(group.get('title')) < 15 else group[1][:12] + '...',
                        'callback_data': f"rules|0|0|0|{group.get('chat')}"
                    })

        self.send_supplement = '没有查找到你的群组，请点击【帮助】查看如果使用本服务'
        if self.inline_keyboard:
            self.send_supplement = '当前为你找到以下群组，点击可查看群组的规则详情，如果没有你期望的群组，请点击【帮助】按钮查看解决方案'

        self.guide_button = [
            {'text': '添加机器人到群组', 'url': 'https://t.me/addbot?startgroup=true'},
            {'text': '帮助', 'callback_data': 'help|0|0|0|0'},
            {'text': '返回', 'callback_data': 'start|0|0|0|0'}
        ]

    def init_rules(self):
        '''
        初始化当前群组的规则
        定义群组标题
        :return:
        '''


        if self.option == 'prelude' or not self.group:
            return None

        result = {}
        filed = f'`title`, `{self.option}`'
        if self.option in ["0", 'administrators']:
            filed = f'`title`'
            result = run_config.rules_example.keys()

        query = f"SELECT {filed} FROM `{sql.table_rules}` WHERE `chat`=%s"
        query = sql.query(sql.base_database, query, [self.group])

        # 构建机器人消息的标题，如果群组标题超长则截取前面部分字符
        title = query[0]['title']
        self.group_title = title if len(title) < 15 else title[:12] + '...'
        self.bot_title = f'{self.bot_title} >> {self.group_title}'


        if len(query[0]) > 1 and query[0][self.option]:
            query = json.loads(query[0][self.option])
            for key in run_config.rules_example[self.option].keys():
                result.update({key: query[key]})
        elif not result:
            result = copy.deepcopy(run_config.rules_example[self.option])

        return result



if __name__ == '__main__':



    pass









