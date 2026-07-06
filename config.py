'''
配置模块
'''



import os
import platform
from myaccount import account

base_path = os.path.dirname(os.path.abspath(__file__))

project_timezone = 'utf-8'  # 项目时区
project_timeoffset = 8
time_format = "%Y-%m-%d %H:%M:%S"
date_format = "%Y-%m-%d"

# 日志文件路径
table_structure = os.path.join(base_path, 'data')

# 储存数据表字段信息的文件
structure_path = os.path.join(base_path, 'data', 'tables_fields.json')

# 识别当前系统信息,视系统是否配置代理以及配置TDLib库文件路径和数据库账户配置以匹配本地测试和服务器运行的需求
database_account = None
database_remote = None
proxy = None
proxies = None
system_name = platform.system().lower()
if system_name == 'windows':
    # 客户端使用此代理
    proxy = {
        'http': 'http://127.0.0.1:10809',
        'socks5': 'socks5h://127.0.0.1:10808'
    }
    # requests使用此代理
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "socks5://127.0.0.1:10808",
    }
    library_path = os.path.join(base_path, 'TDLib', 'bin', 'tdjson.dll')
    database_account = account.database_windows
    database_remote = account.database_ubuntu
elif system_name == 'linux':
    library_path = '/home/ubuntu/td/build/libtdjson.so'
    database_account = account.database_ubuntu
else:
    raise RuntimeError(f'Unsupported system: {platform.system()}')


##############################################
# 结巴分词用到的数据路径
stop_path = os.path.join(base_path, 'data', 'stopwords.txt')
city_path = os.path.join(base_path, 'data', 'city.txt')
extrawords_path = os.path.join(base_path, 'data', 'extrawords.txt')
indivisible_path = os.path.join(base_path, 'data', 'indivisible.txt')
extrawords_more = os.path.join(base_path, 'data', 'extrawords_more.txt')
extr_path = os.path.join(base_path, 'data', 'extrawords.txt')

###############

# 在处理分享链接时应该跳过以下列表中的类型
service_paths = [
    'setlanguage', 'share', 'proxy', 'socks', 'addstickers', 'addemoji', 'addlist', 'addtheme', 'iv', 'bg','login',
    'confirmphone',  'joinchat', 'c', 'premium', 'giftcode', 'boost',
]

# ====================================

# 账号参数，关于账号的APT参数你可以到 https://my.telegram.org
account_dir = 'big'       # 储存当前账号信息的文件夹
accounts = account.accounts.get(account_dir, {})
account_phone = accounts.get('phone')

# 用户数据路径
user_path = os.path.join(base_path, 'myaccount', account_dir)

# 账号认证参数
authorize_params = {
        '@type': 'setTdlibParameters',
        'database_directory': user_path,
        'use_message_database': True,
        'use_secret_chats': False,
        'api_id': accounts.get('api_id'),
        'api_hash': accounts.get('api_hash'),
        'system_language_code': 'en',
        'device_model': 'Desktop',
        'application_version': '1.0',
        'enable_storage_optimizer': True
    }


for config_dir in [table_structure]:
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

if __name__ == '__main__':

    print(accounts.get('api_hash'))





