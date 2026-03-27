'''
配置文件，对程序运行所需和参数进行定义
'''

import os


class Config:
    '''
    t
    '''
    def __init__(self, base_path):


        self.base_path = base_path

        # 一个储存临时文件的路径
        self.temp_path = os.path.join(base_path, 'temp')

        # 节点池文件 ***
        self.aggregatorNodes = os.path.join(base_path, 'data', 'aggregatorNodes.txt')

        # 将下载的订阅内容临时储存到此文件
        self.subscribe_content = os.path.join(base_path, 'data', 'subscribe_content.txt')

        # 从网络收集到的订阅内容解码成完整的订阅节点后储存到此文件中
        self.v2rayNodes = os.path.join(base_path, 'data', 'v2rayNodes.txt')

        # 网络收集的订阅url，经处理后会添加到订阅连接汇总文件
        self.glean_subscribe = os.path.join(base_path, 'data', 'sub_list.json')

        # 订阅 url 汇总文件，从这些链接下载订阅内容
        self.subscribe_urls = os.path.join(base_path, 'data', 'subscribeurls.json')

        # 日志文件路径
        self.log_path = os.path.join(base_path, 'logs', 'error.log')

        # v2ray.exe 所在的文件夹
        self.v2ray_path = os.path.join(base_path, 'v2ray')

        # 测试用的配置文件路径，测试完成后会清空此文件夹
        self.test_configs_path = os.path.join(base_path, 'v2ray', 'TestConfigs')




        # v2ray 版本信息 url
        self.v2ray_versions_url = 'https://api.github.com/repos/v2fly/v2ray-core/releases'

        self.proxy = {
            'http': 'http://127.0.0.1:10809',
            'https': 'socks5://127.0.0.1:10808'
        }


        self.base_config = {
            'log': {
                'access': '',
                'error': '',
                'loglevel': 'error'
            },
            'inbounds': [
                {
                    'tag': 'socks',
                    'port': 10908,
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
                    'port': 10909,
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
            ],
            'outbounds': [
                {
                    'tag': 'proxy',
                    'protocol': 'vmess',
                    'settings': {
                        'vnext': [
                            {
                                'address': '2001:bc8:32d7:302::10',
                                'port': 44579,
                                'users': [
                                    {'id': '8e34e170-13ae-4892-9d20-05962acc9f84', 'alterId': 0, 'email': 't@t.tt', 'security': 'auto'}
                                ]
                            }
                        ]
                    },
                    'streamSettings': {
                        'network': 'ws',
                        'wsSettings': {
                            'path': '/?ed=2048',
                            'headers': {'Host': '2001:bc8:32d7:302::10'}
                        }
                    },
                    'mux': {
                        'enabled': False,
                        'concurrency': -1
                    }
                },

                {'tag': 'direct',
                 'protocol': 'freedom',
                 'settings': {}}, {
                    'tag': 'block',
                    'protocol': 'blackhole',
                    'settings': {
                        'response': {'type': 'http'}
                    }
                }
            ],
            'routing': {
                'domainStrategy': 'AsIs',
                'rules': [
                    {
                        'type': 'field',
                        'inboundTag': ['api'],
                        'outboundTag': 'api',
                        'enabled': True
                    },
                    {
                        'id': '5692889982520216494',
                        'type': 'field',
                        'outboundTag': 'direct',
                        'domain': ['domain:example-example.com', 'domain:example-example2.com'],
                        'enabled': True
                    },
                    {
                        'id': '4805404872540384867',
                        'type': 'field',
                        'outboundTag': 'block',
                        'domain': ['geosite:category-ads-all'],
                        'enabled': True
                    },
                    {
                        'id': '5698484366022086523',
                        'type': 'field',
                        'outboundTag': 'direct',
                        'domain': ['geosite:cn'],
                        'enabled': True
                    },
                    {
                        'id': '5427097418358676978',
                        'type': 'field',
                        'outboundTag': 'direct',
                        'ip': ['geoip:private', 'geoip:cn'],
                        'enabled': True
                    },
                    {
                        'id': '5686083513038190221',
                        'type': 'field',
                        'port': '0-65535',
                        'outboundTag': 'proxy',
                        'enabled': True
                    }
                ]
            }
        }

    def init_config_path(self):
        '''
        初始化配置文件
        :return:
        '''
        print('正在初始化配置文件.....')
        try:
            for key, value in self.__dict__.items():
                if not isinstance(value, str) or key in ['base_path', 'v2ray_versions_url']:
                    continue
                if not os.path.exists(value):
                    if key == 'subscribe_urls':
                        raise '原始订阅链接文件丢失，程序即将退出！！！！'
                    os.makedirs(value)
            return True
        except Exception as e:
            print(e)
        return False



config = Config(os.getcwd())

if __name__ == '__main__':

    config.init_config_path()










