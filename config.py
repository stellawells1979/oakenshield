'''
配置模块
'''



import os
import platform
from myaccount import account


base_path = os.path.dirname(os.path.abspath(__file__))


# 日志文件路径
table_structure = os.path.join(base_path, 'data')

# 储存数据表字段信息的文件
structure_path = os.path.join(base_path, 'data', 'tables_fields.json')

# TDLib库路径

proxy = None
system_name = platform.system().lower()
if system_name == 'windows':
    proxy = {
        'http': 'http://127.0.0.1:10809',
        'socks5': 'socks5h://127.0.0.1:10808'
    }
    library_path = os.path.join(base_path, 'TDLib', 'bin', 'tdjson.dll')
elif system_name == 'linux':
    library_path = os.path.join(base_path, 'TDLib', 'bin', 'libtdjson.so')
else:
    raise RuntimeError(f'Unsupported system: {platform.system()}')


import platform

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
account_dir = 'guang'       # 储存当前账号信息的文件夹
account_phone = account.phone

# 用户数据路径
user_path = os.path.join(base_path, 'myaccount', account_dir)

# 账号认证参数
authorize_params = {
        '@type': 'setTdlibParameters',
        'database_directory': user_path,
        'use_message_database': True,
        'use_secret_chats': False,
        'api_id': account.api_id,
        'api_hash': account.api_hash,
        'system_language_code': 'en',
        'device_model': 'Desktop',
        'application_version': '1.0',
        'enable_storage_optimizer': True
    }





for config_dir in [table_structure]:
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)





