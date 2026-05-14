'''
小工具
'''

import os
import json
import time
from urllib.parse import urlparse

from database import sql


def update_local_info(table, data):
    '''
    更新数据库数据，此方法适用 user 和 chat 数据表
    :param table:
    :param data:
    :return:
    '''
    result = None
    query = f'SELECT * FROM `{table}` WHERE chat_id=%s'
    sql.query(sql.database, query, [data.get('chat_id')])


    return result


def parse_tme_url(url):
    '''
    解析t.me链接
    :param url:
    :return:
    '''
    parsed = urlparse(url)

    if parsed.scheme not in ('http', 'https'):
        return None

    if parsed.netloc not in ('t.me', 'telegram.me'):
        return None

    parts = [part for part in parsed.path.split('/') if part]

    if not parts:
        return None

    username = parts[0]
    extra = None

    if len(parts) >= 2:
        extra = int(parts[1]) if parts[1].isdigit() else parts[1]


    return [f'{parsed.scheme}://{parsed.netloc}', username, extra]

