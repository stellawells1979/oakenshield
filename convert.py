
'''
解析订阅内容并格式化成详细的订阅节点信息
'''

import base64
import json
import logging
from config import config
from urllib.parse import urlparse, parse_qs, unquote
import yaml
from Log import loginfo
from convertyaml import ConvertYaml



# 配置日志记录
log = loginfo('convert', logging.DEBUG, logging.ERROR)

class Convert:
    '''
    s
    '''

    def __init__(self, path):

        self.path = path
        self.content = self.read_file(path)
        self.datas = []

    def main(self):
        '''

        :return:
        '''
        log.info('启动节点解析程序')
        result = self.check_file_content()
        if result == 'yaml':
            self.datas = ConvertYaml(self.path).main()
        elif result == 'base64':
            for node in self.content.splitlines():
                if not node.strip():
                    continue
                for start in ["vmess://", "vless://", "trojan://", "ss://", "anytls://", "hysteria2://", 'ssr://']:
                    if node.startswith(start) and node in self.datas:
                        log.info('main: This node is duplicate')
                    elif node.startswith(start):
                        self.datas.append(node)
        else:
            log.info('Unkown File')

        return self.datas



    def check_file_content(self):
        '''
        检查文件内容

        :return:
        '''
        if not self.content:
            log.error('Check file content -- This file is empty')
            return None

        # 尝试进行 base64 解码
        try:
            self.content = base64.b64decode(self.content).decode()
            return 'base64'
        except Exception as e:
            log.info(f'Check file content BASE64: {e}')

        # 尝试 json 序列化
        try:
            self.content = json.loads(self.content)
            if isinstance(self.content, (dict, list)):
                return 'json'
            log.info(f"Check file content JSON：this is not a JSON object")
        except Exception as e:
            log.info(f"Check file content JSON： - {e}")

        try:
            for start in ["vmess://", "vless://", "trojan://", "ss://", "anytls://", "hysteria2://", 'ssr://']:
                if self.content.strip().startswith(start):
                    return 'base64'
        except Exception as e:
            log.error(f"Check file content Lines： - {e}")



        # 尝试 yaml 格式的文件解析
        try:
            self.content = yaml.safe_load(self.content)
            return 'yaml'
        except Exception as e:
            log.info(f'Check file content YAML: {e}')

        log.error('Check file content -- All type is not')

        return None

    @classmethod
    def read_file(cls, path):
        """
        读取 Base64 文件内容
        """
        result = None
        try:
            with open(path, "r", encoding="utf-8") as file:
                result = file.read().strip()
        except Exception as e:
            log.error(f"【Read File】: {e}")
        return result



class SubscriptionParser:
    '''
    u
    '''
    def __init__(self, path):
        """
        初始化类
        :param path: 包含 Base64 编码订阅节点的文件路径
        """
        self.path = path
        self.base64_datas = None     # bsae64 数据流
        self.json_datas = None
        self.yaml_datas = None
        self.intact_subscribe = []  # 完整的订阅节点
        self.base64_subscribe = []  # bsae64 格式的订阅节点

        self.check_subscribe_file()

    def main(self):
        '''
        :return:
        '''
        if self.base64_datas:
            self.subscribe_base64(self.base64_datas.splitlines())

        elif self.base64_subscribe:
            self.subscribe_base64(self.base64_subscribe)

        elif self.yaml_datas:
            input('解析 yaml 格式的订阅节点')
            nodes = self.yaml_datas.get("proxies", [])

            if not nodes:
                log.erroe("YAML 文件中没有找到节点信息（'proxies' 部分为空）")
            else:
                for node in nodes:
                    if not isinstance(node, dict):
                        log.info('yaml 节点格式无效')
                        continue
                    if not node.get("type"):
                        log.info('yaml 无法识别的节点信息')
                        continue
                    self.intact_subscribe.append(f"{node.get('type')}: {json.dumps(node, ensure_ascii=False)}")

        if self.intact_subscribe:
            with open(config.v2rayNodes, "a", encoding="utf-8") as file:
                file.write("\n".join(self.intact_subscribe))

        return self.intact_subscribe

    def subscribe_base64(self, nodes):
        """
        解析所有节点列表
        :param nodes: 解码后的节点列表
        :return: 解析结果列表
        """

        for node in nodes:
            result = None
            node = node.strip()
            sub_type = node.split("://")[0]
            if not node:
                continue
            if node.startswith("vmess://"):
                result = self.parse_vmess_node(node)
            elif node.startswith("ss://"):
                result = self.parse_shadowsocks_node(node)
            elif node.startswith("ssr://"):
                result = self.parse_shadowsocks_ssr(node)
            elif node.startswith("trojan://"):
                result = self.parse_trojan_node(node)
            elif node.startswith("vless://"):
                result = self.parse_vless_node(node)
            elif node.startswith("anytls://"):
                result = self.parse_anytls_node(node)
            elif node.startswith("hysteria2://"):
                result = self.parse_hysteria2_node(node)
            else:
                log.error(f"【Unknown Subscribe】: {node}")
            if result:
                self.intact_subscribe.append(f'{sub_type}: {json.dumps(result, ensure_ascii=False)}')

    @classmethod
    def parse_vmess_node(cls, node):
        """
        解析 Vmess 节点
        """
        result = None
        try:
            base64_data = node[8:]  # 去掉 "vmess://" 前缀
            decoded_data = base64.b64decode(base64_data).decode("utf-8")
            result = json.loads(decoded_data)
        except Exception as e:
            log.error(f"【Analysis Vmess Error】: {e}")
        return result

    @classmethod
    def parse_shadowsocks_node(cls, node):
        """
        解析 Shadowsocks 节点
        """
        try:
            node = node[5:]  # 去掉 "ss://" 前缀
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
                    "server": address,  # 服务器地址 (add)
                    "port": port,  # 服务器端口 (port)
                    "method": method,  # 加密方式 (method)
                    "password": password,  # 密码 (password)
                    "remarks": name or "无备注"  # 节点备注 (ps)
                }
                return result
            else:
                input('此订阅节点没有包含 “#” 号')
        except Exception as e:
            log.error(f"【Parse shadowsocks Error】: {e}")

        return None

    @classmethod
    def parse_shadowsocks_ssr(cls, node):
        '''

        :param node:
        :return:
        '''
        try:
            print(node)
            data = cls.check_base64(node[6:])
            parts = data.split("/?")
            main_info = parts[0].split(":")
            if len(main_info) < 6:
                log.info(f"[ERROR] 解析 ssr 节点失败: SSR 节点信息格式不正确")
                return None
            service, port, protocol, method, obfs, password_base64 = main_info
            password = cls.check_base64(password_base64)  # 解码密码
            result = {
                'server': service,
                'port': int(port),
                'protocol': protocol,
                'method': method,
                'obfs': obfs,
                'password': password,
            }
            return result
        except Exception as e:
            log.error(f"【Parse shadowsocksR Error】: {e}")
        return None

    @classmethod
    def parse_trojan_node(cls, node):
        """
        解析 Trojan 节点
        """

        try:
            # 确保链接是以 "trojan://" 开头
            if not node.startswith("trojan://"):
                raise ValueError("链接不是有效的 Trojan 节点链接")

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
                "server": server,  # 服务器地址
                "port": port,  # 服务器端口
                "tls": "tls",  # 固定为 "tls"
                "sni": query_params.get("sni", [""])[0],  # SNI 伪装域名
                "allowInsecure": allow_insecure,  # 是否允许不安全连接
                "network": query_params.get("type", ["tcp"])[0],  # 网络类型（通常为 "tcp"）
                "headerType": query_params.get("headerType", ["none"])[0],  # HTTP 伪装头部类型
                "remarks": unquote(parsed_url.fragment),  # 提取备注信息（即 # 号后的内容，通常是 URL 编码的备注）
                'path': query_params.get('path', [''])[0] or ''
            }
            return result
        except Exception as e:
            log.error(f"【Parse trojan Error】: {e}")

        return None

    @classmethod
    def parse_vless_node(cls, node):
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
                "type": "vless",  # 固定值
                "uuid": uuid,  # 用户唯一标识
                "server": server,  # 服务器地址
                "port": port,  # 端口号
                "encryption": query_params.get("encryption", ["none"])[0],  # 加密方式 (通常为 "none")
                "flow": query_params.get("flow", [""])[0],  # 流控模式
                "security": query_params.get("security", [""])[0],  # TLS 安全传输
                "sni": query_params.get("sni", [""])[0],  # 伪装域名 (SNI)
                "fingerprint": query_params.get("fp", [""])[0],  # 客户端指纹伪装
                "public_key": query_params.get("pbk", [""])[0],  # 公钥
                "sid": query_params.get("sid", [""])[0],  # 会话 ID
                "allowInsecure": allow_insecure,  # 是否允许不安全连接
                "network": network,  # 网络类型
                "headerType": query_params.get("headerType", ["none"])[0],  # TCP 或 HTTP 头部伪装类型
                "name": unquote(parsed_url.fragment),  # 节点备注信息
                'path': query_params.get('path', [''])[0] or ''
            }
            return result


        except Exception as e:
            log.error(f"【Parse vless Error】: {e}")

        return None

    @classmethod
    def parse_anytls_node(cls, node):
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
                "type": "anytls",  # 节点类型
                "add": parsed.hostname,  # 服务器地址
                "port": int(parsed.port),  # 服务器端口号
                "id": parsed.username,  # 用户唯一标识（UUID，用于身份认证）
                "security": params.get("security", ["none"])[0],  # 加密方式
                "network": params.get("type", ["tcp"])[0],  # 传输方式（tcp、ws等）
                "sni": params.get("sni", [""])[0],  # 伪装域名（Server Name Indication）
                "allowInsecure": params.get("allowInsecure", ["0"])[0] == "1",  # 是否允许跳过证书校验
                "fp": params.get("fp", [""])[0],  # 使用的伪装指纹（如 chrome、firefox 等）
                "udp": params.get("udp", ["0"])[0] == "1",  # 是否支持 UDP 转发
                "ps": unquote(parsed.fragment) or "无备注",  # 节点备注信息，解码 URL 编码的内容
            }
            return result
        except Exception as e:
            log.error(f"【Parse anytls Error】: {e}")
        return None

    @classmethod
    def parse_hysteria2_node(cls, node):
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
            log.error(f"【Analysis hysteria2 Error】: {e}")

        return None

    def check_subscribe_file(self):
        '''

        :return:
        '''
        # 读取文件
        content = self.read_file(self.path)

        #
        result = self.check_base64(content)
        if result:
            self.base64_datas = result
            return 'base64 datastream'

        # 优先判断是否为 JSON
        try:
            self.json_datas = json.loads(content)
            return 'json datastream'
        except json.JSONDecodeError:
            pass  # 如果不是 JSON 格式，继续检查 YAML

        try:
            # 判断每行是否符合节点协议，如 vmess:// 或 vless://
            sub_head = ["vmess://", "vless://", "trojan://", "ss://", "anytls://", "hysteria2://"]
            lines = content.strip().splitlines()
            for line in lines:
                line = line.strip()
                for head in sub_head:
                    if line.startswith(head):
                        try:
                            node = line[len(head):]
                            if json.loads(node):
                                self.intact_subscribe.append(line)
                        except Exception as e:
                            self.base64_subscribe.append(line)
        except Exception:
            pass

        try:
            self.yaml_datas = yaml.safe_load(content)
            return 'yaml datastream'
        except yaml.YAMLError:
            log.info('未检测到任何有效内容')
            return None  # 解析失败（既不是 JSON，也不是 YAML）

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
        except Exception:
            return False

    @classmethod
    def check_yaml(cls, data):
        '''

        :return:
        '''
        try:
            return yaml.safe_load(data)
        except yaml.YAMLError:
            return None  # 解析失败，可能不是有效的 YAML 文件

    @classmethod
    def read_file(cls, path):
        """
        读取 Base64 文件内容
        """
        result = None
        try:
            with open(path, "r", encoding="utf-8") as file:
                result = file.read().strip()
        except Exception as e:
            log.error(f"【Read File】: {e}")
        return result


if __name__ == "__main__":

    # 实例化订阅解析器并进行解析
    file_path = config.subscribe_datas
    convert = Convert(file_path)
    datas = convert.main()

    print(datas)

























