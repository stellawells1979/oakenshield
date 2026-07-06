'''
标签集合器
'''

import time
import config
from database import Sql, sql

import logging
from logg import LogManager
log = LogManager('Share', logging.WARNING, logging.INFO)

class TagMuster:

    '''
    标签集合器
    '''

    def __init__(self):


        self.local_tag_path = f"{config.base_path}/data/tag_text.txt"
        self.prevail_tag = {}  # 流行标签,收集一些热门的流行标签，最多收集1000个流行标签
        self.hot_tag = {}  # 热门标签，我众多的流行标签中收集比较热门的标签，最多储存100个热门标签

        self.local_tags = self.init_local_tags()
        self.curr_tags = []


    def assemble_hot_tag(self, text):
        '''
        组装热门标签
        一个流行标签或热门标签都包含两个打桩参数，如 [22, 178214587585]，描述了该标签出现的次数和最后出现的时间，次
        数直观地反映了该标签的热度，如果现在的时间与最后出现的时间相差太久，你应该考虑降低其热度
        :return:
        '''
        if not text or '#' not in text:
            return

        now_time = time.time()
        tags = self.extract_tag(text)
        for tag in tags:

            if tag in self.hot_tag:
                # 如果当前标签已存在热门标签中，则继续增加热度
                self.hot_tag.update({tag: [self.hot_tag.get(tag) + 1, now_time]})
                continue

            # 获取当前标签的流行程度和最近出现的时间，如果没有则默认是[0, 0]
            level = self.prevail_tag.get(tag) or [0, 0]
            if level[0] > 20:
                # 出现超过20次的标签则被视为热门标签，将其添加到热门标签组中
                self.hot_tag.update({tag: [level, now_time]})
                del self.prevail_tag[tag]
            else:
                # 继续推高其流行程度
                self.prevail_tag.update({tag: [level + 1, now_time]})

    def extract_tag(self, text):
        '''
        提取标签，从一段文本中提取出可能的标签
        :return:
        '''
        if not text or '#' not in text:
            return []


        invalid_char = [' ', '\n', '\t', '\r', '|', '?', '，']
        result = []
        tags = text.split('#')  # 以 # 号为分隔，分割出可能的标签样本
        for tag in tags:
            tag = tag.replace(' ', '').strip()
            if not tag:
                continue

            if len(tag) > 6 or len(tag) < 2 or tag in result:
                # 超过5个字符或少于2个字符，则无做为标签的意义
                continue
            for i in invalid_char:
                if i in tag:
                    tag = tag.replace(i, '')

            # 收集标签到本地
            if tag not in self.local_tags:
                self.curr_tags.append(tag)

            result.append(f"#{tag.strip()}")
        # 将收集到的标签保存到本地文件
        if len(self.curr_tags) > 100:
            with open(f'{config.base_path}/data/tag_text.txt', 'a', encoding='utf-8') as file:
                file.write(f",{','.join(self.curr_tags)}")
            self.curr_tags = []

        return result

    def init_local_tags(self):
        '''
        初始化本地标签集
        :return:
        '''
        try:
            with open(self.local_tag_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            print('读取文件出错：', e)
            content = []

        result = []

        for char in content.split(','):
            if not char:
                continue
            if char == '#' or '#' not in char or char in result:
                continue
            result.append(char)

        if result:
            with open(self.local_tag_path, 'w', encoding='utf-8') as file:
                file.write(','.join(result))
        return result



tagmuster = TagMuster()

if __name__ == '__main__':


    remote_sql = Sql(
        config.database_remote['host'],
        config.database_remote['port'],
        config.database_remote['user'],
        config.database_remote['password'],
        config.database_remote['charset'],
        'telegram',
        extra=True
    )

    all_tag_text = tagmuster.local_tags

    tag_text = []



    query = f"SELECT `url`,`title`,`description`,`tag` FROM shares WHERE `edited` < DATE_SUB(NOW(), INTERVAL 20 DAY)"
    datas = sql.query(sql.database, query, None)
    for data in datas:

        row_tags = data.get('tag').split(',') if data.get('tag') else []
        row_tags_len = len(row_tags)

        for row in tagmuster.extract_tag(data.get('title')):
            if row in row_tags:
                continue
            row_tags.append(row)

        for row in tagmuster.extract_tag(data.get('description')):
            if row in row_tags:
                continue
            row_tags.append(row)

        for row in row_tags:
            if row not in all_tag_text:
                tag_text.append(row)
                all_tag_text.append(row)

        if row_tags_len != len(row_tags):
            query = f"UPDATE shares SET `tag`=%s, `render`=%s WHERE `url`=%s"
            remote_sql.query(sql.database, query, [','.join(row_tags), 'admin', data.get('url')])
            print(row_tags, '已更新至远程数据库')

        if len(tag_text) > 1000:
            with open(f'{config.base_path}/data/tag_text.txt', 'a', encoding='utf-8') as f:
                f.write(f",{','.join(tag_text)}")
            tag_text = []
            log.info('已将tag_text写入文件')






