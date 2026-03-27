
'''
转换 yaml 格式
'''

import yaml
import json
import base64
import sys
import urllib.parse
import logging
from Log import loginfo

log = loginfo('ConvertYaml', logging.DEBUG, logging.ERROR)

class ConvertYaml:
    '''
    将 yaml 格式的订阅节点转换成符合 v2ray 的 json 格式
    '''
    def __init__(self, file_path):
        '''

        :param file_path:
        '''
        self.content = self.read_yaml_file(file_path)
        self.v2ray_node = []

    def main(self):
        '''
        转换所有节点
        :return:
        '''
        self.content = self.content.get('proxies', [])
        if not self.content:
            log.error('main -- this yaml file not have "proxies"')
            return []
        for node in self.content:
            protocol = node.get('type').lower()
            if not protocol:
                log.info('main -- this node not have "type"')
                continue
            result = None
            if protocol == 'vmess':
                result = self.convert_vmess(node)
            elif protocol == 'ss':
                result = self.convert_ss(node)
            elif protocol == 'vless':
                result = self.convert_vless(node)
            elif protocol == 'trojan':
                result = self.convert_trojan(node)
            else:
                log.info(f'main -- this node type is not support: {node}')


            if result and result in self.v2ray_node:
                log.info(f'main -- this node is duplicate: {result}')
            if result:
                self.v2ray_node.append(result)

        return self.v2ray_node
    
    @classmethod
    def convert_vmess(cls, node):
        '''
        转换 vmess
        :param node: 
        :return: 
        '''
        try:
            # 创建vmess链接所需的json对象
            vmess_node = {
                "v": "2",
                "ps": node.get('name', 'vmess node'),
                "add": node.get('server', ''),
                "port": str(node.get('port', '')),
                "id": node.get('uuid', ''),
                "aid": str(node.get('alterId', 0)),
                "net": node.get('network', 'tcp'),
                "type": node.get('type', 'none'),
                "host": node.get('ws-headers', {}).get('Host', '') or node.get('servername', ''),
                "path": node.get('ws-path', '') or node.get('path', ''),
                "tls": "tls" if node.get('tls', False) else "",
                "sni": node.get('servername', '') or node.get('sni', ''),
                "alpn": ','.join(node.get('alpn', [])) if isinstance(node.get('alpn', []), list) else node.get(
                    'alpn', '')
            }

            # 处理特殊情况
            if node.get('network') == 'ws':
                vmess_node['host'] = node.get('ws-headers', {}).get('Host', '') or node.get('ws-opts', {}).get(
                    'headers', {}).get('Host', '')
                vmess_node['path'] = node.get('ws-path', '') or node.get('ws-opts', {}).get('path', '')
            elif node.get('network') == 'h2':
                vmess_node['host'] = node.get('h2-opts', {}).get('host', [''])[0] if isinstance(
                    node.get('h2-opts', {}).get('host', []), list) else ''
                vmess_node['path'] = node.get('h2-opts', {}).get('path', '')
            elif node.get('network') == 'http':
                vmess_node['host'] = node.get('http-opts', {}).get('headers', {}).get('Host', [''])[0] if isinstance(
                    node.get('http-opts', {}).get('headers', {}).get('Host', []), list) else ''
                vmess_node['path'] = node.get('http-opts', {}).get('path', [''])[0] if isinstance(
                    node.get('http-opts', {}).get('path', []), list) else ''
            elif node.get('network') == 'grpc':
                vmess_node['path'] = node.get('grpc-opts', {}).get('grpc-service-name', '')

            # 编码为vmess链接
            vmess_json_str = json.dumps(vmess_node)
            vmess_b64 = base64.b64encode(vmess_json_str.encode('utf-8')).decode('utf-8')
            return f"vmess://{vmess_b64}"
        except Exception as e:
            log.error(f"convert_vmess -- '{node}' 失败: {e}")
            return None

    @classmethod
    def convert_ss(cls, node):
        """
        转换Shadowsocks节点为v2rayN格式
        """
        try:
            server = node.get('server', '')
            port = node.get('port', '')
            password = node.get('password', '')
            method = node.get('cipher', 'aes-128-gcm')
            name = node.get('name', 'ss node')

            # 创建ss链接
            user_info = f"{method}:{password}"
            user_info_b64 = base64.b64encode(user_info.encode('utf-8')).decode('utf-8')

            # 添加插件信息（如果有）
            plugin_str = ""
            if node.get('plugin'):
                plugin_opts = node.get('plugin-opts', {})
                if node['plugin'] == 'obfs':
                    plugin = "obfs-local"
                    plugin_opts_str = []
                    if plugin_opts.get('mode'):
                        plugin_opts_str.append(f"obfs={plugin_opts['mode']}")
                    if plugin_opts.get('host'):
                        plugin_opts_str.append(f"obfs-host={plugin_opts['host']}")
                    plugin_str = f";plugin={plugin};{';'.join(plugin_opts_str)}"
                elif node['plugin'] == 'v2ray-plugin':
                    plugin = "v2ray-plugin"
                    plugin_opts_str = []
                    if plugin_opts.get('mode'):
                        plugin_opts_str.append(f"mode={plugin_opts['mode']}")
                    if plugin_opts.get('host'):
                        plugin_opts_str.append(f"host={plugin_opts['host']}")
                    if plugin_opts.get('tls'):
                        plugin_opts_str.append("tls")
                    plugin_str = f";plugin={plugin};{';'.join(plugin_opts_str)}"

            ss_url = f"ss://{user_info_b64}@{server}:{port}{plugin_str}"

            # 添加节点名称
            ss_url += f"#{urllib.parse.quote(name)}"

            return ss_url
        except Exception as e:
            log.error(f"convert_ss -- '{node}' 失败: {e}")
            return None

    @classmethod
    def convert_trojan(cls, node):
        """
        转换trojan节点为v2rayN格式
        """
        try:
            server = node.get('server', '')
            port = node.get('port', '')
            password = node.get('password', '')
            name = node.get('name', 'trojan node')
            sni = node.get('sni', '') or node.get('servername', '')
            alpn = node.get('alpn', [])
            alpn_str = ""
            if alpn:
                if isinstance(alpn, list):
                    alpn_str = f"&alpn={','.join(alpn)}"
                else:
                    alpn_str = f"&alpn={alpn}"

            # 处理网络类型
            network = node.get('network', '')
            network_params = ""
            if network == 'ws':
                host = node.get('ws-opts', {}).get('headers', {}).get('Host', '') or node.get('ws-headers', {}).get(
                    'Host', '')
                path = node.get('ws-opts', {}).get('path', '') or node.get('ws-path', '')
                if host:
                    network_params += f"&host={urllib.parse.quote(host)}"
                if path:
                    network_params += f"&path={urllib.parse.quote(path)}"
                network_params = f"&type=ws{network_params}"
            elif network == 'grpc':
                service_name = node.get('grpc-opts', {}).get('grpc-service-name', '')
                if service_name:
                    network_params = f"&type=grpc&serviceName={urllib.parse.quote(service_name)}"

            # 构建trojan URL
            trojan_node = f"trojan://{password}@{server}:{port}?sni={sni}{alpn_str}{network_params}"
            trojan_node += f"#{urllib.parse.quote(name)}"

            return trojan_node
        except Exception as e:
            log.error(f"convert_trojans -- '{node}' 失败: {e}")
            return None

    @classmethod
    def convert_vless(cls, node):
        """
        转换vless节点为v2rayN格式
        """
        try:
            server = node.get('server', '')
            port = node.get('port', '')
            uuid = node.get('uuid', '')
            name = node.get('name', 'vless node')
            tls = "tls" if node.get('tls', False) else "none"
            sni = node.get('servername', '') or node.get('sni', '')

            # 处理流控制
            flow = node.get('flow', '')
            flow_param = f"&flow={flow}" if flow else ""

            # 处理网络类型
            network = node.get('network', 'tcp')
            network_params = ""

            if network == 'ws':
                host = node.get('ws-opts', {}).get('headers', {}).get('Host', '') or node.get('ws-headers', {}).get(
                    'Host', '')
                path = node.get('ws-opts', {}).get('path', '') or node.get('ws-path', '')
                if host:
                    network_params += f"&host={urllib.parse.quote(host)}"
                if path:
                    network_params += f"&path={urllib.parse.quote(path)}"
            elif network == 'grpc':
                service_name = node.get('grpc-opts', {}).get('grpc-service-name', '')
                if service_name:
                    network_params += f"&serviceName={urllib.parse.quote(service_name)}"
            elif network == 'tcp':
                if node.get('tcp-opts', {}).get('header', {}).get('type') == 'http':
                    host = node.get('tcp-opts', {}).get('header', {}).get('request', {}).get('headers', {}).get('Host',
                                                                                                                [''])
                    path = node.get('tcp-opts', {}).get('header', {}).get('request', {}).get('path', [''])
                    if isinstance(host, list) and host:
                        network_params += f"&host={urllib.parse.quote(host[0])}"
                    if isinstance(path, list) and path:
                        network_params += f"&path={urllib.parse.quote(path[0])}"

            # 处理ALPN
            alpn = node.get('alpn', [])
            alpn_str = ""
            if alpn:
                if isinstance(alpn, list):
                    alpn_str = f"&alpn={','.join(alpn)}"
                else:
                    alpn_str = f"&alpn={alpn}"

            # 构建vless URL
            vless_node = f"vless://{uuid}@{server}:{port}?encryption=none&security={tls}&type={network}{network_params}{flow_param}{alpn_str}"
            if sni:
                vless_node += f"&sni={sni}"
            vless_node += f"#{urllib.parse.quote(name)}"

            return vless_node
        except Exception as e:
            log.error(f"convert_vless -- '{node}' 失败: {e}")
            return None

    @classmethod
    def convert_hysteria2(cls, node):
        """
        转换hysteria2节点为v2rayN格式
        """
        try:
            server = node.get('server', '')
            port = node.get('port', '')
            password = node.get('password', '') or node.get('auth', '')
            name = node.get('name', 'hysteria2 node')
            sni = node.get('sni', '') or node.get('servername', '')

            # 处理obfs参数
            obfs = node.get('obfs', '')
            obfs_param = node.get('obfs-password', '') or node.get('obfs-param', '')
            obfs_str = ""
            if obfs:
                obfs_str = f"&obfs={obfs}"
                if obfs_param:
                    obfs_str += f"&obfs-password={urllib.parse.quote(obfs_param)}"

            # 处理ALPN
            alpn = node.get('alpn', '')
            alpn_str = f"&alpn={alpn}" if alpn else ""

            # 处理其他参数
            insecure = "&insecure=1" if node.get('skip-cert-verify', False) else ""
            pinSHA256 = f"&pinSHA256={node.get('fingerprint', '')}" if node.get('fingerprint', '') else ""

            # 构建hysteria2 URL
            hysteria2_node = f"hysteria2://{password}@{server}:{port}?sni={sni}{obfs_str}{alpn_str}{insecure}{pinSHA256}"
            hysteria2_node += f"#{urllib.parse.quote(name)}"

            return hysteria2_node
        except Exception as e:
            log.error(f"convert_hysteria2 -- '{node}' 失败: {e}")
            return None

    @classmethod
    def read_yaml_file(cls, file_path):
        '''
        读取文件
        :param file_path:
        :return:
        '''
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config
        except Exception as e:
            log.error(f'Read yaml file failed: {e}')
            sys.exit(1)


if __name__ == "__main__":

    Yaml_path = 'D:/PycharmProjects/SpecialNetwork/data/yaml.txt'
    convert = ConvertYaml(Yaml_path)
    v2ray_nodes = convert.main()
    if v2ray_nodes:
        with open('D:/PycharmProjects/SpecialNetwork/data/v2ray_nodes.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(v2ray_nodes))







