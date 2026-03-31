
'''
temp
'''
from utils.jiebawords import jiebas
from database import sql
import run_config
from utils.toolbox import toolbox
from utils.marketing import marketing
import logging
from logmanage import DailyLogManager

log = DailyLogManager('Search', logging.ERROR, logging.INFO)

class Search:
    '''
    定义全局变量，

    '''

    def __init__(self, user, data):
        '''
        响应用户的搜索操作。用户的搜索操作有两种，一种是用户发起新的关键字词搜索，称为新搜索。
        另一种是在已有的搜索结果中的操作，称为操作搜索
        :param data: 回调参数，用户点击搜索消息中的按钮返回参数


        :self.send_text (str) 请求的文本消息
        :self.assort_keyboard (obj) 分类键盘，在向用户展示的搜索内结果中，可能包含多种类型的结果，创建一个分类导航键盘，增强用户体验
        :self.turning_keyboard (obj) 翻页键盘,就是上一页，一下页
        :self.customize_keyboard (obj) 自定义键盘，就是想加什么就加什么，当然也可以不理会它
        :self.predefined_entities (obj) 一个容器，当你需要为某些文本添加富文本效果时，将富文本属性添加到些容器，这只是
            个草稿对象，最终需要调用 toolbox 工具箱中的 format_entities 方法将其格式化成合法的 telegram entitie 对象
        :self.page_count (int) 第条消息显示和搜索数量，这是个全局参数，你可以地 run_config.py 文本中修改此参数
        '''

        self.search_type = data[0]
        self.user_id = user
        self.keyword = data[1]
        self.option = data[2]
        self.page = int(data[3])
        self.owner_user = int(data[4])

        self.search_data = {}
        self.reply_to = {}
        self.inline_keyboard = []   # 主键盘
        self.assort_keyboard = []  # 分类键盘
        self.turning_keyboard = []  # 翻页键盘
        self.customize_keyboard = []

        self.page_count = run_config.page_count

        # 初始化发送文本为一个顶置的推广
        self.send_text, self.predefined_entities = marketing.search_head_marketing()

        # 在分类按钮中显示的 emoji
        self.assort_example = {
            'bot': '🤖',
            '机器人': '🤖',
            'movie': '🎬',
            '电影': '🎬',
            '音乐': '🎵',
            'music': '🎵',
            '新闻': '📰',
            'news': '📰',
            '游戏': '🎮',
            'game': '🎮',
            '书籍': '📖',
            'books': '📖',
            '图片': '🖼️',
            'image': '🖼️',
            '视频': '📹',
            'video': '📹',
            '贴纸': '🧩',
            'sticker': '🧩',
            '表情': '😀',
            'emoji': '😀',
            '链接': '🔗',
            'link': '🔗',
            '群组': '👥',
            '频道': '📢',
            'group': '👥',
            'channel': '📢',
            'private': '👤',
            'text': '📄',
            'posts': '📝',
        }

    def main(self):
        '''

        :return:
        '''
        if self.search_type == 'ST' and self.keyword == 'Tag':
            self.hot_tags()

        elif self.search_type in ['SP', 'ST', 'SG']:

            self.turning()


        return self.search_data

    def turning(self):
        '''
        |关键字词|类别|页数|用户
        :return:
        '''

        search_data = self.get_search_data(self.keyword, self.option)
        if not search_data:
            return []

        if self.page > 0:
            self.turning_keyboard = [{
                'text': '上一页',
                'callback_data': f'{self.search_type}|{self.keyword}|{self.option}|{self.page - 1}|{self.user_id}'
            }]
        for index, record in enumerate(search_data[self.page * self.page_count:]):
            if index >= self.page_count:
                self.turning_keyboard.append({
                    'text': '下一页',
                    'callback_data': f'{self.search_type}|{self.keyword}|{self.option}|{self.page + 1}|{self.user_id}'
                })
                break

            record_type = self.assort_example.get(record['type'])
            url = record['url']
            members = record['members']

            # members 参数，当 record_type 是群组时，members 是这个群组或频道的人数，当 record_type 是多媒体时， members 是浏览次数
            if not record_type or not members:
                members = ''
            else:
                members = self.format_to_k(members)

            # 将标题去除空格等符号，并以占位符的方式处理文本长度,以匹配中英文字符的显示宽度
            text = record['title'].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            text = toolbox.get_display_width(text, 40)

            self.send_text = f'{self.send_text}{record_type} {text}  {members}\n'
            self.predefined_entities.append({'text': text, 'type': 'text_link', 'url': url})

        pages = (len(search_data) + self.page_count - 1) // self.page_count
        option = run_config.translation.get(self.option, self.option)
        self.send_text = f'{self.send_text}\n当前显示【{option}】 {pages}/{self.page + 1}页'

        # 如果是个人聊天，你应该为当前消息添加一个返回我按钮
        if self.search_type == 'ST':
            self.turning_keyboard.append({
                'text': '返回',
                'callback_data': f'{self.search_type}|Tag|all|0|{self.user_id}'
            })

        self.search_data.update({
            'text': self.send_text,
            'entities': toolbox.format_entities(self.send_text, self.predefined_entities),
            'reply_markup': {'inline_keyboard': [self.assort_keyboard, self.turning_keyboard]},
        })

    def hot_tags(self):
        '''

        :return:
        '''
        catalog = [
            '影视剧情', '娱乐八卦', '音乐视频', '科学上网', '社区论坛', '虚拟币', '软件编程', '游戏竞技', '主播直播', '网购电商',
            '健康保健', 'SEX', '新闻时政', '小说书籍', '教育培训', '体育赛事', '彩票博彩', 'IT科技', '美食养生', '旅行摄影', '社交媒体',
            '金融财经', '动漫二次元', '广告营销', '招聘职务', '商务贸易', '资源搜集', '同城交友', '暗网禁区', '手机数码',
        ]
        inline_keyboard = []
        for tag in catalog:
            inline_keyboard.append({'text': tag, 'callback_data': f'ST|#{tag}|all|0|0'})

        inline_keyboard = [inline_keyboard[i:i + 4] for i in range(0, len(inline_keyboard), 4)]

        inline_keyboard.append([{'text': '返回', 'callback_data': f'start|0|0|0|0'}])

        self.send_text = "百搜机器人\n\n  搜群组,搜频道,搜影视,搜资讯,搜遍TG的搜索小能手"

        self.search_data.update({
            'text': self.send_text,
            'reply_markup': {'inline_keyboard': inline_keyboard},
        })

    def get_search_data(self, keyword, option):
        '''
        :return:
        '''

        keywords = jiebas.organize(keyword)
        if not keywords:
            log.info(f'搜索关键字【{keyword}】，在数据表中没有查找到相关的记录')
            return []

        where = ''
        values = []
        for key in keywords:
            key = key.strip()
            if key.startswith('#'):
                where = f"{where} tag LIKE %s OR"
                values.append(f'%{key}%')
            else:
                where = f"{where} title LIKE %s OR description LIKE %s OR"
                values.extend([f'%{key}%', f'%{key}%'])
        where = where.rstrip(' OR')

        query = f"SELECT * FROM `{sql.table_groups}` WHERE {where}"
        query = sql.querys(sql.base_database, query, values)

        all_option = []
        count = 0
        while count < len(query):

            record_type = query[count].get('type')

            if not record_type or (option != 'all' and option != record_type):
                del query[count]
                continue

            if record_type not in all_option:
                all_option.append(record_type)

                # 构建分类键盘
                self.assort_keyboard.append({
                    'text': self.assort_example.get(record_type, record_type),
                    'callback_data': f'{self.search_type}|{self.keyword}|{record_type}|0|{self.user_id}'
                })
            count += 1

        if self.assort_keyboard:
            self.assort_keyboard.insert(
                0,
                {'text': '全部', 'callback_data': f'{self.search_type}|{self.keyword}|all|0|{self.user_id}'}
            )

        return query

    @classmethod
    def format_to_k(cls, value):
        """
        将超过1000的数字格式化为 k 表示法。
        :param value: int - 输入的数值
        :return: str - 格式化后的字符串
        """
        if value >= 1000:
            return f"{value / 1000:.1f}k" if value % 1000 != 0 else f"{value // 1000}k"
        return str(value)


if __name__ == '__main__':


    search = Search(123456789, ['ST', '科学上网', 'all', 0, 123456789])
    ss = search.main()
    print(ss)





