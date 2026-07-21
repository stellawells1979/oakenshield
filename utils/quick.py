'''
此类集成了获取聊天信息的工具函数
'''
import json
from utils.TGrequest import request
from database import sql
import logging
from logmanage import LogManager
from utils.account import account

log = LogManager('Quick', logging.WARNING, logging.INFO)

class Quick:
    '''
    1
    '''

    def __init__(self, bot=None):
        '''

        '''
        self.bot = bot

    @classmethod
    def update_chat(cls, bot, chat, chat_type, title, bot_status=None):
        '''

        :param bot:
        :param chat:
        :param chat_type:
        :param title:
        :param bot_status:
        :return:
        chatMember_expection = {
            'user': {'id': 8598030336, 'is_bot': True, 'first_name': 'rulesbot', 'username': 'wellwen_bot'},
            'status': 'administrator',
            'is_anonymous': True,       # 当前状态是否为隐藏状态
            'can_be_edited': False,     # 员是否有权限编辑管理员列表
            'can_manage_chat': True,    # 是否有权限访问聊天事件日志、获取推广列表、查看隐藏的超级群组和频道成员、举报垃圾信息、忽略慢速模式，以及无需支付 Telegram 星星即可向聊天发送消息。
            'can_change_info': True,    # 是否有权限更改聊天标题、头像和其他设置。
            'can_delete_messages': True,    # 是否有权限删除聊天中的消息。
            'can_invite_users': True,       # 是否有权限邀请新成员加入聊天。
            'can_restrict_members': True,   # 是否有权限限制成员的权限。
            'can_pin_messages': True,       # 是否有权限将消息置顶。
            'can_manage_topics': False,     # 是否有权限管理聊天主题，包括创建、重命名、关闭和重新打开论坛主题。
            'can_promote_members': True,    # 是否有权限提升其他成员为管理员。
            'can_manage_video_chats': True,     # 是否有权限管理视频聊天
            'can_post_stories': False,      # 是否有权限发布故事。
            'can_edit_stories': False,      # 是否有权限编辑故事。
            'can_delete_stories': False,    # 是否有权限删除故事。
            'can_manage_tags': False,       # 是否有权限编辑普通成员的标签
            'can_manage_voice_chats': True
        }
        '''

        result = None

        table = sql.table_rules if bot == 'rules' else sql.table_search
        chat_admin = None
        if not bot_status:
            # 获取机器人在群组中的身份状态
            bot_status = cls.chat_member(bot, account.attribute(bot, 'id'), chat)

        if bot_status and bot_status.get('status') == 'administrator':
            # 如果机器人是管理员身份，则获取当前群组的管理员列表，并将相关信息添加或更新到数据库
            chat_admin = cls.get_administrators(bot, chat)

        # 序列化机器人状态参数（如果有铲的话）
        bot_status = json.dumps(bot_status, ensure_ascii=False) if bot_status else None

        # 构建数据库查询语句
        query = (f"INSERT INTO {table} (`chat`,`title`,`type`,`bot_status`) VALUES (%s,%s,%s,%s) "
                 f"ON DUPLICATE KEY UPDATE `title`=%s, `bot_status`=%s")
        values = [chat, title, chat_type, bot_status, title, bot_status]

        if chat_admin:
            # 如果获取到当前群组的管理员列表，也一并写入数据库
            chat_admin = json.dumps(chat_admin, ensure_ascii=False) if chat_admin else None
            query = (f"INSERT INTO {table} (`chat`,`title`,`type`,`administrators`,`bot_status`) VALUES (%s,%s,%s,%s,%s) "
                     f"ON DUPLICATE KEY UPDATE `title`=%s,`administrators`=%s,`bot_status`=%s")
            values = [chat, title, chat_type, chat_admin, bot_status, title, chat_admin, bot_status]
            result = True
        sql.query(sql.database, query, values)

        return result

    @classmethod
    def permissions(cls, restrict=None):
        '''
        限制和解除限制
        :param restrict: 些参数有效时为添加限制
        :return:
        '''
        return {
            'can_send_messages': False if restrict else True,
            'can_send_audios': False if restrict else True,
            'can_send_documents': False if restrict else True,
            'can_send_photos': False if restrict else True,
            'can_send_videos': False if restrict else True,
            'can_send_video_notes': False if restrict else True,
            'can_send_voice_notes': False if restrict else True,
            'can_send_polls': False if restrict else True,
            'can_send_other_messages': False if restrict else True,
            'can_add_web_page_previews': False if restrict else True,
            'can_change_info': False if restrict else True,
            'can_invite_users': False if restrict else True,
            'can_pin_messages': False if restrict else True,
            'can_manage_topics': False if restrict else True,
        }

    @classmethod
    def get_administrators(cls, bot, group):
        '''
        获取指定群组的管理员
        :param bot:
        :param group:
        :return:
        '''
        response = request.send(bot, 'getChatAdministrators', {'chat_id': group})
        if response and response['ok']:
            return response['result']

        return []

    @classmethod
    def chat_member(cls, bot, user, group):
        '''
        获取聊天中某个成员的信息
        :param bot:
        :param group:
        :param user:
        :return:
        '''
        response = request.send(bot, 'getChatMember', {'chat_id': group, 'user_id': user})
        if response and response['ok']:
            return response['result']

        return None

    @classmethod
    def chat_info(cls, bot, group):
        '''
        获取某个聊天的信息
        :param bot:
        :param group:
        :return:
        '''
        response = request.send(bot, 'getChat', {'chat_id': group})
        if response:
            return response['result']
        return []

    @classmethod
    def get_chatmembercount(cls, bot, group):
        '''
        获取聊天中成员数量
        :param bot:
        :param group:
        :return: int
        '''
        response = request.send(bot, 'getChatMemberCount', {'chat_id': group})
        if response:
            return response['result']

        return 0


quick = Quick()

if __name__ == '__main__':

    pass

