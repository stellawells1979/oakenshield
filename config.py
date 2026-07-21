
'''
全局变量
'''

import os
import platform
from myaccount import account


# 项目时区
time_zone = 'UTC+8'
project_timeoffset = 8
project_timezone = '+08:00'

# 基础文件路径
base_path = os.path.dirname(os.path.abspath(__file__))

# 识别当前系统信息,视系统是否配置代理
system_name = platform.system().lower()

# 根据系统匹配数据库账号
if system_name == 'windows':
    database_account = account.database_windows
elif system_name == 'linux':
    database_account = account.database_ubuntu
else:
    raise RuntimeError(f'Unsupported system: {platform.system()}')


# 账户信息
account_path = os.path.join(base_path, 'myaccount', 'myaccount.txt')

if system_name == 'linux':
    database_account = account.database_ubuntu
elif not system_name == 'windows':
    raise RuntimeError(f'Unsupported system: {platform.system()}')

# 日志文件路径
logs_path = os.path.join(base_path, 'logs')

# 数据表结构文件，用于创建数据表
table_structure = os.path.join(base_path, 'data', 'tables_fields.json')

# 自定义的停用词文件
stop_words = os.path.join(base_path, 'data', 'stopwords.txt')

# 额外的停用词文件
extr_words = os.path.join(base_path, 'data', 'extrawords.txt')

# 城市名字文件
city_path = os.path.join(base_path, 'data', 'city.txt')

# 设置日志保留时间
retention_days = 7

# 在回复用户的搜索结果消息中，每条消息显示的搜索条目数量
page_count = 15

# 代理参数，你必须在地本地运行一个代理客户并配置正确代理参数
proxy = {
    'http': 'http://127.0.0.1:10809',
    'https': 'socks5h://127.0.0.1:10808'
}

proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'socks5h://127.0.0.1:10808'
}

# 本地代理池路径
local_proxies_queue_path = os.path.join(base_path, 'data', 'HttpsProxies', 'ProxierQueue.json')

# 用于储存临时下载代理数据的文件夹
local_proxies_dir = os.path.join(base_path, 'data', 'HttpsProxies')


rules_example = {
    # 这是个默认的规则实例
    # 每一个字典对象是一个规则选项
    # 字典中的键是一个按钮，参数按钮或功能按钮，对应的值参数值，如果是功能按钮，那么它的统一值是 disabled
    'administrators': [],
    'register': {
        'regi_count': 0, 'regi_id': None, 'regi_name': None, 'describe': None,
        'origin': None, 'expired': None, 'timing': 0, 'status': None
    },
    'newcomer': {'welcome': None, 'tip_join': False, 'tip_leave': False, 'verify_join': False},
    'text': {'len': 0, 'high': 0, 'key': None, 'allow': 0, 'level': None, 'mute_time': 0},
    'photo': {'allow': 0, 'level': None, 'mute_time': 0},
    'video': {'allow': 0, 'level': None, 'mute_time': 0},
    'voice': {'allow': 0, 'level': None, 'mute_time': 0},
    'link': {'allow': 0, 'level': None, 'mute_time': 0},
    'document': {'allow': 0, 'level': None, 'mute_time': 0},
    'multimedia': {'allow': 0, 'level': None, 'mute_time': 0},
    'contact': {'allow': 0, 'level': None, 'mute_time': 0},
    'forward': {'allow': 0, 'level': None, 'mute_time': 0},
    'checkname': {'allow': 0, 'key': None, 'level': None, 'mute_time': 0},
    'intelligent': {'mode': None, 'scope': 0, 'count': 0, 'level': None, 'mute_time': 0}
}

rules_keyboard = {
        'register': {
                '创建签到项目': 'regi_name', '设置签到描述': 'describe', '设置签到周期': 'period',
                '轮循时间': 'timing', '启动签到': 'begin', '查看历史签到': 'history', '关闭签到': 'End'
        },
        'newcomer': {
                '设置欢迎语': 'welcome', '验证进群': 'verify_join', '清除入群提示': 'tip_join',
                '清除离群提示': 'tip_leave', '清空规则': 'clear'
        },
        'text': {
                '设置长度限制': 'len', '设置行数限制': 'high', '设置关键字': 'key', '允许次数': 'allow',
                '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'
        },

        'photo': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'video': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'voice': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'link': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'document': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'multimedia': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'contact': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},
        'forward': {'允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time', '清空规则': 'clear'},

        'checkname': {
                '设置关键字词': 'key', '允许次数': 'allow', '处理规则': 'level', '禁言时长': 'mute_time',
                '清空规则': 'clear'
        },
        'intelligent': {
                '设置检测模式':'mode', '设置检测范围': 'scope', '设置次数': 'count', '处理规则': 'level',
                '禁言时长': 'mute_time', '清空规则': 'clear'
        },
}

# 此列表中的字段仅接收整数型参数
rules_param_int = ['len', 'high', 'scope', 'mute', 'allow', 'count', 'period', 'timing']

# 此列表中的字段限制长度
rules_param_restrict = {
    'welcome': 150,
    'key': 100,
    'describe': 200,
    'regi_name': 20
}

translation = {
    'delete': '删除消息',
    'mute': '禁言',
    'mute_time': '禁言时长',
    'kick': '移出',
    'ban': '拉黑',
    'stage_kick': '叠加限制(移出)',
    'stage_ban': '叠加限制(拉黑)',

    'clear': '清空规则',
    'allow': '允许次数',
    'level': '处理规则',
    'len': '长度限制',
    'high': '行数限制',
    'key': '关键字词',


    'register': '签到管理',
    'create_reg': '创建签到项目',
    'regi_name': '签到名称',
    'period': '签到周期',
    'describe': '签到描述',
    'timing': '轮循时间',
    'origin': '起始时间',
    'expired': '到期时间',
    'begin': '启动签到',
    'Read': '就绪',
    'Run': '进行中',
    'Exp': '已过期',
    'End': '关闭',
    'Unknown': '未设置',
    'status': '当前状态',
    'history': '查看历史签到',
    'administrators': '更新群管理员',
    'newcomer': '新人管理',
    'verify_join': '入群验证',
    'tip_join': '清除入群提示',
    'tip_leave': '清除离群提示',
    'welcome': '自定义欢迎语',
    'text': '文本消息',
    'photo': '图片消息设置',
    'justQR': '仅检测二维码',
    'video': '视频消息设置',
    'voice': '音频消息设置',
    'link': '链接消息设置',
    'document': '文档消息设置',
    'multimedia': '多媒体消息设置',
    'GIF': 'GIF',
    'Story': '故事',
    'Poll': '投票',
    'sticker': '贴纸',
    'contact': '名片消息设置',
    'forward': '转发消息设置',
    'checkname': '检测用户名',

    'intelligent': '智能反广告',
    'mode': '检测模式',
    'scope': '设置范围',
    'count': '设置次数',

    'all': '全部',
    'group': '群组',
    'channel': '频道',
    'bot': '机器人',
    'movie': '影视',
    'private': '用户',
    'image': '图片',
    'news': '新闻',
    'books': '书籍',
    'game': '游戏',
    'music': '音乐',
    'posts': '帖子',
    'creator': '创建者'

}

# emoji示例，应用于search模块
assort_emoji = {
    'bot': '🤖',
    '机器人': '🤖',
    'movie': '🎥',
    '电影': '🎥',
    '音乐': '🎵',
    'music': '🎵',
    '新闻': '📰',
    'news': '📰',
    '游戏': '🎮',
    'game': '🎮',
    '书籍': '📚',
    'books': '📚',
    '图片': '🏞',
    'photo': '🏞',
    '视频': '📹',
    'video': '📹',
    '贴纸': '🧩',
    'sticker': '🧩',
    '表情': '😀',
    'emoji': '😀',
    '链接': '🔗',
    'link': '🔗',
    '群组': '👥',
    '频道': '📣',
    'group': '👥',
    'channel': '📣',
    'private': '👤',
    'text': '📄',
    'posts': '📝',
    '文档': '📂',
    'document': '📂',
    'planning': '🎉'
}
