'''
获取公开群组详情
此类为静态类，修改时应济注意控制类属性
'''
import json
import logging
import random
import time
from datetime import datetime
import config
from database import sql
from utils.tagtication import tagnote
from logg import LogManager
from utils import quick
from utils.Sharelinkchecker import check_share
from TDLibeObjectClass.Chat import Chat
from TDLibeObjectClass.Message import Message, MessageLinkInfo
from TDLibeObjectClass.Supergroupfullinfo import SupergroupFullInfo
from TDLibeObjectClass.Chatinvitelinkinfo import ChatInviteLinkInfo



log = LogManager('Share', logging.WARNING, logging.INFO)


class Share:
    '''
    1
    :var share_links: dict 一个储存分享链接的容器，记录了一个分享链接在当前程序中的状态，None表示未处理，True表示正在处理 False表示处理失败
    :var send_data: list 在解析分享内容前先将此容器清空。在解析分享链接内容的过程中，如果需要进一步请求其它信息时，将请求追加到此容器

    aggregator_share_link() 方法收集分享链接，查询数据和当前share_links容器是否包含当前链接，如果没有则追加到 share_links 容器
    get_sharelink() 方法从 share_links 获取一个未处理的分享链接
    parse_share_content() 方法解析分享链接的内容，解析成功会写入数据库，然后从 share_links 中移除相应链接
    '''

    def __init__(self):

        self.next_time = 60 + time.time()
        self.send_data = []
        self.share_links = {}
        self.all_chat_type = {'chatTypeBasicGroup', 'chatTypeSupergroup', 'chatTypePrivate', 'chatTypeSecret'}

    def aggregator_share_link(self, data):
        '''
        聚合分享链接
        :return:
        '''

        if not data:
            return
        for entity in data:

            link = entity.get('url')

            if not link:
                continue

            pamrams = quick.parse_tme_url(link)

            if not pamrams:
                continue
            domain, name, extra = pamrams

            if (not link or not link.startswith('https://t.me/') or link.find('?') != -1 or
                    link.find('=') != -1 or name in config.service_paths or link in self.share_links ):
                continue


            if name.startswith('+'):
                # 不处理关于私密邀请链接分享的群组
                continue


            query = f"SELECT `url`,`chat_id`,`edited` FROM `{sql.table_shares}` WHERE `url`=%s"
            query = sql.query(sql.database, query, [link])
            if query and query[0] and query[0].get('edited'):
                edited_time = query[0]['edited']
                days = (datetime.now().date() - edited_time.date()).days
                if days > 30:
                    self.share_links.update({link: None})
            else:
                self.share_links.update({link: None})

    def get_sharelink(self):
        '''
        处理 telegram 的分享链接
        链接示例：https://t.me/+0OxgaJIBSDJhNTRl 这是一个私密邀请链接
        链接示例：https://t.me/hkkz8/738 这是一个公开的消息链接，中间的 hkkz8 是群组的名称，后面是消息的ID
        链接示例：https://t.me/hkkz8 这是一个公开的群组链接，其中 hkkz8 是群组的名称
        链接示例：https://t.me/c/1219413616/3578378 私有/隐藏来源消息链接，c表示这是内部 chat 链接格式

        :return:
        '''
        # 首先将 link 解析为 domain, name, message_id
        result = []
        now_time = time.time()

        if self.next_time > now_time:
            return result

        for link, statu in self.share_links.items():
            if statu is not None:
                continue

            query = f"SELECT `url` FROM `{sql.table_shares}` WHERE `url`=%s"
            query = sql.query(sql.database, query, [link])
            if query:
                continue


            link_statu = check_share.check(link)
            if link_statu is None:
                continue
            elif link_statu is False:
                self.share_links.update({link: False})
                continue

            domain, name, extra = quick.parse_tme_url(link)
            if not name:
                continue

            if extra:
                result = {
                    '@type': 'getMessageLinkInfo',
                    'url': link,
                    '@extra': f"share|get|messageLinkInfo|{name}|0|{link}"
                }
            else:
                result = {
                    '@type': 'searchPublicChat',
                    'username': name,
                    '@extra': f"share|search|chat|{name}|0|{link}"
                }
            if result:
                self.next_time = now_time + random.uniform(90, 240)
                self.share_links.update({link: True})
                break

        return result

    def parse_share_content(self, data):
        '''
        解析从分享链接中获取到的内容
        :param data:
        :return:
        '''
        # 将请求容器清空, 将请求容器清空, 将请求容器清空
        self.send_data = []

        data_type = data.get('@type')
        extra = data.get('@extra')

        result = None
        steat, method, obj, name, sid, url = extra.split('|', 5)

        if data_type == 'error':
            self.parse_error(extra, data)

        elif obj == 'messageLinkInfo':
            result = self.parse_share_content_messageLinkInfo(extra, data)

        elif obj == 'chat':
            result = self.parse_share_content_chat(extra, data)

        elif obj == 'chatInviteLinkInfo':
            result = self.parse_share_content_chatinvitelinkinfo(extra, data)

        elif obj == 'chatHistory':
            result = self.parse_share_content_album(extra, data)
            log.info(f'收到请求的专辑信息')

        elif obj in ['supergroupFullInfo']:
            result = self.parse_share_content_supergroup(extra, data)

        if result:
            changes = [f'`{key}`' for key, value in result.items() if value is not None]
            values = [json.dumps(value) if type(value) in [list, dict] else value for key, value in result.items() if value is not None]
            query = (
                f"INSERT INTO `{sql.table_shares}` ({','.join(changes)}) VALUES ({','.join(['%s'] * len(changes))}) "
                f"ON DUPLICATE KEY UPDATE {','.join([field + '=%s' for field in changes[1:]])}")
            sql.query(sql.database, query, values + values[1:])

        if not self.send_data and url in self.share_links:
            del self.share_links[url]

        return self.send_data

    def parse_share_content_album(self, extra, data):
        '''
        解析分享内容中关于相册对你的信息
        如果在前面解析分享的帖子信息中缺少帖子的描述，通常会触发这个逻辑
        :param extra:
        :param data: 来自getChatHistory方法获取到消息集，参演会包含多个 message 对象
        :return:
        '''
        steat, method, obj, name, sid, url = extra.split('|', 5)
        for message_obj in data.get('messages'):

            params = Message(message_obj, False).__dict__

            # 查找当前消息所属和相册ID，并与回调消息（extra）中的 sid 进行比较，如果同属于一个相册且包含描述（caption）字段，则采用此内容
            if params.get('album_id') == sid and params.get('caption'):
                # 定义标签
                tag = self.parse_tag_fromtext(params.get('caption'), params.get('entities'))

                return {
                    'url': url,
                    'description': params.get('caption'),
                    'tag': ','.join(tag) if tag else None,
                    'render': 'admin',
                }

        return None

    def parse_share_content_chat(self, extra, data):
        '''
        解析分享只穿中的陈琦对象
        :param extra:
        :param data:
        :return:
        '''
        steat, method, obj, name, sid, url = extra.split('|', 5)
        data = Chat(data).__dict__

        if data.get('chat_type') == 'chatTypePrivate':
            # 排队个人聊天
            return None

        share_type = None
        if method == 'search':
            group_id = data.get('group_id')
            share_type = 'channel' if data.get('channel') else 'group'

            if data.get('chat_type') == 'chatTypeSupergroup':
                self.send_data.append({
                    '@type': 'getSupergroupFullInfo',
                    'supergroup_id': group_id,
                    '@extra': f"share|get|supergroupFullInfo|{name}|{group_id}|{url}"
                })
            elif data.get('chat_type') == 'chatTypeBasicGroup':
                self.send_data.append({
                    '@type': 'getBasicGroup',
                    'basic_group_id': group_id,
                    '@extra': f"share|get|basicgroup|{name}|{group_id}|{url}"
                })
        # 返回需要更新到数据库的字段

        tag = tagnote.create_tag(data.get('title'), 2)
        return {
            'url': url,
            'share_type': share_type,
            'share_title': data.get('title') if method == 'search' else None,
            'chat_id': data.get('chat_id'),
            'chat_type': data.get('chat_type'),
            'group_id': data.get('group_id'),
            'title': data.get('title'),
            'name': name,
            'member': data.get('member'),
            'tag': ','.join(tag) if tag else None,
        }

    def parse_share_content_chatinvitelinkinfo(self, extra, data):
        '''

        :param extra:
        :param data:
        :return:
        '''
        steat, method, obj, name, sid, url = extra.split('|', 5)
        data = ChatInviteLinkInfo(data).__dict__
        tag = tagnote.create_tag(data.get('title'), 2)
        tag = tag + tagnote.create_tag(data.get('description'), 2)

        return {
            'url': url,
            'share_title': data.get('title'),
            'chat_id': data.get('chat_id'),
            'chat_type': data.get('chat_type'),
            'title': data.get('title'),
            'name': name,
            'member': data.get('member_count'),
            'tag': ','.join(tag) if tag else None,
            'description': data.get('description'),
            'render': 'admin'
        }

    def parse_share_content_messageLinkInfo(self, extra, data):
        '''
        解析分享内容中的消息链接对象
        :param extra:
        :param data:
        :return:
        '''
        if not data.get('message'):
            return None

        steat, method, obj, name, sid, url = extra.split('|', 5)

        # 调用MessageLinkInfo解析消息链接信息
        data = MessageLinkInfo(data).__dict__

        # 读取这个消息的各属性和构建数据库更新数据
        description = data.get('caption') or data.get('text') or ''     # 通常是媒体消息的附件描述内容
        tag = self.parse_tag_fromtext(description, data.get('entities'))
        share_type = data.get('message_type').split('message')[-1]

        # 另外需要获取当前消息的聊天室详情以完整分享信息
        self.send_data.append({
            '@type': 'getChat',
            'chat_id': data.get('chat_id'),
            '@extra': f"share|get|chat|{name}|{data.get('chat_id')}|{url}"
        })

        # 如果没有媒体描述内容且消息是专辑相册(album),则说明描述内容可能包含在同一相册的其它媒体中
        if not description and data.get('album') and data.get('album_id') != '0':
            # 构建请求获取当前消息的上下文，以获取当前消息的描述字段内容
            self.send_data.append({
                '@type': 'getChatHistory',
                'chat_id': data.get('chat_id'),
                'from_message_id': data.get('message_id'),  # 从相册消息 ID 开始（如果有）
                'offset_order': -10,
                'limit': 10,
                'only_local': False,
                '@extra': f"share|get|chatHistory|{name}|{data.get('album_id')}|{url}"
            })

        return {
            'url': url,
            'share_type' : share_type.lower() if share_type else None,
            'chat_id': data.get('chat_id'),
            'channel': data.get('channel'),
            'name': name,
            'post_id': data.get('message_id'),
            'members': data.get('interaction'),
            'tag': ','.join(tag) if tag else None,
            'description': description,
            'render': 'admin'
        }

    def parse_share_content_supergroup(self, extra, data):
        '''
        解析解析分享内容中的超级群组对象
        :param extra:
        :param data:
        :return:
        '''
        steat, method, obj, name, sid, url = extra.split('|', 5)
        data = SupergroupFullInfo(data).__dict__
        tag = tagnote.create_tag(data.get('description'), 2)
        return {
            'url': url,
            'tag': ','.join(tag) if tag else None,
            'description': data.get('description'),
            'render': 'admin'
        }

    def parse_error(self, extra, data):
        '''

        :param extra:
        :param data:
        :return:
        '''
        steat, method, obj, name, sid, url = extra.split('|', 5)
        if data.get('code') == 429:
            if data.get('message') and 'retry after' in data.get('message'):
                retry = data.get('message').split('retry after')[-1].strip()
                if retry.isdigit():
                    self.next_time = int(retry) + time.time() + 30
        elif url in self.share_links:
            self.share_links.update({url: False})

        log.warning(data)

        return None

    @classmethod
    def parse_tag_fromtext(cls, text, entities=None):
        '''
        从可能包含标签的 entities 对象或文本中解析出标签
        :param text:
        :param entities:
        :return:
        '''
        result = tagnote.create_tag(text, 2)
        if entities:
            tags = [entity.get('text') for entity in entities if entity.get('type') == 'textEntityTypeHashtag']  # 媒体标签
            for tag in tags:
                if tag not in result:
                    result.append(tag)
        return result

share = Share()


if __name__ == '__main__':

    from utils import client_object


    share.parse_share_content(client_object.error_02)


