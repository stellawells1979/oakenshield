


'''
项目时区时间统筹，按项目指定的时区获取，计算和转换日期时间
此模块提供在以下上下文中处理datetime和date对象的函数，预定义的项目时区。它包括获取当前时间或日期的方法，
转换Unix时间戳，格式化日期和时间以供显示，并规范各种将日期表示转换为一致的日期对象。

功能：
-now：返回项目时区中的当前日期时间。
-today：返回项目所在时区的当前日期。
-from_timestamp：将Unix时间戳转换为项目的时区日期时间。
-date_from_timestamp：将Unix时间戳转换为项目的时区日期。
-format_datetime：将日期时间或时间戳格式化为项目时区中的字符串。
-format_datetime_tz：使用时区标识符格式化日期时间。
-normalize_date：将各种日期表示转换为项目的时区日期。

'''
import random
from datetime import datetime, date, timezone, timedelta
from config import time_zone, time_offset
import pytz


PROJECT_TZ = timezone(timedelta(hours=time_offset))



def unix():
    '''
    获取Unix时间戳
    :return:
    '''
    return int(datetime.now().timestamp())

def now():
    """
    返回项目时区下的当前 datetime。
    """
    return datetime.now(PROJECT_TZ)

def today():
    """
    返回项目时区下的当前 date。
    """
    return now().date()

def from_timestamp(timestamp):
    """
    将 Unix 时间戳转换为项目时区的日期时间，附带时区位移字符。如：2026-04-27 02:03:43+08:00
    适合用于程序内部的计算和储存场景
    Telegram 的 date 字段就是 Unix 秒级时间戳。

    """
    return datetime.fromtimestamp(timestamp, tz=PROJECT_TZ)

def date_from_timestamp(timestamp=None):
    """
    将 Unix 时间戳转换为项目时区日期。
    """
    if timestamp is None:
        timestamp = unix()
    return from_timestamp(timestamp).date()

def format_datetime(value=None):
    """
    将 datetime 或时间戳格式化为项目时区字符串。
    返回格式化后的字符串，此方法返回结果不带时区信息，略显简洁
    """
    if value is None:
        value = now()
    elif isinstance(value, (int, float)):
        value = from_timestamp(value)
    elif isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=PROJECT_TZ)
        else:
            value = value.astimezone(PROJECT_TZ)

    return value.strftime("%Y-%m-%d %H:%M:%S")

def format_datetime_tz(value=None):
    """
    格式化时间，并附带时区标识。
    返回格式化后的字符串，包含直鸡肉的 UTC+ 时区标识符，用于严谨的时间展示，但不适合用于计算
    :param value: datetime 或时间戳
    """
    return f"{format_datetime(value)} {time_zone}"

def format_unix(date_str, tz_str=None):
    """
    将指定时区的日期或日期时间转换为时间戳
    :param date_str: 日期字符串，支持格式：
        - 日期：YYYY-MM-DD，例如 '2026-06-09'
        - 日期时间：YYYY-MM-DD HH:MM:SS，例如 '2026-06-09 12:30:00'
    :param tz_str: 时区字符串，例如 'UTC+8'、'Asia/Shanghai'
    :return: 时间戳（秒级）
    """
    # 自动识别日期格式
    if not tz_str:
        tz_str = time_zone
    if len(date_str) == 10:  # 仅日期 YYYY-MM-DD
        naive_dt = datetime.strptime(date_str, '%Y-%m-%d')
    else:  # 日期时间 YYYY-MM-DD HH:MM:SS
        naive_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    # 处理 UTC+8 这类时区格式，转换为 pytz 可识别的时区
    if tz_str.startswith('UTC'):
        offset = int(tz_str[3:])
        # 生成对应的时区对象
        tz = pytz.FixedOffset(offset * 60)
    else:
        tz = pytz.timezone(tz_str)

    # 为日期/日期时间添加时区信息
    localized_dt = tz.localize(naive_dt)
    # 转换为时间戳
    timestamp = int(localized_dt.timestamp())
    return timestamp

def normalize_date(value):
    """
    将常见时间类型统一转换为项目时区 date。
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=PROJECT_TZ)
        else:
            value = value.astimezone(PROJECT_TZ)
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, (int, float)):
        if value > 10_000_000_000:
            value = value / 1000
        return from_timestamp(value).date()

    if isinstance(value, str):
        value = value.strip()

        if value.isdigit():
            timestamp = int(value)
            if timestamp > 10_000_000_000:
                timestamp = timestamp / 1000
            return from_timestamp(timestamp).date()

        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=PROJECT_TZ).date()
            except ValueError:
                continue

    raise ValueError(f"无法解析日期字段: {value!r}")

def datetime_from_string(string):
    '''
    解析日期时间字符串，支持UTC时区偏移量
    :param string: 日期时间字符串
    :return: datetime对象
    '''
    string = string.strip()

    parts = string.rsplit(" ", 1)

    if len(parts) == 2 and parts[1].startswith("UTC"):
        datetime_part, tz_part = parts
    else:
        datetime_part = string
        tz_part = None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(datetime_part, fmt)
            break
        except ValueError:
            dt = None

    if dt is None:
        raise ValueError(f"无法解析日期时间字符串: {string}")

    if tz_part:
        offset_hours = int(tz_part.replace("UTC", ""))
        dt = dt.replace(tzinfo=timezone(timedelta(hours=offset_hours)))

    return dt


if __name__ == '__main__':

    pass

















