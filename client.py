'''
4
'''
import json
import sys
import time
import config
from ctypes import CDLL, CFUNCTYPE, c_char_p, c_double, c_int
import logging
from logg import LogManager

from TDLibeObjectClass.File import FileObject
from TDLibeObjectClass.Message import Message
from utils.share import share

log = LogManager('client', logging.ERROR, logging.INFO)


class TdlibClient:
    '''
    初始化客户端
    '''

    def __init__(self):

        # 加载 TDLib 动态链接库
        tdjson = CDLL(config.library_path)

        create_client = tdjson.td_create_client_id
        create_client.restype = c_int
        create_client.argtypes = []

        self.query_receive = tdjson.td_receive
        self.query_receive.restype = c_char_p
        self.query_receive.argtypes = [c_double]

        self.query_send = tdjson.td_send
        self.query_send.restype = None
        self.query_send.argtypes = [c_int, c_char_p]

        self.query_execute = tdjson.td_execute
        self.query_execute.restype = c_char_p
        self.query_execute.argtypes = [c_char_p]

        log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)
        set_log_message_callback = tdjson.td_set_log_message_callback
        set_log_message_callback.restype = None
        set_log_message_callback.argtypes = [c_int, log_message_callback_type]

        def on_log_message_callback(verbosity_level, mess):
            '''

            :param verbosity_level:
            :param mess:
            :return:
            '''
            if verbosity_level == 0:
                sys.exit('TDLib fatal error: %r' % mess)

        # 设置日志级别
        on_log_message_callback = log_message_callback_type(on_log_message_callback)
        set_log_message_callback(0, on_log_message_callback)

        # 测试与TDLib通信状态,此处应返回包 @type: ok 的字段
        testing = self.send_execute({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': 1, '@extra': 1.01234})
        log.info(f'TDLib communication test result: {testing}')
        time.sleep(2)


        self.client = create_client()
        time.sleep(2)

        # 设置代理
        if config.proxy:
            self.setup_and_verify_proxy()

    def send(self, datas):
        '''

        :param datas:
        :return:
        '''
        query_json = json.dumps(datas).encode()
        self.query_send(self.client, query_json)

    def receive(self):
        '''

        :return:
        '''
        result = self.query_receive(2.0)
        if result:
            result = json.loads(result.decode('utf-8'))
            return result
        return None

    def send_execute(self, query):
        '''

        :param query:
        :return:
        '''
        query_json = json.dumps(query).encode('utf-8')
        result = self.query_execute(query_json)
        if result:
            result = json.loads(result.decode('utf-8'))
        return result

    def setup_and_verify_proxy(self):
        '''
        设置并验证 TDLib 代理
        '''

        # 构建 addProxy 查询（启用！）
        proxy_data = {
            '@type': 'addProxy',
            'server': '127.0.0.1',
            'port': 10808,
            'enable': True,  # 关键：启用代理
            'type': {'@type': 'proxyTypeSocks5'}
        }

        # 发送添加代理
        self.send(proxy_data)
        log.info(f'添加 (enabled=True)')

        time.sleep(2)

    def account(self):
        '''
        :return:
        '''
        while True:
            events = self.receive()
            if not events:
                continue

            events_type = events.get('@type')

            if events_type == 'updateAuthorizationState':
                auth_state = events.get('authorization_state', {})
                auth_type = auth_state.get('@type')

                if auth_type == 'authorizationStateWaitTdlibParameters':
                    print('正在提交参数')
                    self.send(config.authorize_params)

                elif auth_type == 'authorizationStateWaitEncryptionKey':
                    print('正在设置加密密钥')
                    self.send({
                        '@type': 'checkDatabaseEncryptionKey',
                        'encryption_key': ''
                    })

                elif auth_type == 'authorizationStateWaitPhoneNumber':
                    print('正在提交手机号')
                    self.send({
                        '@type': 'setAuthenticationPhoneNumber',
                        'phone_number': config.account_phone
                    })

                elif auth_type == 'authorizationStateWaitCode':
                    long_code = ''
                    while len(long_code) < 5:
                        long_code = input('请输入验证码：')
                    self.send({
                        '@type': 'checkAuthenticationCode',
                        'code': long_code
                    })

                elif auth_type == 'authorizationStateWaitPassword':
                    password = input('请输入两步验证密码：')
                    self.send({
                        '@type': 'checkAuthenticationPassword',
                        'password': password
                    })

                elif auth_type == 'authorizationStateReady':
                    print('授权完成，客户端已就绪')
                    return True

                else:
                    print(f'未处理的授权状态: {auth_type}')

        return False





if __name__ == '__main__':

    clinent = TdlibClient()

    if clinent.account():
        log.info('授权成功，开始运行')
    else:
        log.error('授权失败，请检查账号信息')
        exit(1)


    while True:
        now_time = time.time()
        send_data = []
        update = clinent.receive()
        if not update:
            continue

        update_type = update.get('@type')
        update_extra = update.get('@extra')
        print('0000000000000000', update_type, '//', len(share.share_links))
        # print(update)


        # 获取一条分享链接并生成相应方法请求分享链接的详情，并设置间隔时间，控制请求频率
        share_link = share.get_sharelink()
        if share_link:
            send_data.append(share_link)


        if update_extra:
            extra = update.get('@extra').split('|')
            if extra[0] == 'share':
                # 如果收到分享链接请求的响应，则调用方法解析内容并适当调整间隔时间，稍微提升请求频率
                send_data.extend(share.parse_share_content(update))

            elif extra[0] == 'download' and extra[2] == 'file':
                FileObject(update).main()

        elif update_type == 'error':
            log.warning(update)

        # 以下是随机更新
        elif update_type == 'updateUser':
            pass
            # send_data = User(update.get('user')).main()

        elif update_type == 'updateNewChat':
            pass
            # send_data = Chat(update.get('chat')).main()

        elif update_type in ['updateNewMessage', 'updateChatLastMessage']:
            message = None
            if update_type == 'updateChatLastMessage' and update.get('last_message'):
                message = Message(update.get('last_message'))
            elif update_type == 'updateNewMessage':
                message = Message(update.get('message'))
            if message:
                send_data = message.main()
                share.aggregator_share_link(message.entities)

        for data in send_data:
            clinent.send(data)
            time.sleep(0.2)





