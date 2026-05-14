'''
Created on Aug 6, 2016
'''
import time
import json
import logging

from database import sql

from logg import LogManager



log = LogManager('Message', logging.ERROR, logging.INFO)

repetitious = []
chat_ids = []

class Message(object):
    '''
    classdocs
    '''
    def __init__(self, data, skip=True):
        '''
        Constructor
        :param data:
        :param skip: 是否忽略重复的消息ID
        '''
        self.skip_message = skip
        self.send_data = []

        self.message_id = data.get('id')
        self.album_id = data.get('media_album_id')  # 当前消息所属的相册标识符(string)
        self.chat_id = data.get('chat_id')
        self.channel = data.get('is_channel_post')
        self.sender_id = data.get('sender_id', {}).get('user_id')
        self.date = data.get('date')
        self.message_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['date'])) if data.get('date') else None
        self.edited_date = data.get('edit_date')
        self.interaction = data.get('interaction_info', {}).get('view_count')   # 媒体消息的浏览量
        self.content = data.get('content')

        self.message_type = None
        self.text = None
        self.caption = None
        self.entities = []      # 注意，此参数是通过原始entities对象解析出来的结果，不是指向消息中的原始entities对象

        if  len(chat_ids) > 30:
            del chat_ids[0]

    def main(self):
        '''

        :return:
        '''
        if self.skip_message and [self.chat_id, self.message_id] in chat_ids:
            # log.info('Skip repetitious Message:')
            return []

        chat_ids.append([self.chat_id, self.message_id])


        self.update_any_group()
        self.parse_content()

        return self.send_data

    def parse_content(self):
        '''
        解析消息内容主体
        :return:
        '''
        if not self.content:
            return None
        result = []

        self.message_type = self.content.get('@type')
        if self.message_type == 'messageText':
            # 处理文本消息内容
            self.parse_content_text(self.content.get('text'))

        elif self.message_type == 'messagePhoto':
            if self.content.get('caption'):
                self.parse_content_caption(self.content.get('caption'))

        elif self.message_type == 'messageVideo':
            if self.content.get('caption'):
                self.parse_content_caption(self.content.get('caption'))



        return result

    def update_any_group(self):
        """
        更新数据库中特定用户的'any_group'字段。它确保
        chat_id被包含在'any_group'列表中，并且已更新的列表被存储
        在数据库中。如果操作成功，它会记录更新情况
        返回成功状态。

        :rtype: bool or None
        """
        if not self.sender_id:
            return None

        query = f"SELECT `any_group` FROM `{sql.table_users}` WHERE `id`=%s"
        any_group = sql.query(sql.database, query, [self.sender_id])
        if any_group and any_group[0] and any_group[0]['any_group']:
            any_group = any_group[0]['any_group']
        else:
            any_group = []
        if self.chat_id not in any_group:
            any_group.append(self.chat_id)
            query = f"INSERT INTO {sql.table_users} (`id`,`any_group`) VALUES (%s,%s) ON DUPLICATE KEY UPDATE `any_group`=%s"
            sql.query(sql.database, query, [self.sender_id, json.dumps(any_group), json.dumps(any_group)])

            # log.info(f'Update any_group to database.users: {self.sender_id}')
            return True


        return False

    def parse_content_text(self, data):
        '''
        解析消息内容的文本消息
        :param data: dict 消息内容的文本内容
        :return:
        '''
        if not data:
            return
        self.text = data.get('text')
        if data.get('entities'):
            self.entities = self.parse_entities(self.text, data.get('entities'))

    def parse_content_caption(self, data):
        '''
        解析附件的描述内容
        :param data:
        :return:
        '''
        self.caption = data.get('text')
        if data.get('entities'):
            self.entities = self.parse_entities(self.caption, data.get('entities'))

    def parse_entities(self, text, entities):
        '''
        解析富文本实体
        :param text: 原始文本
        :param entities: 实体列表
        :return: 解析后的实体列表
        '''
        result = []
        for entite in entities:
            result.append({
                'type': entite.get('type', {}).get('@type'),
                'text': self.slice_by_utf16(text, entite.get('offset'), entite.get('length')),
                **{key: value for key, value in entite.get('type').items() if key != '@type'}
            })
        return result

    @classmethod
    def slice_by_utf16(cls, text, offset, length):
        '''
        根据UTF-16编码的偏移和长度切分文本
        :param text: 待切分的文本
        :param offset: 开始偏移
        :param length: 切分长度
        :return: 切分后的文本
        '''
        encoded = text.encode("utf-16-le")

        start = offset * 2
        end = (offset + length) * 2

        return encoded[start:end].decode("utf-16-le")



class MessageLinkInfo(Message):
    '''
    消息链接信息
    '''
    def __init__(self, data):
        super().__init__(data.get('message'), skip=False)

        self.public = data.get('is_public')     # 是否公开消息
        self.album = data.get('for_album')


        self.main()





if __name__ == '__main__':

    from utils import client_object



    for msg in client_object.chatHistory_02.get('messages'):
        message = Message(msg, False)
        break




