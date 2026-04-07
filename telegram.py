
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
import logging
from flask import Flask
from flask import request as flask_request
from threading import Thread
import run_config
from database import sql
from utils.bots import bots
from utils.TGrequest import crave
from message import message_filter
from callbackquery import CallbackQuery
from logmanage import DailyLogManager



# 配置日志管理器
log = DailyLogManager('Telegram', logging.ERROR, logging.INFO)

# 提取常量
REQUEST_DELAY = 3  # 请求更新的时间间隔（秒）


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
        self.bot_id = bots.attribute(bot, 'id')
        self.update_id = self.uphold_update_id()
        self.send_data = []

    def telegram_requests(self):
        """
        处理队列中的 API 消息请求，并确保请求的时效性。
        """
        index = 0
        while index < len(self.send_data):
            data = self.send_data[index]
            if data[2] and data[2].get('delay') and data[2].get('delay') > run_config.date:
                log.info('telegram_requests: this message is delayed')
                index += 1
                continue
            response = crave.send(self.bot, data[0], data[1])
            if response['ok']:
                if data[2] and data[2].get('delete'):
                    message_id = response['result']['message_id']
                    self.send_data.append([
                        'deleteMessage',
                        {'chat_id': data[1]['chat_id'], 'message_id': message_id},
                        {'delay': data[2]['delete']}
                    ])
                del self.send_data[index]
            elif not response['ok']:
                error_info = self.error(response.get('description'), response.get('error_code'))
                log.info(f'telegram_requests: {error_info}')
                del self.send_data[index]
            else:
                index += 1
                log.info(f" Request result: {response}")

    def process_update(self, update):
        """
        解析并处理单个更新。
        :param update: Telegram 更新 JSON 对象
        """
        self.update_id = update['update_id'] + 1
        self.uphold_update_id(self.update_id)  # 更新数据库中的消息偏移量
        result = []
        if 'message' in update:
            result = message_filter(self.bot, update)
        elif 'callback_query' in update:
            result = CallbackQuery(self.bot, update).main()

        self.send_data.extend(result)

    def remove_expired_verifications(self):
        """
        移除超时的验证用户。
        数据表中储存这些用户的信息。
        """
        query = f'SELECT chat, verify FROM `{sql.table_restriction}` WHERE bot={self.bot_id} AND verify IS NOT NULL'
        result = sql.query(sql.base_database, query)
        if result:
            for chat_id, verify_json in result:
                verify = json.loads(verify_json)
                expired_keys = [key for key, value in verify.items() if run_config.date > value]
                for key in expired_keys:
                    self.send_data.append(['kickChatMember', {'chat_id': chat_id, 'user_id': int(key)}])
                    del verify[key]
                if expired_keys:
                    update_query = f'UPDATE `{sql.table_restriction}` SET verify=%s, edited=NOW() WHERE bot=%s AND chat=%s'
                    sql.query(sql.base_database, update_query, [json.dumps(verify), self.bot_id, chat_id])
                    log.warning('remove_expired_verifications: Kicked user for verification timeout')

    def uphold_update_id(self, update_id=None):
        """
        维护当前机器人的 update_id 参数。
        :param update_id: 默认传入的新值，如果为空，则查询数据库得到。
        :return: 当前机器人保存的 update_id 参数
        """

        if update_id is None:
            query = f'SELECT update_id FROM `{sql.table_manage}` WHERE id=%s'
            result = sql.querys(sql.base_database, query, [self.bot_id])

            if result and result[0]:
                return result[0].get('update_id')
            else:
                default_update_id = -1
                query = f'INSERT INTO `{sql.table_manage}` (id, name, update_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE update_id=%s'
                sql.querys(sql.base_database, query, [self.bot_id, self.bot, default_update_id, default_update_id])
                return default_update_id
        query = f'UPDATE `{sql.table_manage}` SET update_id=%s, edited=NOW() WHERE id=%s'
        sql.querys(sql.base_database, query, [update_id, self.bot_id])
        return update_id

    def set_webhook(self, url):
        '''
        设置webhook
        :param bot:
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

app = Flask(__name__)

def handle_update(update):
    """
    后台处理单个 Telegram 更新。

    这里放真正耗时的业务逻辑：
    1. 解析 update
    2. 调用你的 Telegram 业务处理类
    3. 执行发送消息、修改群组状态、数据库更新等操作

    这样做的好处是：
    - webhook 接口可以立刻返回 200
    - Telegram 不会因为超时而重复投递同一个 update
    - 业务逻辑与 HTTP 响应解耦
    """
    telegram = Telegram("rules")  # TODO: 改成你的实际 bot 名称，例如 rules / search
    telegram.process_update(update)
    telegram.telegram_requests()


@app.route("/telegram", methods=["POST"])
@app.route("/telegram/<path:anything>", methods=["POST"])
def telegram_webhook(anything=""):
    """
    Telegram webhook 入口。

    这个接口只负责：
    1. 接收 Telegram 推送过来的 update
    2. 启动后台线程处理更新
    3. 立即返回 200 给 Telegram

    注意：
    - 不要在这里做耗时逻辑
    - 不要在这里 sleep
    - 不要在这里执行大量数据库或网络请求
    """
    # 从请求体中读取 Telegram 发来的 JSON 更新数据
    # silent=True 的意思是：如果不是合法 JSON，不抛异常，而是返回 None
    update = flask_request.get_json(silent=True) or {}

    # 创建后台线程，异步处理更新
    # daemon=True 表示主程序退出时，这个线程也随之结束
    # 适合 webhook 这种“短任务触发”的场景
    t = Thread(target=handle_update, args=(update,))
    t.daemon = True
    t.start()

    # 立刻返回 200，告诉 Telegram：我已经收到这条 update 了
    # 这样 Telegram 就不会因为等待过久而重复重发
    return "ok", 200


if __name__ == "__main__":

    telegram = Telegram('rules')
    info = telegram.check_webhook()
    input(info)


    # 监听 0.0.0.0 允许局域网/反代服务器访问
    # port 要和你 Nginx 反代到的后端端口一致
    app.run(host="0.0.0.0", port=5000)












    # log.info('Telegram 正在初始化运行环境')
    #
    # # 创建运行函数
    # def run_bot(use_bot):
    #     '''
    #
    #     :param use_bot:
    #     :return:
    #     '''
    #     telegram = Telegram(use_bot)
    #     telegram.main()
    #
    #
    # # 定义需要启动的机器人名称
    # bot_names = ['rules', 'search']  # 两个机器人分别命名
    #
    # # 创建线程为每个机器人分别运行
    # threads = []
    # for bot_name in bot_names:
    #     bot_thread = threading.Thread(target=run_bot, args=(bot_name,))
    #     threads.append(bot_thread)
    #     bot_thread.start()
    #
    # # 确保主线程等待所有子线程完成
    # for thread in threads:
    #     thread.join()
    #
    # telegram = Telegram('rules')
    #
    # telegram.main()




