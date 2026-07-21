
'''
统筹数据库系统管理程序
'''



import json
import pymysql
from queue import Queue
import logging
import config
from utils.tools import tools
from logmanage import LogManager

log = LogManager('Dabase', logging.WARNING, logging.INFO)

'''
# 主要异常类
pymysql.err.Error                # 所有异常的基类
pymysql.err.InterfaceError       # 接口错误（连接不可用等）
pymysql.err.OperationalError     # 操作错误（连接失效、服务器断开等）
pymysql.err.DatabaseError        # 数据库错误
pymysql.err.DataError            # 数据错误
pymysql.err.IntegrityError       # 完整性错误（主键冲突等）
pymysql.err.ProgrammingError     # SQL 语法错误
pymysql.err.InternalError        # 内部错误
pymysql.err.NotSupportedError    # 不支持的操作
'''

class Mysql:
    '''
    初始化数据库系统，建立数据库连接池，管理连接池，
    '''
    def __init__(self, host, port, user, password, charset, size=3, timezone=None):
        '''

        :param host:
        :param port:
        :param user:
        :param password:
        :param charset:
        :param size: 链接池大小，默认3个
        :param timezone: 时区，默认+08:00
        '''

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset
        self.size = size
        self.timezone = timezone
        if not self.timezone:
            try:
                self.timezone = config.project_timezone
            except:
                log.warning('你没有指定时区参数且在配置文件中也没有找到时区配置，将使用默认时区 +08:00')
                self.timezone = '+08:00'

        self.connect_queue = Queue(maxsize=self.size)    # 初始化链接池

        for _ in range(self.size):
            self.create_connect()

    def create_connect(self):
        '''
        创建一个数据库连接
        :return:
        '''
        result = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset=self.charset,
            autocommit=True,        # 自动提交事务
            init_command = f"SET time_zone = '{self.timezone}'"
        )
        self.connect_queue.put(result)

    def get_connect(self):
        '''
        获取一个数据库连接对象
        :return: connect ID，connect object
        '''
        return self.connect_queue.get(timeout=10)

    def release_connect(self, connect, remover=None):
        '''
        释放一个数据库连接对象，如果 remover 为 True，则关闭连接并重新创建一个连接
        :return:
        '''
        if remover:
            # 尝试关闭当前连接
            try:
                connect.close()
            except Exception:
                pass
            # 创建新连接并追加到连接池
            return self.create_connect()

        # 将当前连接重新放回连接池
        self.connect_queue.put(connect)

        return True

    def close_all(self):
        '''
        关闭连接池中的所有连接。
        '''
        log.info('[MySql] - close_all: close all connect')
        while not self.connect_queue.empty():
            self.connect_queue.get().close()


class Sql(Mysql):
    '''
    数据库应用类，提供数据库操作接口
    '''

    def __init__(self, host, port, user, password, charset, size=5, database=None):
        '''
        创建数据库应用接口
        '''
        super().__init__(host, port, user, password, charset, size)

        self.database = database
        if not self.database:
            self.database = 'telegram'

        self.table_users = 'users'
        self.table_chats = 'chats'
        self.table_shares = 'shares'

        # 初始化数据库系统。只对本地数据库进行初始化
        if self.host == '127.0.0.1':
            self.init_database()

    def query(self, database=None, quire=None, params=None, extra='dict'):
        '''
        执行数据库查询操作

        :param database: 数据库名称
        :param quire: 查询语句
        :param params: 查询参数
        :param extra: 额外参数
        :return: 查询结果
        '''

        result = None

        if not database:
            database = self.database

        if not quire:
            log.warning(f"[database] <Sql> - query: 查询语句不能为空")
            return None

        for _ in range(2):
            # 获取一个查询连接
            connect = self.get_connect()

            if not connect:
                self.create_connect()
                continue

            # 创建查询游标
            if extra == 'dict':
                # 创建一个返回结果指向 dict 的专用游标
                cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
            else:
                # 否则返回 Mysql 系统默认的 tuple
                cursor = connect.cursor()

            # 执行查询语句
            try:
                if not quire.startswith('CREATE DATABASE'):
                    cursor.execute(f"USE `{database}`")     # 选择数据库
                cursor.execute(quire, params)

                # fetchall() 对于非查询语句会返回空列表或抛出异常
                if cursor.description:
                    # 有结果集描述说明是查询语句
                    result = cursor.fetchall()
                    if extra == 'dict':
                        result = self.transform_result(quire, result)
                else:
                    # 非查询语句
                    result = True

                return result

            except pymysql.err.InterfaceError as e:
                log.warning(f"<Sql> - query: 数据库连接不可用：{e}")
                self.release_connect(connect, remover=True)
                continue

            except pymysql.err.OperationalError as e:
                error_code = e.args[0] if e.args else None
                log.warning(f"[database] <Sql> - query: 数据库操作错误：{e}")
                if error_code in [2003, 2006, 2013]:
                    self.release_connect(connect, remover=True)
                    continue
                return False

            except pymysql.err.DataError as e:
                log.warning(f"[database] <Sql> - query: 数据错误：{e}")
                return False

            except pymysql.err.IntegrityError as e:
                log.warning(f"[database] <Sql> - query: 完整性错误：{e}")
                return False

            except pymysql.err.ProgrammingError as e:
                log.warning(f"[database] <Sql> - query: SQL 语法错误：{quire}，错误：{e}")
                return False

            except pymysql.err.InternalError as e:
                log.warning(f"[database] <Sql> - query: 数据库内部错误：{e}")
                return False

            except pymysql.err.NotSupportedError as e:
                log.warning(f"[database] <Sql> - query: 不支持的操作：{quire}，错误：{e}")
                return False

            except pymysql.err.DatabaseError as e:
                log.warning(f"[database] <Sql> - query: 数据库错误：{e}")
                return False

            except pymysql.err.Error as e:
                log.warning(f"[database] <Sql> - query: 数据库其它错误：{quire}: {e}")
                return False

            finally:
                if cursor:
                    cursor.close()
                self.release_connect(connect)

        return result

    def transform_result(self, quire, data):
        '''
        转换查询结果

        :param quire:
        :param data:
        :return:
        '''

        if not data:
            return []

        if not quire.startswith('SELECT'):
            return data

        try:
            # 提取表名
            curr_table = quire.split('FROM', 1)[1].strip().split(' ')[0].replace('`', '')
        except Exception:
            raise f"提取表名失败：{quire}"

        # 从表结构中提取 tinyint(1) 和 json 字段
        all_fields = self.get_table_fields(curr_table)
        bool_fields = [row.get('Field') for row in all_fields if row.get('Type') == 'tinyint(1)']   # bool 字段
        json_fields = [row.get('Field') for row in all_fields if row.get('Type') == 'json']     # json 字段

        # 迭代查询结果，将 tinyint(1) 和 json 字段值转换为 Python 对象
        for row in data:
            for key, value in row.items():
                if key in bool_fields:
                    row.update({key: bool(value)})
                if key in json_fields and value:
                    row.update({key: json.loads(value)})
        return data

    def init_database(self):
        '''
        初始化数据库，检查所须数据表是否存在
        :return:
        '''
        print('正在初始化数据库系统 .....................')

        # 创建数据库，执行此命令后，如果系统存在该数据库，则跳过创建步骤
        self.query(quire=f"CREATE DATABASE IF NOT EXISTS `{self.database}`")

        # 提取数据库中所有表名
        database_tables = self.get_database_tables(self.database)

        # 提取本类自定义的名（本类中以 table_ 开头的属性）
        class_tables = [name for attr, name in self.__dict__.items() if attr.startswith('table_')]

        all_tables_fields = {}      # 初始化一个储存所有表字段的容器
        for table in class_tables:
            if table not in database_tables:
                # 如果数据不存在，则创建数据表
                log.error(f'<Sql> - init_database: {table} not found in {self.database}，try create it')
                self.create_table(table)

            # 不管是已有表还是刚创建的表，都重新读取字段结构
            all_tables_fields.update({table: self.get_table_fields(table)})

        if len(all_tables_fields) == len(class_tables) and self.host == '127.0.0.1':
            # 将表字段结构保存到本地，且仅对本地数据库才会执行这个操作
            tools.write_json_content(config.table_structure, all_tables_fields)

    def create_table(self, table_name):
        '''
        创建数据表
        :param table_name:
        :return:
        '''
        # 从本地获取表的字段名
        local_fields = self.get_local_tables_fields(table_name)
        # 构建创建数据表的 SQL 语句
        universal_sql = self.generate_universal_sql(table_name, local_fields)

        return self.query(self.database, universal_sql)

    @classmethod
    def get_local_tables_fields(cls, table_name):
        '''
        提取储存在本地的数据表字段名
        :param table_name:
        :return:
        '''
        with open(config.table_structure, encoding='utf-8') as f:
            data = json.load(f)
            return data.get(table_name)

    def get_table_fields(self, table_name):
        '''
        提取指定数据表中所有字段名
        :param table_name:
        :return:
        '''
        return self.query(self.database, f"SHOW COLUMNS FROM `{table_name}`")

    def get_database_tables(self, database):
        '''
        提取数据库中所有表名
        :param database:
        :return:
        '''
        result = []

        all_tables = self.query(database, "SHOW TABLES", extra='list')

        if all_tables and len(all_tables) > 0:
            result = [row[0] for row in all_tables]

        return result

    @classmethod
    def generate_universal_sql(cls, table_name, columns):
        '''
        构建创建数据表的 SQL 语句
        :param table_name:
        :param columns:
        :return:
        '''
        if not columns:
            raise ValueError(f'缺少数据表结构配置: {table_name}')

        column_defs = []
        primary_keys = []

        for col in columns:
            field_name = f"`{col['Field']}`"
            col_type = col['Type']

            null_str = "NOT NULL" if col['Null'] == "NO" else "DEFAULT NULL"

            default_str = ""
            raw_default = col.get('Default')
            if raw_default is not None:
                raw_default_upper = str(raw_default).upper()

                if "(" in str(raw_default) or raw_default_upper in ["CURRENT_TIMESTAMP", "NULL"]:
                    default_str = f"DEFAULT {raw_default}"
                else:
                    default_str = f"DEFAULT '{raw_default}'"

            extra_str = col.get('Extra', "").replace("DEFAULT_GENERATED", "").strip()

            if col.get('Key') == 'PRI':
                primary_keys.append(field_name)
            elif col.get('Key') == 'UNI':
                extra_str = f"{extra_str} UNIQUE".strip()

            parts = [field_name, col_type, null_str, default_str, extra_str]
            column_defs.append("  " + " ".join(p for p in parts if p))

        if primary_keys:
            pk_stmt = f"  PRIMARY KEY ({', '.join(primary_keys)})"
            column_defs.append(pk_stmt)

        full_sql = (
                f"CREATE TABLE `{table_name}` (\n"
                + ",\n".join(column_defs)
                + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        )

        return full_sql

    @classmethod
    def create_sql(cls, host, port, user, password, charset, database):
        '''
        可以使用此方法创建一个远程数据库服务
        :return:
        '''
        return Sql(
            host,
            port,
            user,
            password,
            charset
        )


sql = Sql(
    host=config.database_account['host'],
    port=config.database_account['port'],
    user=config.database_account['user'],
    password=config.database_account['password'],
    charset=config.database_account['charset'],
    database='telegram',
)


if __name__ == '__main__':


    query = f"SELECT * FROM `chats`"

    datas = sql.query('telegram', query)
    print(len(datas))


    sql.close_all()





