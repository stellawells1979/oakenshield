
'''
人
'''
import json
import logging
from database import sql
from logg import LogManager

log = LogManager('File', logging.ERROR, logging.INFO)

class FileObject:
    '''
    处理文件
    '''


    def __init__(self, data):

        self.extra = data.get('@extra')
        self.file_id = data.get('chat_id')
        self.size = data.get('size')
        self.path = data.get('local', {}).get('path')

    def main(self):
        '''

        :return:
        '''

        if self.extra:
            extras = self.extra.split('|')
            if extras[0] == 'download' and extras[2] == 'image':
                self.update_face(extras[1], int(extras[3]), self.path)

    @classmethod
    def update_face(cls, table, pri_id, param):
        '''
        更新本地用户的头像信息
        :return:
        '''
        query = f"SELECT `image` FROM `{table}` WHERE `chat_id`=%s"
        query = sql.query(sql.database, query, [pri_id])
        if query and query[0]:
            user_info = query[0].get('image', {})
            if not user_info or user_info.get('path') != param:
                user_info.update({'path': param})
                query = f"UPDATE `{table}` SET `image`=%s WHERE `chat_id`=%s"
                sql.query(sql.database, query, [json.dumps(user_info), pri_id])
        else:
            query = f"INSERT INTO `{table}`(`chat_id`, `image`) VALUES (%s, %s)"
            sql.query(sql.database, query, [pri_id, json.dumps({'path': param})])

        log.info(f'Update image to {sql.database}.{table}: {param}')



if __name__ == '__main__':

    from utils import client_object

    file = FileObject(client_object.file_01)
    file.main()


















