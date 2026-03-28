'''
test
'''

import time
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from config import config

import base64
from urllib.parse import urlparse, parse_qs, unquote
import logging
from Log import loginfo
import subprocess
import requests
import concurrent.futures
import shutil
import psutil
import socket
import threading
import json
import os

from v2raycode import V2rayCocde




log_Parse = loginfo('TestNode -- ParseNode', logging.DEBUG, logging.ERROR)
log_Test = loginfo('TestNode -- TestNode', logging.DEBUG, logging.ERROR)





class ThreadSafePortManager:
    '''
    f
    '''
    def __init__(self, min_port=1024, max_port=65535):
        """
        初始化端口管理模块
        :param min_port: 最小可用端口
        :param max_port: 最大可用端口
        """
        self.min_port = min_port
        self.max_port = max_port

        # 用于存储已占用的端口 (内存数据结构)
        self.used_ports = set()

        # 线程锁，保证线程安全
        self.lock = threading.Lock()

    @classmethod
    def _is_port_free(cls, port):
        """
        检查指定端口是否空闲 (检查操作无锁，仅用于检查系统层面状态)
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return True
            except OSError:
                return False

    def allocate_port(self):
        """
        自动分配一个可用端口 (线程安全)
        """
        with self.lock:
            for port in range(self.min_port, self.max_port + 1):
                if port not in self.used_ports and self._is_port_free(port):
                    self.used_ports.add(port)
                    return port
            return None  # 如果没有可用端口，返回 None

    def allocate_specific_port(self, port):
        """
        尝试分配指定端口 (线程安全)
        :param port: 需要分配的端口号
        :return: 如果成功返回 True，失败返回 False
        """
        if port < self.min_port or port > self.max_port:
            raise ValueError(f"Port {port} is out of the valid range ({self.min_port}-{self.max_port})")

        with self.lock:
            if port not in self.used_ports and self._is_port_free(port):
                self.used_ports.add(port)
                return True
            return False

    def release_port(self, port):
        """
        释放指定端口 (线程安全)
        """
        with self.lock:
            self.used_ports.discard(port)

    def get_used_ports(self):
        """
        获取当前已分配的端口列表 (线程安全)
        :return: 按序返回已分配端口
        """
        with self.lock:
            return sorted(self.used_ports)

    def is_port_in_use(self, port):
        """
        检查指定端口是否已经被分配 (线程安全)
        """
        with self.lock:
            return port in self.used_ports


def is_port_in_use(port):
    """
    检查端口是否被占用。
    :param port: 需要检查的端口号
    :return: 如果占用返回 True，否则返回 False
    """
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port:
            return True
    return False


port_pool = ThreadSafePortManager(*config.test_port_range)


class ParseNode:
    '''
    解析节点信息
    '''

    def __init__(self, node=None):
        '''

        :param node:
        '''
        self.node = node
        self.datas = []

    @classmethod
    def parse_node(cls, node):
        '''
        :param node:
        :return:
        '''
        if not node:
            log_Parse.error('Please enter a valid node link')
            return None
        result = None
        protocol, params = node.split('://', maxsplit=1)
        if protocol == 'ss':
            result = cls.parse_shadowsocks(node)
        elif protocol == 'vmess':
            result = cls.parse_vmess(node)
        elif protocol == 'trojan':
            result = cls.parse_trojan(node)
        elif protocol == 'vless':
            result = cls.parse_vless(node)

        else:
            log_Parse.error(f'parse: Unkown protocol: {protocol}')

        if result:
            return protocol, result

        return None

    @classmethod
    def parse_vmess(cls, node):
        """
        解析 Vmess 节点
        """
        result = None

        try:
            node = node.split('vmess://')[1].strip()
            decoded_data = base64.urlsafe_b64decode(node).decode("utf-8")
            result = json.loads(decoded_data)
        except Exception as e:
            log_Parse.error(f"【Analysis Vmess Error】: {e}")
        return result

    @classmethod
    def parse_shadowsocks(cls, node):
        """
        解析 Shadowsocks 节点
        """
        try:
            node = node.split('ss://')[1].strip()
            if "#" in node:
                data, name = node.split("#", maxsplit=1)
                name = unquote(name)  # 备注解码

                if '@' not in data:
                    data = cls.check_base64(data)
                method_password, server_info = data.rsplit("@", maxsplit=1)

                # 解析方法和密码
                if ":" not in method_password:
                    method_password = cls.check_base64(method_password)
                method, password = method_password.split(":", maxsplit=1)

                # 解析地址和端口
                address, port = server_info.split(":", maxsplit=1)

                result = {
                    "add": address,  # 服务器地址 (add)
                    "port": port,  # 服务器端口 (port)
                    "method": method,  # 加密方式 (method)
                    "password": password,  # 密码 (password)
                    'ps': name
                }
                return result
            else:
                log_Parse.eror('此订阅节点没有包含 “#” 号')
        except Exception as e:
            log_Parse.error(f"Parse shadowsocks: {e}")

        return None

    @classmethod
    def parse_shadowsocksR(cls, node):
        '''

        :param node:
        :return:
        '''
        try:
            data = cls.check_base64(node[6:])
            parts = data.split("/?")
            main_info = parts[0].split(":")
            if len(main_info) < 6:
                log_Parse.info(f"[ERROR] 解析 ssr 节点失败: SSR 节点信息格式不正确")
                return None
            service, port, protocol, method, obfs, password_base64 = main_info
            password = cls.check_base64(password_base64)  # 解码密码
            result = {
                'add': service,
                'port': int(port),
                'method': method,
                'obfs': obfs,
                'password': password,
            }
            return result
        except Exception as e:
            log_Parse.error(f"【Parse shadowsocksR Error】: {e}")
        return None

    @classmethod
    def parse_trojan(cls, node):
        """
        解析 Trojan 节点
        """
        try:
            # 解析 URL
            parsed_url = urlparse(node)

            # 从用户认证部分提取密码
            password = parsed_url.username

            # 提取服务器地址和端口号
            server = parsed_url.hostname
            port = parsed_url.port

            # 解析查询参数 (如 sni, allowInsecure 等)

            query_params = parse_qs(parsed_url.query)
            allow_insecure = query_params.get("allowInsecure", ["0"])[0] == "1"  # 转换为布尔值

            # 构造结果字典
            result = {
                "password": password,  # 密码
                "add": server,  # 服务器地址
                "port": port,  # 服务器端口
                "tls": query_params.get("security", ['tls'])[0],  # 固定为 "tls"
                "sni": query_params.get("sni", [""])[0],  # SNI 伪装域名
                "allowInsecure": allow_insecure,  # 是否允许不安全连接
                "net": query_params.get("type", ["tcp"])[0],  # 网络类型（通常为 "tcp"）
                "headerType": query_params.get("headerType", ["none"])[0],  # HTTP 伪装头部类型
                'path': query_params.get('path', [''])[0] or ''
            }
            return result
        except Exception as e:
            log_Parse.error(f"parse_trojan: {e}")

        return None

    @classmethod
    def parse_vless(cls, node):
        """
        解析 VLESS 节点链接并输出符合 V2Ray 标准字段的 JSON
        :param node: VLESS 节点链接
        :return: 解析后的信息字典
        """
        if not node.startswith("vless://"):
            return "[ERROR] 无效的 VLESS 节点链接"
        try:
            # 解析 URL
            parsed_url = urlparse(node)

            # 从用户认证部分提取 UUID (用户标识)
            uuid = parsed_url.username

            # 提取服务器地址和端口号
            server = parsed_url.hostname
            port = parsed_url.port

            # 解析查询参数

            query_params = parse_qs(parsed_url.query)

            network = query_params.get("type", ["tcp"])[0]
            allow_insecure = query_params.get("allowInsecure", ["0"])[0] == "1"  # 转换为布尔值

            # 构造结果字典
            result = {
                "id": uuid,  # 用户唯一标识
                "add": server,  # 服务器地址
                "port": port,  # 端口号
                "encryption": query_params.get("encryption", ["none"])[0],  # 加密方式 (通常为 "none")
                "flow": query_params.get("flow", [""])[0],  # 流控模式
                "tls": query_params.get("security", [""])[0],  # TLS 安全传输
                "sni": query_params.get("sni", [""])[0],  # 伪装域名 (SNI)
                "fingerprint": query_params.get("fp", [""])[0],  # 客户端指纹伪装
                "public_key": query_params.get("pbk", [""])[0],  # 公钥
                "sid": query_params.get("sid", [""])[0],  # 会话 ID
                "allowInsecure": allow_insecure,  # 是否允许不安全连接
                "net": network,  # 网络类型
                "headerType": query_params.get("headerType", ["none"])[0],  # TCP 或 HTTP 头部伪装类型
                'path': query_params.get('path', [''])[0] or ''
            }
            return result


        except Exception as e:
            log_Parse.error(f"【Parse vless Error】: {e}")

        return None

    @classmethod
    def parse_anytls(cls, node):
        '''

        :param node:
        :return:
        '''
        try:

            # 使用 urlparse 解析 URL
            parsed = urlparse(node)

            # 提取查询参数部分并转化为字典
            params = parse_qs(parsed.query)

            result = {
                "add": parsed.hostname,  # 服务器地址
                "port": int(parsed.port),  # 服务器端口号
                "id": parsed.username,  # 用户唯一标识（UUID，用于身份认证）
                "security": params.get("security", ["none"])[0],  # 加密方式
                "net": params.get("type", ["tcp"])[0],  # 传输方式（tcp、ws等）
                "sni": params.get("sni", [""])[0],  # 伪装域名（Server Name Indication）
                "allowInsecure": params.get("allowInsecure", ["0"])[0] == "1",  # 是否允许跳过证书校验
                "fp": params.get("fp", [""])[0],  # 使用的伪装指纹（如 chrome、firefox 等）
                "udp": params.get("udp", ["0"])[0] == "1",  # 是否支持 UDP 转发
            }
            return result
        except Exception as e:
            log_Parse.error(f"parse_anytls: {e}")
        return None

    @classmethod
    def parse_hysteria2(cls, node):
        """
        解析 Hysteria2 节点为标准格式
        """
        try:
            # 解析节点 URL
            parsed = urlparse(node)
            query_params = parse_qs(parsed.query)

            # 提取字段
            server = parsed.hostname
            port = int(parsed.port)
            uuid = parsed.username
            sni = query_params.get("sni", [""])[0]
            remark = unquote(parsed.fragment)

            # 构造 V2Ray 标准节点
            standard_node = {
                "add": server,  # 服务器地址
                "port": port,  # 端口号
                "id": uuid,  # 用户 ID
                "net": "udp",  # 传输协议
                "sni": sni,  # SNI 域名
                "tls": True,  # 强制启用 TLS
                "ps": remark  # 备注
            }

            return standard_node
        except Exception as e:
            log_Parse.error(f"parse_hysteria2: {e}")

        return None

    @classmethod
    def check_base64(cls, data):
        '''

        :param data:
        :return:
        '''
        # Base64 数据必须是 4 的倍数长度
        try:
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            return base64.b64decode(data).decode("utf-8")
        except Exception as e:
            log_Parse.error(f"check_base64: {e}")
            return False

class TestNode(ParseNode):
    '''
    测试节点类
    '''
    def __init__(self, v2ray_path):

        super().__init__()
        self.session = self.create_session_with_retry()
        self.server = None
        self.port = None
        self.duplicate = []
        self.v2ray_exe = v2ray_path
        self.tese_url = 'https://www.google.com/'

    def parallel_execution(self, data, thread):
        '''
        多线程测试节点的连通性
        :param data:
        :param thread:
        :return: 包含所有测试结果的集合
        '''
        with concurrent.futures.ThreadPoolExecutor(thread) as executor:
            result = list(executor.map(self.test_function, enumerate(data)))

        return result

    def test_function(self, item):
        '''
        多线程时每个测试实例的处理逻辑
        :param item:
        :return:
        '''
        index, spaper = item
        subscribe = self.parse_node(spaper)
        if not subscribe or subscribe[0] not in ['ss', 'trojan', 'vmess', 'vless']:
            return index, None

        protocol, node = subscribe
        result = self.v2ray_test(protocol, node)

        if not result:
            return index, None
        return index, result

    def v2ray_test(self, protocol, node):
        '''
        创建配置文件并启动节点测试
        :param protocol:
        :param node:
        :return: 测试结果或 None
        '''
        self.server = node.get('add')
        self.port = node.get('port')

        if f'{self.server}:{self.port}' in self.duplicate:
            log_Test.info(f'create_config : this node is duplicate: {self.server}:{self.port}')
            return None

        self.duplicate.append(f'{self.server}:{self.port}')

        # 开始构建 v2ray 配置参数
        result = None
        if protocol == 'ss':
            result = self.create_ss_config(node)
        elif protocol == 'vless':
            result = self.create_vless_config(node)
        elif protocol == 'trojan':
            result = self.create_trojan_config(node)
        elif protocol == 'vmess':
            result = self.create_vmess_config(node)

        if not result:
            return None
        # 动态替换端口
        local_http_port = port_pool.allocate_port()
        local_socks_port = port_pool.allocate_port()

        inbounds = [
            {
                'tag': 'socks',
                'port': local_socks_port,
                'listen': '127.0.0.1',
                'protocol': 'socks',
                'sniffing': {
                    'enabled': True,
                    'destOverride': ['http', 'tls'],
                    'routeOnly': False
                },
                'settings': {
                    'auth': 'noauth',
                    'udp': True,
                    'allowTransparent': False
                }
            },
            {
                'tag': 'http',
                'port': local_http_port,
                'listen': '127.0.0.1',
                'protocol': 'http',
                'sniffing': {
                    'enabled': True,
                    'destOverride': ['http', 'tls'],
                    'routeOnly': False
                },
                'settings': {
                    'auth': 'noauth',
                    'udp': True,
                    'allowTransparent': False
                }
            }
        ]
        config.base_config['inbounds'] = inbounds
        config.base_config['outbounds'] = result


        # 将配置数据写入本地文件
        test_config = os.path.join(config.test_configs_path, f'{local_socks_port}--{local_http_port}.json')
        self.write_config_file(test_config, config.base_config)

        # 启动 V2Ray 并加载配置文件
        result = None
        process = subprocess.Popen(
            [self.v2ray_exe, 'run', f"-config={test_config}"],
            stdout=subprocess.PIPE,  # 禁止标准输出
            stderr=subprocess.PIPE,   # 禁止错误输出
            text=True  # 设置文本模式（Python 3.6+），避免手动解码
        )

        try:
            start_time = time.time()
            proxies = {
                "http": f"http://127.0.0.1:{local_http_port}",
                "https": f"socks5h://127.0.0.1:{local_socks_port}"
            }

            self.session.proxies.update(proxies)

            response = self.session.get(self.tese_url, timeout=6)
            log_Test.info(f"[成功] URL: {self.tese_url}  | 状态码: {response.status_code}")
            result = time.time() - start_time
        except requests.exceptions.Timeout:
            print('连接超时')
        except requests.exceptions.RequestException:
            pass
        finally:
            process.terminate()  # 停止 V2Ray

        stdout, stderr = process.communicate()
        if stderr.startswith('Failed to start'):
            if 'failed to listen TCP' in stderr:
                log_Test.error(f'Failed to listen TCP on port {local_http_port}')
            result = 'Failed to start'

        port_pool.release_port(local_socks_port)
        port_pool.release_port(local_http_port)

        return result

    def create_vmess_config(self, node):
        '''
        创建 vmes 配置文件
        :param node:
        :return:
        '''

        network = node.get('net')

        # 提取流量层传输协议，如果采用了 tls 协议来传输整个流量，你应该正确设置 streamSettings.tlsSettings 字段
        tls = node.get('tls') if node.get('tls') else 'none'

        # 创建流量层传输字段
        streamsettings = {
            'network': network,
            **({'security': tls} if tls else {}),
            **({'tlsSettings': {'serverName': node.get('sni') or self.server}} if tls == 'tls' else {})
        }

        # 创建通信协议配置，根据 network 的值，可以是以下几种字段，tcpSettings, wsSettings, grpcSettings, h2Settings 等

        if network == 'ws':
            streamsettings.update({
                'wsSettings': {
                    'path': node.get('path') or '/',
                    'headers': {'Host': node.get('sni') or self.server}
                }
            })

        elif network == 'grpc':
            streamsettings.update({
                'grpcSettings': {
                    'serviceName': node.get('sni'),
                }
            })

        # 创建出站配置
        return [
            {
                'tag': 'proxy',
                'protocol': "vmess",      # 出站协议类型
                'settings': {
                    'vnext': [
                        {
                            'address': self.server,  # 代理服务器地址（IP 或域名）
                            'port': int(self.port),       # 代理服务器端口（通常是 443 或 80）
                            'users': [
                                {
                                    'id': node.get('id'), # 用户 UUID
                                    'alterId': int(node.get('aid')),         # 用户的 alterId，应与服务端保持一致
                                    'security': node.get('scy')    # 加密方式：推荐使用 auto，可选 aes-128-gcm、chacha20-poly1305 等
                                }
                            ]
                        }
                    ]
                },
                'streamSettings': streamsettings,
            }
        ]

    def create_vless_config(self, node):
        '''
        创建 vless 配置文件
        :return:
        :param node:
        :return:
        '''

        network = node.get('net')

        streamsettings = None
        if network == 'ws':
            streamsettings = {
                'network': network,
                'security': node.get('tls'),
                'tlsSettings':{
                    'allowInsecure': node.get('allowInsecure'),
                    'serverName': node.get('sni'),
                    **({'fingerprint': node.get('fingerprint')} if node.get('fingerprint') else {})
                },
                'wsSettings': {
                    'path': node.get('path'),
                    'headers': {
                        'Host': node.get('sni'),
                    }
                }
            }
        elif network == 'grpc':
            streamsettings = {
                'network': network,
                'security': node.get('tls'),
                'tlsSettings': {
                    'allowInsecure': node.get('allowInsecure'),
                    'serverName': node.get('sni'),
                },
                'grpcSettings': {
                    'path': node.get('path'),
                    'headers': {
                        'Host': node.get('sni'),
                    }
                }
            }
        elif network == 'tcp':
            streamsettings = {
                'network': network,
                'security': node.get('tls'),
                'tlsSettings':{
                    'allowInsecure': node.get('allowInsecure'),
                    'serverName': node.get('sni'),
                    **({'fingerprint': node.get('fingerprint')} if node.get('fingerprint') else {}),
                },

            }

        # 创建出站配置参数
        if streamsettings:
            return [{
                "tag": "proxy",
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": self.server,
                            "port": int(self.port),
                            "users": [{
                                'id': node.get('id'),
                                'alterId': 0,
                                'security': 'auto',
                                'encryption': node.get('encryption'),
                                'flow': node.get('flow'),
                            }]
                        }
                    ]
                },
                'streamSettings': streamsettings,
            }]
        return None

    def create_ss_config(self, node):
        '''

        :param self:
        :param node:
        :return:
        '''
        try:
            return [{
                "tag": "proxy",
                "protocol": "shadowsocks",
                "settings": {
                    "servers": [{
                        "address": self.server,
                        "port": int(self.port),
                        "method": node.get('method'),
                        "password": node.get('password'),
                    }]
                },
                'streamSettings': {
                    'network': 'tcp'
                }
            }]
        except Exception as e:
            log_Test.error(f"create_ss_config: {e}")
            return None

    def create_trojan_config(self, node):
        '''

        :param self:
        :param node:
        :return:
        '''
        network = node.get('net')
        streamsettings = None
        if network == 'tcp':
            streamsettings = {
                'network': network,
                'security': node.get('tls'),
                'tlsSettings':{
                    'allowInsecure': node.get('allowInsecure'),
                    **({'serverName': node.get('sni')} if node.get('sni') else {})
                }

            }
        elif network == 'ws':
            streamsettings = {
                'network': network,
                'security': node.get('tls'),
                'tlsSettings': {
                    'allowInsecure': node.get('allowInsecure'),
                    'serverName': node.get('sni'),
                },
                'wsSettings': {
                    'path': node.get('path'),
                    'headers': {
                        'Host': node.get('sni'),
                    }
                }
            }

        # 创建出站配置参数
        return [{
            "tag": "proxy",
            "protocol": "trojan",
            "settings": {
                "servers": [{
                    'address': self.server,
                    'port': int(self.port),
                    'method': node.get('method') if node.get('method') else 'chacha20',
                    'password': node.get('password')
                }]
            },
            'streamSettings': streamsettings
        }]

    def create_anytls_config(self, sub):
        '''
        :param self:
        :param sub:
        :return:
        '''

    def create_ssr_config(self, sub):
        '''

        :param self:
        :param sub:
        :return:
        '''

    @classmethod
    def write_config_file(cls, config_file, config_data):
        '''
        写入配置文件
        :return:
        '''
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            log_Test.error(f"Error writing config file: {e}")

    @classmethod
    def clear_folder(cls, folder_path):
        '''
        清空文件夹
        :param folder_path:
        :return:
        '''
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' does not exist.")
            return

        # 遍历文件夹中所有的项目
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            try:
                # 删除文件
                if os.path.isfile(item_path):
                    os.remove(item_path)
                # 删除文件夹及其内容
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

        print(f"Folder '{folder_path}' is now empty.")

    @classmethod
    def create_session_with_retry(cls, max_retries=3, backoff_factor=0.5):
        """
        创建带有重试机制的 Session。
        """
        session = requests.Session()

        # 设置重试策略
        retry_strategy = Retry(
            total=max_retries,  # 最大重试次数
            backoff_factor=backoff_factor,  # 重试间隔因子（指数退避机制）
            status_forcelist=[500, 502, 503, 504],  # 针对这些状态码进行重试
            allowed_methods=["GET", "POST"]  # 支持重试的请求方法
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session



if __name__ == "__main__":


    v2ray_exe = V2rayCocde().main()
    test = TestNode(v2ray_exe)

    with open(config.v2rayNodes, 'r', encoding='utf-8') as file:
        content = file.read().splitlines()

    test_results = test.parallel_execution(content, 5)

    # 处理测试结果

    for row, tested in reversed(test_results):
        if tested is None:
            del content[row]

    # 保存成功的节点
    with open(config.aggregatorNodes, 'a', encoding='utf-8') as file:
        file.write('\n'.join(content))

    print('Connect succeed:', len(content))

    test.clear_folder(config.test_configs_path)










