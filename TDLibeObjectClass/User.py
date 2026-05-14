
'''
User 类
'''
import time
import json
import logging
from database import sql
from logg import LogManager

log = LogManager('User', logging.ERROR, logging.INFO)

class User:
    '''
    用户类
    '''
    def __init__(self, data):

        self.send_data = []
        self.profile_photo = data.get('profile_photo')

        self.id = data.get('id')
        self.type = data.get('type', {}).get('@type')
        self.username = data.get('usernames', {}).get('active_usernames', [None])[0]
        self.is_bot = data.get('is_bot')    # 是否为机器人
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.phone = data.get('phone_number')
        self.image = None
        self.status = data.get('status')

        self.contact = data.get('is_contact')    # 是否为联系人
        self.mutual = data.get('is_mutual_contact')    # 是否双向联系人
        self.premium = data.get('is_premium')    # 是否为高级用户
        self.new_chated = data.get('restricts_new_chats')   # 是否限制新聊天
        self.access = data.get('have_access')   # 是否能获取详细用户信息

    def main(self):
        '''

        :return:
        '''
        self.update_user_info()
        return self.send_data

    def update_user_info(self):
        '''
        更新本地数据库的用户信息
        将更新的用户消息和本地数据库储存的信息相比较，以达到更新本在用户信息的目的
        :return:
        '''
        change = []
        values = []
        query = f"SELECT * FROM `{sql.table_users}` WHERE `id`=%s"
        query = sql.query(sql.database, query, [self.id])
        if query and query[0]:

            for key, value in query[0].items():
                if key in ['id', 'created', 'edited']:
                    continue
                if key == 'image':
                    result = self.avatar_photo(value)
                    if result and result != value:
                        values.append(json.dumps(result))
                        change.append(key)

                elif self.__dict__.get(key) and self.__dict__.get(key) != value:
                    new_value = self.__dict__.get(key)
                    if type(new_value) in [list, dict]:
                        new_value = json.dumps(new_value)
                    values.append(new_value)
                    change.append(key)
            if change:
                log.info(f'Update these field to database.users： {change}')
                change = ','.join([f'{key}=%s' for key in change])
                values.append(self.id)
                query = f"UPDATE `{sql.table_users}` SET {change} WHERE `id`=%s"
                sql.query(sql.database, query, values)

        else:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            fields = [fields.get('Field') for fields in sql.all_tables_fields.get(sql.table_users)]
            for field in fields:
                if field in ['created', 'edited']:
                    values.append(now_time)
                    continue
                value = self.__dict__.get(field)
                if type(value) in [list, dict]:
                    # 将python的list,dict对你序列化成json串，确保安全写入数据表
                    value = json.dumps(value)
                values.append(value)
            log.info('Add new user to database.users: {}'.format(self.id))
            query = f"INSERT INTO `{sql.table_users}` VALUES ({''.join(['%s', ','] * len(fields))[:-1]})"
            sql.query(sql.database, query, values)

    def avatar_photo(self, local_param):
        '''
        解析更新消息中的用户头像信息，如果未下载过则下载
        如果头像信息发生改变也会下载
        '''


        if not self.profile_photo:
            return None

        file_id = self.profile_photo.get('id')  # 更新数据包中的头像文件ID
        result = {'id': file_id}

        # 获取本地储存的文件ID，此参数可能为空
        if local_param:
            local_id = local_param.get('id')
        else:
            local_id = None

        # 获取头像信息，优先使用大头像，
        profile_photo = self.profile_photo.get('big', self.profile_photo.get('small'))
        if not profile_photo:
            return None

        # 检查是否允许下载文件
        if not profile_photo.get('local').get('can_be_downloaded'):
            return None

        # 检查更新消息中是否包含本地文件路径
        update_local_path = profile_photo.get('local').get('path')
        if file_id != local_id or not update_local_path:
            # 头像文件ID与本地储存的文件ID不相同，则说明用户头像信息发生了改变
            # 更新消息中的本地路径为,空则说明该文件未被下载过
            self.send_data.append({
                '@type': 'downloadFile',
                'file_id': profile_photo.get('id'),
                'priority': 32,
                'synchronous': True,
                '@extra': f'download|users|image|{self.id}'
            })
            result.update({'path': None})
        elif update_local_path and not local_param.get('path'):
            result.update({'path': update_local_path})

        return result


class UserFullInfo(User):
    '''
    用户详细信息类
    '''

    def __init__(self, data, _id=None):

        super().__init__(data)

        self.id = _id or data.get('id')
        self.description = data.get('bio')
        self.called = data.get('can_be_called')     # 是否支持语音通话
        self.video_calls = data.get('can_be_called')    # 是否支持视频通话


if __name__ == '__main__':

    from utils import client_object

    user = User(client_object.updateUser_01['user'])
    user.main()
    print(user.send_data)









