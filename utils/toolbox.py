



'''
一个工具箱，定义一些常用方法供调用
'''
import re
import random
import unicodedata
from utils.TGrequest import crave
import logging
from logmanage import DailyLogManager

log = DailyLogManager('ToolBox', logging.ERROR, logging.INFO)


class ToolBox:
    '''
    格式化工具
    '''

    @classmethod
    def contains_uppercase(cls, str):
        '''
        判断字符串是否包含大写字母
        :return:
        '''
        return any(char.isupper() for char in str)

    @classmethod
    def format_entities(cls, all_text, draft_entities):

        '''
        将 entities 草稿对象序列为合法的 telegram entities 对象
        :param all_text:
        :param draft_entities:
        :return:
        '''
        entities_type = [
            # 多行代码块
            {'type': 'pre', 'offset': 0, 'length': 1, 'language': '指定编程语言，比如 python'},
            # “文本链接”(用于可点击的文本网址)
            {'type': 'text_link', 'offset': 0, 'length': 1, 'url': '你希望跳转的目标网址'},
            # “文本提及”( 用于没有用户名的用户)
            {'type': 'text_mention', 'offset': 0, 'length': 1, 'user': {'字段': '当前user对象的所有可用字段'}},
            # “自定义表情符号”( 用于内嵌自定义表情符号贴纸)。
            {'type': 'custom_emoji', 'offset': 0, 'length': 1, 'custom_emoji_id': 'ID 参数'},
            {'type': 'bold', 'offset': 0, 'length': 1},  # 粗体效果
            {'type': 'italic', 'offset': 0, 'length': 1},  # 斜体效果
            {'type': 'underline', 'offset': 0, 'length': 1},  # 下划线
            {'type': 'strikethrough', 'offset': 0, 'length': 1},  # 删除线
            {'type': 'spoiler', 'offset': 0, 'length': 1},  # 剧透，马赛克文本（隐藏内容，需要点击显示）
            {'type': 'code', 'offset': 0, 'length': 1},  # 代码
            {'type': 'mention', 'offset': 0, 'length': 1},  # 提及
            {'type': 'hashtag', 'offset': 0, 'length': 1},  # “话题标签”(#hashtag或#hashtag@chatusername)
            {'type': 'cashtag', 'offset': 0, 'length': 1},  # “金融标签”($USD或$USD@chatusername)
            {'type': 'bot_command', 'offset': 0, 'length': 1},
            {'type': 'phone_number', 'offset': 0, 'length': 1},
            {'type': 'email', 'offset': 0, 'length': 1},
            {'type': 'blockquote', 'offset': 0, 'length': 1},  # 块引用
            {'type': 'expandable_blockquote', 'offset': 0, 'length': 1},  # 可扩展的块引用
            {'type': 'url', 'offset': 0, 'length': 1},
        ]
        extra_fileds = ['language', 'user', 'url', 'custom_emoji_id']
        encoding = "utf-16"

        result = []
        start = 0

        # 将文本编码为 UTF-16，并移除 BOM，实际上变成 \x00e\x00l\x00l\x00o 的样式
        all_text = all_text.encode(encoding)[2:]
        for entitie in draft_entities:

            # 同样将字串编码为 UTF-16，并移除 BOM，
            text = entitie['text'].encode(encoding)[2:]

            # 以 utf-16 格式的编码查找字串起始位置
            index = all_text.find(text, start)

            if index != -1:
                # 将字节偏移量转换为 UTF-16 单位
                offset = index // 2

                # 因为 utf-16 编码中，每个字符占用 2 个字节，因此通过 len(text) // 2 来获取子串的字符长度。
                text_len = len(text) // 2

                extra_param = {row: entitie.get(row) for row in extra_fileds if entitie.get(row)}

                # 构建富文本对象
                result.append({
                    'type': entitie['type'],
                    'offset': offset,
                    'length': text_len,
                    **extra_param,
                })

                # 更新搜索起始位置
                start = index + len(text)

        # 返回参数前将 result 中各个对象按对象中的 offset 值排序
        return sorted(result, key=lambda x: x['offset'])

    @staticmethod
    def extract_links(text):
        '''
        从文本中提取所有的链接
        :param text:
        :return: list
        '''
        pattern = r'(https?://.*?(?:\.[a-zA-Z]{2,6})(?:/[^ ]*)?)'
        # 使用 re.findall 找出所有的链接
        links = re.findall(pattern, text)
        return links

    @classmethod
    def create_verify(cls, member, group):
        '''
        创建一验证实例
        获取两个随机数 a, b, 将它们相加得出结果 answer
        在 answer 值有左右之间取 5 位随机数与 answer 进行混淆，再将这些参数打乱

        :return:
        '''
        member_id = member.get('id')
        member_name = member.get('first_name') + member.get('last_name', '')

        a = random.randint(16, 100)
        b = random.randint(30, 100)

        answer = a + b
        admix = [random.randrange(answer - 10, answer + 60) for _ in range(5)]
        # 确保 admix 包含了正确答案（answer）
        if not answer in admix:
            admix.append(answer)
        # 执行混淆交打乱顺序
        random.shuffle(admix)

        # 生成答案键盘，为正确答案按键定义 Y 的回调信息，
        button = []
        for index in admix:
            button.append({'text': str(index), 'callback_data': f'|verify|{"Y" if index == answer else "N"}|{member_id}|{group}'})

        text = f"{member_name}: 请计算以下算术题并选择正确答案\n\n   {a} + {b} = ？ \n\n  你有两分钟的时间来验证，否则将被移出群聊"
        entitles = cls.format_entities(
            text,
            [
                {'type': 'text_mention', 'text': member_name, 'user': member},
                {'type': 'blod', 'text': '移出群聊'},
            ]
        )

        return {'text': text, 'reply_markup': {'inline_keyboard': [button]}, 'entities': entitles}

    @classmethod
    def get_administrator(cls, bot, group):
        '''
        获取指定群组的管理员
        :param bot:
        :param group:
        :return:
        '''
        response = crave.send(bot, 'getChatAdministrators', {'chat_id': group})
        if response:
            return response['result']
        return []

    @classmethod
    def get_display_width(cls, text, length):
        """
        判断单个字符的显示宽度
        返回值：
        - 英文字符返回 1
        - 中文字符或全角字符返回 2
        """
        count = 0
        result = ''
        for index in [char for char in text]:
            if unicodedata.east_asian_width(index) in ['F', 'W', 'A']:
                # 全角（F）、宽字符（W）、两者兼容（A）的宽度为 2
                count += 1
            count += 1
            result = f'{result}{index}'
            if count >= length:
                return result
        return text



toolbox = ToolBox()


if __name__ == '__main__':

    pass





















