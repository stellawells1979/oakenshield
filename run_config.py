
'''
全局变量
'''

import os
import time


date = time.time()

now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date))

# 在回复用户的搜索结果消息中，每条消息显示的搜索条目数量
page_count = 15

# 基础文件路径
base_path = os.path.dirname(os.path.abspath(__file__))

# 日志文件路径
logs_path = os.path.join(base_path, 'logs')

# 数据表结构文件，用于创建数据表
table_structure = os.path.join(base_path, 'configs')

# 自定义的停用词文件
stop_words = os.path.join(base_path, 'data', 'stopwords.txt')

# 额外的停用词文件
extr_words = os.path.join(base_path, 'data', 'extrawords.txt')

# 城市名字文件
city_path = os.path.join(base_path, 'data', 'city.txt')

# 设置日志保留时间
retention_days = 7


rules_example = {
        # 这是个默认的规则实例
        # 每一个字典对象是一个规则选项
        # 字典中的键是一个按钮，参数按钮或功能按钮，对应的值参数值，如果是功能按钮，那么它的统一值是 disabled
        'administrators': [],
        'register': {'period': 0, 'explain': None, 'status': None, 'view': None, 'begin': 'disabled', 'clear': None
                     },
        'newcomer': {
            'welcome': None, 'tip_join': False, 'tip_leave': False, 'verify_join': False,'clear': None
        },
        'text': {
            'len': 0, 'high': 0, 'key': None, 'allow': 0, 'level': None,
            'restrict': '10分钟', 'clear': None,
        },
        'photo': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': False,
        },
        'video': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': False,
        },
        'voice': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None,
        },
        'link': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None,
        },
        'document': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None
        },
        'multimedia': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None
        },
        'contact': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None
        },
        'forward': {
            'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None
        },
        'checkname': {
            'key': None, 'allow': 0, 'level': None, 'restrict': '10分钟', 'clear': None
        },
        'intelligent': {
            'mode': None, 'scope': 0, 'count': 0, 'level': None, 'restrict': '10分钟', 'clear': None,
        }
    }

translation = {
        True: '✅',
        False: '⚪️',
        'deleteMessage': '删除消息',
        'restrictChatMember': '禁言',
        'restrict': '禁言时长',
        'kickChatMember': '移出',
        'banChatMember': '拉黑',
        'gradually(kick)': '渐进限制(移出)',
        'gradually(block)': '渐进限制(拉黑)',

        'clear': '清空规则',
        'allow': '允许次数',
        'level': '处理规则',
        'len': '长度限制',
        'high': '高度限制',
        'key': '设置关键字词',

        'register': '签到管理',
        'period': '签到周期',
        'explain': '签到描述',
        'begin': '启动签到',
        'Ready': '就绪',
        'Run': '进行中',
        'Unknown': '未设置',
        'status': '当前状态',
        'view': '查看签到数据',
        'administrators': '更新群管理员',
        'newcomer': '新人管理',
        'verify_join': '入群验证',
        'tip_join': '清除入群提示',
        'tip_leave': '清除离群提示',
        'welcome': '欢迎语',
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
        'posts': '帖子'

    }
