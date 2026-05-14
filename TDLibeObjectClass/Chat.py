
import json
import time
import logging
from database import sql
from logg import LogManager

log = LogManager('Chat', logging.ERROR, logging.INFO)

class Chat:
    '''
    d
    '''

    def __init__(self, data):
        '''

        '''
        self.send_data = []

        self.chat_id = data.get('id')
        self.chat_type = data.get('type', {}).get('@type')

        if self.chat_type == 'chatTypeSupergroup':
            self.group_id = data.get('type', {}).get('supergroup_id')
        elif self.chat_type == 'chatTypeBasicGroup':
            self.group_id = data.get('type', {}).get('basic_group_id')
        else:
            self.group_id = None
        self.channel = data.get('type', {}).get('is_channel')
        self.title = data.get('title')
        self.description = data.get('description')

        self.member = data.get('member_count') if data.get('member_count') != 0 else None

        self.image = data.get('photo')
        self.admin = data.get('admin_id')
        self.creator = data.get('creator_id')
        self.permissions = data.get('permissions')

    def main(self):
        '''

        :return:
        '''
        self.update_local_info()

        return self.send_data

    def update_local_info(self):
        '''

        :return:
        '''
        query = f'SELECT * FROM `{sql.table_chats}` WHERE chat_id=%s'
        local_data = sql.query(sql.database, query, [self.chat_id])
        if local_data:
            local_data = local_data[0]
        else:
            local_data = {fields.get('Field'): None for fields in sql.all_tables_fields.get('chats')}

        changes = []
        values = []
        query = None
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.image = self.photo_info(local_data.get('image') or {})
        for key, value in local_data.items():
            if key in ['created', 'edited']:
                continue
            param = self.__dict__.get(key)
            if param and param != value:
                changes.append(key)
                prarm = json.dumps(param) if type(param) in [list, dict] else param
                values.append(prarm)

        if not local_data.get('chat_id'):
            changes.extend(['created', 'edited'])
            values.extend([now_time, now_time])

            query = f'INSERT INTO `{sql.table_chats}` ({",".join(changes)}) VALUES ({",".join(["%s"] * len(values))})'
            log.info(f'Add a new chat to database.chats： {self.title}')
        elif changes:
            changes.append('edited')
            values.extend([now_time, self.chat_id])
            query = f'UPDATE `{sql.table_chats}` SET {",".join([f"`{key}`=%s" for key in changes])} WHERE `chat_id`=%s'
            log.info(f'Update these field to database.chats： {changes}')
        if query:
            sql.query(sql.database, query, values)


    def photo_info(self, local_image):
        '''
        解析聊天的头像图片信息,优先获取大头像文件
        :return:
        '''

        if not self.image:
            return None


        result = None
        download = None
        for row in ['big', 'small']:

            photo = self.image.get(row)
            if not photo:
                continue
            can_download = photo.get('local').get('can_be_downloaded')
            photo_id = photo.get('chat_id')
            photo_path = photo.get('local').get('path')

            local_image_id = local_image.get('chat_id') if local_image else None
            if can_download and (not photo_path or local_image_id != photo_id):
                result = {'chat_id': photo_id}
                download = photo_id
            elif not photo_path:
                result = {'chat_id': photo_id, 'path': photo_path}

            if row == 'big':
                break
        if download:
            self.send_data.append({
                '@type': 'downloadFile',
                'file_id': download,
                'priority': 32,
                'synchronous': True,
                '@extra': f'download|chats|image|{self.chat_id}'
            })

        return result



if __name__ == '__main__':


    from utils import client_object

    chat = Chat(client_object.updateNewChat_02.get('chat')).update_local_info()








