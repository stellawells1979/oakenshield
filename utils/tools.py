



'''
一个工具箱，定义一些常用方法供调用
'''
import re
import random
import unicodedata
import string
import logging
from logmanage import DailyLogManager

log = DailyLogManager('ToolBox', logging.ERROR, logging.INFO)


class ToolBox:
    '''
    格式化工具
    '''

    @classmethod
    def contains_uppercase(cls, char):
        '''
        判断字符串是否包含大写字母
        :return:
        '''
        return any(char.isupper() for char in char)

    @classmethod
    def format_entities(cls, all_text, draft_entities):

        '''
        将 entities 草稿对象序列为合法的 telegram entities 对象
        :param all_text:
        :param draft_entities:
        :return: list
        '''
        entities_type = {
            # 多行代码块
            'pre': {'offset': 0, 'length': 1, 'language': '指定编程语言，比如 python'},
            # “文本链接”(用于可点击的文本网址)
            'text_link': {'offset': 0, 'length': 1, 'url': '你希望跳转的目标网址'},
            # “文本提及”( 用于没有用户名的用户)
            'text_mention': {'offset': 0, 'length': 1, 'user': {'字段': '当前user对象的所有可用字段'}},
            # “自定义表情符号”( 用于内嵌自定义表情符号贴纸)。
            'custom_emoji': {'offset': 0, 'length': 1, 'custom_emoji_id': 'ID 参数'},
            'bold': {'offset': 0, 'length': 1},  # 粗体效果
            'italic': {'offset': 0, 'length': 1},  # 斜体效果
            'underline': {'offset': 0, 'length': 1},  # 下划线
            'strikethrough': {'offset': 0, 'length': 1},  # 删除线
            'spoiler': {'offset': 0, 'length': 1},  # 剧透，马赛克文本（隐藏内容，需要点击显示）
            'code': {'offset': 0, 'length': 1},  # 代码
            'mention': {'offset': 0, 'length': 1},  # 提及
            'hashtag': {'offset': 0, 'length': 1},  # “话题标签”(#hashtag或#hashtag@chatusername)
            'cashtag': {'offset': 0, 'length': 1},  # “金融标签”($USD或$USD@chatusername)
            'bot_command': {'offset': 0, 'length': 1},
            'phone_number': {'offset': 0, 'length': 1},
            'email': {'offset': 0, 'length': 1},
            'blockquote': {'offset': 0, 'length': 1},  # 块引用
            'expandable_blockquote': {'offset': 0, 'length': 1},  # 可扩展的块引用
            'url': {'offset': 0, 'length': 1},
        }

        # 富文本中的其它字段，只会包含以下列表中的字段
        extra_fileds = ['language', 'user', 'url', 'custom_emoji_id']
        encoding = "utf-16"

        result = []
        start = 0

        # 将文本编码为 UTF-16，并移除 BOM，实际上变成 \x00e\x00l\x00l\x00o 的样式
        all_text = all_text.encode(encoding)[2:]
        for entitie in draft_entities:
            if not entitie.get('text'):
                continue
            if not entitie.get('type') in entities_type:
                log.error(f'>> format_entities: 构建富文本出错，不支持的富文本类型-- {entitie}')
                continue

            if entitie['type'] in ['pre', 'text_link', 'text_mention', 'custom_emoji'] and len(entitie) < 3:
                log.error(f'>> format_entities: 构建富文本出错，缺少参数，请检查参数-- {entitie}')
                continue

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
    def get_display_width(cls, text, length):
        """
        判断单个字符的显示宽度
        返回值：
        - 英文字符返回 1
        - 中文字符或全角字符返回 2
        """
        if not text:
            return None
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

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

    @classmethod
    def brief_uid(cls, length, use_secure=None):
        """
        生成指定长度的随机字符串
        :param length: 字符串长度
        :param use_secure: 是否使用加密安全随机数 (默认 False)
        """
        if length <= 0:
            return ""

        # 定义字符集：大小写字母 + 数字
        characters = string.ascii_letters + string.digits

        if use_secure:
            import secrets
            return ''.join(secrets.choice(characters) for _ in range(length))
        else:
            return ''.join(random.choice(characters) for _ in range(length))






tools = ToolBox()


if __name__ == '__main__':

    temp = tools.brief_uid(6)
    print(temp)





















