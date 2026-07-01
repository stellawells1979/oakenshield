'''
定时轮循任务
'''
from database import sql
from utils import timestand

class TimingTask:
    '''
    定时轮循任务
    '''
    def __init__(self):

        self.next_register = 0  # 初始化下一次签到计划任务时间，



    def get_register_task(self):
        '''
        获取群组规则的签到任务
        :return:
        '''
        result = []
        now_time = timestand.unix()
        if now_time < self.next_register:
            return result

        query = f'SELECT `id`,`chat`,`describe`,`expired`,`timing`,`status`,`scheme` FROM {sql.table_register} WHERE `status`=%s'
        register_task = sql.query(sql.database, query, 'Run') or []

        now_date = timestand.date_from_timestamp(now_time)  # 当前日期
        for row in register_task:

            if not row:
                continue
            if now_date > row.get('expired'):
                # 检查签到项目是否过期
                query = f"UPDATE {sql.table_register} SET `status`=%s WHERE `id`=%s"
                sql.query(sql.database, query, ['Exp', row.get('id')])
                continue

            if now_time < row.get('scheme'):
                continue

            query = f"UPDATE {sql.table_register} SET `scheme`=%s WHERE `id`=%s"
            sql.query(sql.database, query, [now_time + (row.get('timing') * 60), row.get('id')])
            result.append([
                'rules',
                'sendMessage',
                {'chat_id': row.get('chat'), 'text': row.get('describe')},
                None
            ])

        self.next_register = timestand.unix() + 600  # 下一次签到计划任务时间，默认5分钟轮循一次签到数据表
        return result


scheduled = TimingTask()

if __name__ == '__main__':
    import time
    while True:

        scheduled.get_register_task()
        time.sleep(2)


