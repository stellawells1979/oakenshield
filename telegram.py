'''
规则机器人的主程序
处理规则机器人收到的所有更新
并对更新做出必要的响应

调用 communication 文件的 crave 向 telegram bot api 轮旬方式获取更新
获取更新的依据为专属于此机器人的更新标识符（update_id）,此标识符从 0 开始随你获取的更新次数
递增，所以你必须实时更新并可靠保存此参数，以保证更新的唯一性

telegram bot api 的更新类型较多，为此你应该为第个更新类型创建一个解析函数，本项目对这类函
数统称为功能函数，所创建的功能函数必须能够完全解析所属更新并按需对更新做出响应，此程序会按更
新类型调用相应功能函数并按功能函数的处理逻辑向 telegram 服务器请求

此程序的错误提示会以红色字体打印中运行状态栏
'''

import json
import time
import logging
from flask import Flask
from flask import request as flask_request
from threading import Thread, Event
from queue import Queue, Empty
from database import sql
from utils.account import account
from utils.TGrequest import crave
from message import message_filter
from callbackquery import CallbackQuery
from logmanage import DailyLogManager

# 配置日志管理器
log = DailyLogManager('Telegram', logging.ERROR, logging.INFO)


class Telegram:
    '''
    y
    '''

    def __init__(self, bot):
        """
        初始化运行环境。
        :var self.update_id 必须实时更新以确保唯一性。
        """
        self.bot = bot
        self.bot_id = account.attribute(bot, 'id')
        self.send_data = []

    def set_webhook(self, url):
        '''
        设置webhook
        :param url:
        :return:
        '''
        return crave.send(self.bot, 'setWebhook', {'url': url})

    def check_webhook(self):
        '''
        查看机器人的webhook详情
        :return:
        '''
        return crave.send(self.bot, 'getWebhookInfo')

    def process_update(self, update):
        """
        解析并处理单个更新。
        :param update: Telegram 更新 JSON 对象
        """
        result = []
        if 'message' in update:
            result = message_filter(self.bot, update)
        elif 'callback_query' in update:
            result = CallbackQuery(self.bot, update).main()

        return result

    @classmethod
    def error(cls, description, code=None):
        """
        返回错误描述信息。
        :param description: 错误详情
        :param code: 错误代码
        :return: 错误的文本信息
        """
        if code == 503:
            return f"{code}： {description}"
        return crave.error(description)


class Main:
    '''
    主处理模式
    :return:
    '''
    def __init__(self):
        self.send_data = Queue()    # 定义一个参数池，储存后续程序处理生成的请求对你
        # 创建独立线程运行 telegram_requests()
        self.stop_event = Event()
        self.telegram_thread = Thread(target=self.telegram_requests, daemon=True)
        self.telegram_thread.start()

    def remove_expired_verifications(self):
        """
        移除超时的验证用户。
        数据表中储存这些用户的信息。
        """
        query = f'SELECT bot, chat, verify FROM `{sql.table_restriction}` WHERE verify IS NOT NULL'
        result = sql.query(sql.database, query, None)
        if not result:
            return

        now_date = time.time()
        for item in result:
            if not item:
                continue
            verify = json.loads(item.get('verify', {}))
            expired_keys = []
            for key, value in verify.items():
                # 将验证超时用户移出聊天
                if now_date > value:
                    self.send_data.put([item.get('bot'), 'kickChatMember', {'chat_id': item.get('chat'), 'user_id': int(key)}, None])
                    expired_keys.append(key)
            if not expired_keys:
                continue

            for key in expired_keys:
                del verify[key]
            # 将最新的验证数据更新到数据表
            update_query = f'UPDATE `{sql.table_restriction}` SET verify=%s, edited=NOW() WHERE bot=%s AND chat=%s'
            sql.query(sql.base_database, update_query, [json.dumps(verify), item.get('bot'), item.get('chat')])

    def telegram_requests(self):
        """
        处理队列中的 API 消息请求，并确保请求的时效性。
        """
        self.remove_expired_verifications()     # 从数据库提取验证过期的用户，并将其移出群聊

        while not self.stop_event.is_set():
            try:
                data = self.send_data.get(timeout=1)
            except Empty:
                continue

            if data[3] and data[3].get('delay'):
                now_date = time.time()
                if data[3].get('delay') > now_date:
                    # 如果消息被延迟，重新放入队列
                    self.send_data.put(data)
                    continue
            response = crave.send(data[0], data[1], data[2])

            if response['ok'] and data[3] and data[3].get('delete'):
                message_id = response['result']['message_id']
                self.send_data.put([
                    data[0],
                    'deleteMessage',
                    {'chat_id': data[2]['chat_id'], 'message_id': message_id},
                    {'delay': data[3]['delete']}
                ])
            elif not response['ok'] and response.get('description'):
                error = response['description']
                if error in ['Request Timeout', 'Request ConnectionError'] or error.startswith('Unkown:'):
                    self.send_data.put(data)
                log.info(f'telegram_requests: {response}')
            else:
                print(f" Request result: {response}")


    def handle_update(self, route, update):
        '''
        解析路由并向处理环节传递相应参数
        '''
        if not update:
            return []
        if route == '/telegram/rules':
            bot = 'rules'
            telegram = Telegram('rules')
        elif route == '/telegram/search':
            bot = 'search'
            telegram = Telegram('search')
        else:
            return []
        result = telegram.process_update(update)

        for item in result:
            item.insert(0, bot)
            self.send_data.put(item)
        return False



main = Main()

app = Flask(__name__)


@app.route('/telegram/<path:anything>', methods=['GET', 'POST'])
def route_all():
    '''
    :return:
    '''
    # 从请求体中读取 Telegram 发来的 JSON 更新数据
    # silent=True 的意思是：如果不是合法 JSON，不抛异常，而是返回 None
    update = flask_request.get_json(silent=True) or {}

    # 获取请求头并提取路由字段
    environ_info = dict(flask_request.environ)
    path_info = environ_info['PATH_INFO']

    # 创建线程处理更新
    t = Thread(target=main.handle_update, args=(path_info, update))
    t.daemon = True
    t.start()
    return 'ok', 200


if __name__ == '__main__':


    app.run(host='192.168.1.102', port=5000)





