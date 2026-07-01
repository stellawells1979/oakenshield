'''
搜索
'''
import config
from utils.jiebawords import jiebas
from utils.tools import tools
from database import sql
import logging
from logmanage import DailyLogManager

log = DailyLogManager('Search', logging.ERROR, logging.INFO)


class Search:
    '''
    搜索
    '''

    def __init__(self, user, data):
        '''
        :param user: 用户的ID
        :param data: 搜索数据，包含搜索类型、关键词、选项、页码和所有者用户ID
        '''
        self.user_id = user
        self.search_type = data[0]
        self.keyword = data[1]
        self.option = data[2]
        self.page = int(data[3])
        self.owner_user = int(data[4])

        self.assort_keyboard = []   # 分类键盘
        self.page_keyboard = []     # 翻页键盘
        self.planning_keyboard = []     # 自定义的广告键盘
        self.top_text = ''
        self.share_text = ''
        self.casual_entity = []  #
        self.status_text = ''  # 搜索状态文本，用于描述当前搜内容的说明，最终可能也是空文本

    def search_main(self):
        '''

        :return:
        '''
        self.set_top_text()

        if self.search_type == 'ST' and self.option == '0':
           return self.hot_tags()

        self.create_share_data()
        text = self.top_text + self.status_text + self.share_text
        return {
            'text': text,
            'entities': tools.format_entities(text, self.casual_entity),
            'reply_markup': {'inline_keyboard': [self.assort_keyboard, self.page_keyboard, self.planning_keyboard]},
        }

    def create_share_data(self):
        '''
        生成分享文本
        :return:
        '''

        share_data = self.create_share_link(self.keyword, self.option)
        if not share_data:
            share_data = self.customize_search()

        if self.page > 0:
            self.page_keyboard.append({
                'text': '上一页',
                'callback_data': f'{self.search_type}|{self.keyword}|{self.option}|{self.page - 1}|{self.user_id}'
            })

        for i, row in enumerate(share_data[self.page * config.page_count:]):
            if i >= config.page_count:
                # config文档中的page_count控制了每页显示的条目数，当达到这个数量时，添加下一页按钮并退出当前循环
                self.page_keyboard.append({
                    'text': '下一页',
                    'callback_data': f'{self.search_type}|{self.keyword}|{self.option}|{self.page + 1}|{self.user_id}'
                })
                break

            # 将标题去除空格等符号，并以占位符的方式处理文本长度,以匹配中英文字符的显示宽度
            row_text = row.get('title') or row.get('description')
            if not row_text:
                continue

            row_text = tools.get_display_width(row_text, 40)
            if not row_text:
                continue
            members = self.format_to_k(row.get('members', '')) if row.get('members', '') else ''
            row_type = config.assort_emoji.get(row.get('type'), '❓')  # 以emoji符号显示类型

            self.share_text += f'{row_type} {row_text}  {members}\n'

            # 为文本添加链接
            self.casual_entity.append({'text': row_text, 'type': 'text_link', 'url': row.get('url')})
        # 构建页码提示文本
        pages = (len(share_data) + config.page_count - 1) // config.page_count
        option = config.translation.get(self.option, self.option)
        self.share_text += f"\n当前显示【{option}】 {pages}/{self.page + 1}页"

        # 对于私人聊天，需要添加一个返回按钮
        if self.search_type != 'SG':
            self.page_keyboard.append({
                'text': '返回',
                'callback_data': f'{self.search_type}|0|0|0|{self.user_id}'
            })

    def create_share_link(self, keyword, option):
        '''
        从数据库获取分享链接并按初始化数据集
        :param keyword:
        :param option:
        :return:
        '''
        where = self.select_where(keyword)
        if not where:
            self.status_text = f'没有找到【{keyword}】的相关内容，为你推荐以下内容\n'
            log.info(f'jiebas未能解析【{keyword}】')
            return []

        query = f"SELECT `url`,`type`,`title`,`description`,`members`,`publish` FROM `{sql.table_shares}` WHERE {where}"
        result = sql.query(sql.database, query, None) or []

        count = 0
        all_option = []  # 收集所有分类，用于构建分类按钮
        while count < len(result):

            if not result[count].get('title') and not result[count].get('description'):
                # 如果没有标题或描述文本，则不需要该分享链接
                del result[count]
                continue

            row_type = result[count].get('type')

            if not row_type or row_type == 'mixed_media':
                del result[count]
                continue

            if row_type not in all_option:
                all_option.append(row_type)

            if option != 'all' and row_type != option:
                # 没有类型标识的，
                del result[count]
                continue

            count += 1

        # 构建类型导航键盘
        if all_option:
            for row_type in all_option:
                self.assort_keyboard.append({
                    'text': config.assort_emoji.get(row_type, '❓'),
                    'callback_data': f'{self.search_type}|{self.keyword}|{row_type}|0|{self.user_id}'
                })
            self.assort_keyboard.insert(
                0,
                {'text': '全部', 'callback_data': f'{self.search_type}|{self.keyword}|all|0|{self.user_id}'}
            )

        return result

    @classmethod
    def hot_tags(cls):
        '''
        个人聊天中的热门标签
        :return:
        '''
        catalog = [
            '影视剧情', '娱乐八卦', '音乐视频', '科学上网', '社区论坛', '虚拟币', '软件编程', '游戏竞技', '主播直播', '网购电商',
            '健康保健', 'SEX', '新闻时政', '小说书籍', '教育培训', '体育赛事', '彩票博彩', 'IT 科技', '美食养生', '旅行摄影', '社交媒体',
            '金融财经', '动漫二次元', '广告营销', '招聘职务', '商务贸易', '资源搜集', '同城交友', '暗网禁区', '手机数码', 'AI'
        ]
        inline_keyboard = []
        for tag in catalog:
            inline_keyboard.append({'text': tag, 'callback_data': f'ST|#{tag}|all|0|0'})

        inline_keyboard = [inline_keyboard[i:i + 4] for i in range(0, len(inline_keyboard), 4)]

        inline_keyboard.append([{'text': '返回', 'callback_data': f'start|0|0|0|0'}])

        return {
            'text': "百搜机器人\n\n  搜群组,搜频道,搜影视,搜资讯,搜遍TG的搜索小能手",
            'reply_markup': {'inline_keyboard': inline_keyboard},
        }

    def select_where(self, keyword):
        '''
        构建查询条件
        :param keyword:
        :return:
        '''
        if self.search_type == 'ST':
            return f"`tag` LIKE '%{keyword}%'"

        keywords = jiebas.organize(keyword)
        if not keywords:
            return None

        # 迭代keywords构建查询条件
        result = ''
        for keyword in keywords:
            result += f" `title` LIKE '%{keyword}%' OR `description` LIKE '%{keyword}%' OR `tag` LIKE '%{keyword}%' OR"

        return result.rstrip(' OR')

    @classmethod
    def format_to_k(cls, value):
        """
        将超过1000的数字格式化为 k 表示法。
        :param value: int - 输入的数值
        :return: str - 格式化后的字符串
        """
        if not value:
            return value
        if value >= 1000:
            return f"{value / 1000:.1f}k" if value % 1000 != 0 else f"{value // 1000}k"
        return str(value)

    def set_top_text(self):
        '''
        设置self.top_text文本
        :return:
        '''
        text = '【推广】 '

        query = f"SELECT `only_url`,`description`,`promo`,`level` FROM `planning`"
        result = sql.query(sql.database, query, None) or []
        for row in result:
            if row.get('only_url') == 'https://smspva.com/?ref=206208':
                self.top_text = text + row.get('promo') + '\n\n'
                self.casual_entity.append({'text': row.get('promo'), 'type': 'text_link', 'url': row.get('only_url')})
                break

    def customize_search(self):
        '''
        自定义搜索结果。如果没有获取到用户搜索关键字和结果，则返回这个乍定义的内容
        :return:
        '''


if __name__ == '__main__':

    gt = 'SG|59|group|4|1120690440'
    search = Search(123456789, ['SG', '59', 'photo', 4, 123456789])
    print(search.search_main())
