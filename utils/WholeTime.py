
'''
项目时区时间统筹，按项目指定的时区获取，计算和转换日期时间
'''
from datetime import datetime, timezone, timedelta
import pytz
import config

PROJECT_TZ = timezone(timedelta(hours=config.project_timeoffset))

class UnitaryTime:
    '''
    统筹时间管理
    所有时间管理统一使用同一时区参数，本项目默认的时区参数在config文档中指定
    如需使用其它时区，可在初始化本类时指定
    '''
    def __init__(self, tz=None):
        '''
        时区设定，默认从配置文件中读取时区参数，也可以指定时区，如 UTC+06:00
        :param tz:
        '''
        if tz and isinstance(tz, str):
            if not tz.startswith('UTC+'):
                raise ValueError("TimeWhole Error: tz must be UTC+06:00")

            tz = tz.replace('UTC+', '')
            self.time_zone = timezone(timedelta(hours=int(tz)))

        elif tz and isinstance(tz, timezone):
            self.time_zone = tz
        else:
            self.time_zone = PROJECT_TZ

    @classmethod
    def unix(cls):
        '''
        获取Unix时间戳
        :return:
        '''
        return int(datetime.now().timestamp())

    def datetime(self, Unix=None, Zone=None, Mat=None):
        '''
        功能：将时间戳格式成日期时间，如果不提供 stamp 参数则返回当前时间
             获取当前时间，
        返回：datetime和str型，指定分隔符(mat)，即可返回str值

        :param Unix: 时间戳，不指定时返回当前时间
        :param Zone: 时区参数，默认使用项目时区
        :param Mat: 格式化日期时间的分隔符，此参数有效时返回的是 str
        :retype: datetime or str
        :return: 返回类似于 2026-07-03 16:12:38.656864+08:00 或 2026-07-03 13:34:05 样式的日期时间
        '''

        tz = self.check_time_zone(Zone)

        # 如果提供了时间戳,则从时间戳创建datetime对象
        if Unix is not None:
            if not isinstance(Unix, int):
                raise ValueError("TimeWhole datetime Error: Unix must be an integer")
            curr = datetime.fromtimestamp(Unix, tz=Zone)
        else:
            curr = datetime.now(tz)

        if Mat:
            return curr.strftime(Mat)
        return curr

    def today(self, Unix=None, Zone=None, Mat=None):
        '''
        返回项目时区的日期
        :param Unix 时间戳，如果没有则默认是当前时间
        :param Zone: 时区参数，默认使用项目时区
        :param Mat: 格式化日期时间的分隔符，此参数有效时返回的是 str
        :retype: datetime or str
        :return:
        '''
        Zone = self.check_time_zone(Zone)

        if not Unix:
            # 将指定的时间戳转换为日期的， type: datetime
            current_date = datetime.now(Zone).date()
        else:
            # 否则将当前时间戳转换为日期的 type: datetime
            current_date = datetime.fromtimestamp(Unix, tz=Zone).date()

        if Mat:
            # 如果指定了日期时间分隔符，则返回格式化后的日期字符串，type: str
            return current_date.strftime(Mat)

        return current_date

    def format_unix(self, DateTime, Zone=None):
        '''
        将日期时间转换为时间戳
        :param DateTime: 要转换的日期时间串，可以是 str 或 datetime 对象
        :param Zone: 时区参数，可以是：
                    - None：使用项目默认时区
                    - 字符串：'UTC+8'、'UTC+08:00'、'Asia/Shanghai' 等
                    - timezone 对象：从 datetime 对象提取的 tzinfo
        :return: unix 时间戳（秒级）
        '''
        # 处理 datetime 对象输入
        if isinstance(DateTime, datetime):
            # 如果 datetime 已有时区信息，直接转换
            if DateTime.tzinfo is not None:
                return int(DateTime.timestamp())

            # 如果没有时区信息，转为字符串后处理
            DateTime = DateTime.strftime('%Y-%m-%d %H:%M:%S')

        tz_obj = self.check_time_zone(Zone)

        # 解析日期字符串
        if len(DateTime) == 10:  # YYYY-MM-DD
            naive_dt = datetime.strptime(DateTime, '%Y-%m-%d')
        else:  # YYYY-MM-DD HH:MM:SS
            naive_dt = datetime.strptime(DateTime, '%Y-%m-%d %H:%M:%S')

        # 添加时区信息并转换为时间戳
        if isinstance(tz_obj, timezone):
            # 标准库的 timezone 对象
            aware_dt = naive_dt.replace(tzinfo=tz_obj)
        else:
            # pytz 时区对象
            aware_dt = tz_obj.localize(naive_dt)

        return int(aware_dt.timestamp())

    def check_time_zone(self, Zone):
        '''
        检查并转换时区参数
        :param Zone: 时区参数，可以是 None、timezone 对象、UTC 偏移字符串或 pytz 时区名
        :return: timezone 或 pytz 时区对象
        '''
        if Zone is None:
            return self.time_zone

        if isinstance(Zone, timezone):
            return Zone

        if isinstance(Zone, str):
            Zone = Zone.strip()

            if Zone.startswith('UTC'):
                offset_text = Zone.replace('UTC', '')

                if not offset_text:
                    return timezone.utc

                sign = 1
                if offset_text.startswith('+'):
                    offset_text = offset_text[1:]
                elif offset_text.startswith('-'):
                    sign = -1
                    offset_text = offset_text[1:]
                else:
                    raise ValueError("TimeWhole Error: UTC timezone must look like 'UTC+8' or 'UTC+08:00'")

                if ':' in offset_text:
                    hour_text, minute_text = offset_text.split(':', 1)
                    hours = int(hour_text)
                    minutes = int(minute_text)
                else:
                    hours = int(offset_text)
                    minutes = 0

                return timezone(sign * timedelta(hours=hours, minutes=minutes))

            try:
                return pytz.timezone(Zone)
            except pytz.UnknownTimeZoneError as error:
                raise ValueError(f"TimeWhole Error: unknown timezone name: {Zone}") from error

        raise ValueError("TimeWhole Error: Zone must be None, timezone object, UTC offset string, or pytz timezone name")




wholetime = UnitaryTime()

if __name__ == "__main__":


    print(timedelta(days=10))

