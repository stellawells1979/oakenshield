'''
创建一个数据库通管局程序
'''
import time
import json
import pymysql
import logging
import config
from queue import Queue
from logmanage import DailyLogManager



log = DailyLogManager('Mylogs', logging.ERROR, logging.INFO)


class MySql:
    '''
    初始化本地数据库，创建连接池，定义一些常用方法
    '''

    def __init__(self, host, port, user, password, charset):

        '''
        初始化数据库
        :param host: 主机地址，应该是你的网络IP或者本地IP
        :param port: 主机的通信端口，此参数应在 MySql 系统设置或者使用 MySql 的默认值
        :param user: 用户名，连接数据库的依据
        :param password: 密码，为了安全，你应该设置一个安全密码
        :param charset:
        '''

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset

        # 初始化查询指针池
        self.pool = Queue(maxsize=20)
        self.pool_size = 20

        for _ in range(self.pool_size):
            connection = self._create_connection()
            self.pool.put(connection)



    def _create_connection(self):
        """
        创建一个新的数据库连接
        """
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset=self.charset,
            autocommit=True  # 自动提交事务
        )

    @classmethod
    def _is_connection_valid(cls, conn):
        """
        检查连接是否可用
        """
        if conn is None:
            return False
        try:
            conn.ping(reconnect=True)
            return True
        except Exception as e:
            log.warning(f"<MySql -- _is_connection_valid>: 连接失效 {e}")
            return False

    def pool_get(self):
        '''
        从连接池获取连接
        :return:
        '''
        try:
            conn = self.pool.get(timeout=3)
        except Exception as e:
            log.error(f"<MySql -- pool_get>: 连接池已耗尽，无法获取新的数据库连接 {e}")
            return None

        if not self._is_connection_valid(conn):
            try:
                conn.close()
            except Exception as e:
                pass
            try:
                conn = self._create_connection()
            except Exception as e:
                log.error(f"<MySql -- pool_get>: 重新创建连接失败 {e}")
                return None

        return conn

    def pool_release(self, conn):
        """
        释放连接回连接池
        """
        if conn is None:
            return

        try:
            if self._is_connection_valid(conn):
                self.pool.put(conn)
            else:
                conn.close()
                # 池子缩水时，补一个新的有效连接进去
                try:
                    self.pool.put(self._create_connection())
                except Exception as e:
                    log.error(f"<MySql -- pool_release>: 补充连接失败 {e}")
        except Exception as e:
            log.error(f"<MySql -- pool_release>: 释放连接失败 {e}")

    def sql_query(self, database_name, sql_query, data, extra=None):
        '''
        执行自定义的SQL查询语句
        :param database_name: type(str), 数据库名
        :param sql_query: type(str), SQL查询语句
        :param data: type(tuple), 查询参数
        :param extra: type(bool), 是否以列表格式返回结果
        :return: type(list) 或 type(bool),此方法默认输出字典格式
        '''
        result = []
        conn = self.pool_get()
        try:
            if conn is None:
                return result

            if extra:
                # 输出列表格式的查询结果
                pointer = conn.cursor()
            else:
                # 输出字典格式的查询结果
                pointer = conn.cursor(cursor=pymysql.cursors.DictCursor)
            pointer.execute(f"USE {database_name}")
            pointer.execute(sql_query, data)
            if sql_query.startswith("SELECT") or sql_query.startswith("SHOW"):
                result = pointer.fetchall()
            else:
                result = True
        except SyntaxError:
            log.error(f'SQL语法错误，请检查查询语句: {sql_query}')
        except Exception as e:
            log.error(f'执行SQL查询失败-- {e}')
        finally:
            self.pool_release(conn)
        return result

    def create_database(self, database_name):
        '''
        创建数据库文件
        :param database_name: 数据库文件名
        :return: type(bool)
        '''
        result = False
        conn = self.pool_get()
        try:
            if conn is None:
                return result

            pointer = conn.cursor()
            pointer.execute("CREATE DATABASE " + database_name)
            result = True
        except Exception as e:
            log.error(f'Error: 创建数据库文件出错 {e}')
        finally:
            self.pool_release(conn)
        return result

class Sql(MySql):
    '''
    初始化项目数据库
    '''
    def __init__(self, host, port, user, password, charset, database='telegram'):
        super().__init__(host, port, user, password, charset)

        self.database = database
        self.table_users = 'users'
        self.table_chats = 'chats'
        self.table_supergroups = 'supergroups'
        self.table_groups = 'groups'

        self.table_manage = 'manage'
        self.table_rules = 'rules'
        self.table_interact = 'interact'
        self.table_restriction = 'restriction'
        self.table_register = 'register'
        self.table_marketing = 'marketing'

        # 收集数据表中的tinyint(1)类型字段,以便将这些字段的值转换为布尔值
        self.tinyint1 = {}

        # 储存数据表的字段信息
        self.all_tables_fields = {}

        self.initialize()

        with open(config.table_structure, encoding='utf-8') as f:
            self.all_tables_fields = json.load(f)



    def query(self, database_name, sql_query, data, extra=None):
        '''
        参查询的结果预处理,
        :param database_name:
        :param sql_query:
        :param data:
        :param extra:
        :return:
        '''
        result = self.sql_query(database_name, sql_query, data, extra)
        if not result:
            return []

        if result and sql_query.startswith("SELECT"):

            sql_query = sql_query.replace('`', '')

            # 截取查询语句中的数据表名
            query_table = sql_query.split('FROM')[1].strip().split(' ')[0]

            tinyint1_field = self.tinyint1.get(query_table, [])
            json_fileds = [field.get('Field') for field in self.all_tables_fields.get(query_table) if field.get('Type') == 'json']
            for row in result:
                for key, value in row.items():
                    if key in tinyint1_field:
                        row.update({key: bool(value)})
                    if key in json_fileds and value:
                        row.update({key: json.loads(value)})
        return result

    def initialize(self):
        '''
        # 初始化数据库,收集数据表结构信息,收集数据表中tinyint(1)字段
        :return:
        '''
        result = None
        conn = self.pool_get()
        try:
            pointer = conn.cursor()
            pointer.execute("SHOW DATABASES")  # 列出所有数据库文件名称
            for database in pointer.fetchall():
                if database[0] == self.database:
                    result = True
            if not result:
                log.error(f'<MySql -- initialize>: {self.database} not found，try cerate it')
                self.create_database(self.database)
                time.sleep(2)

            result = None
            # 获取当前数据库中所有的数据表
            data_tables = self.init_table(self.database)

            tables = [name for table, name in self.__dict__.items() if table.startswith('table_')]
            for table in tables:
                # 检查运行依赖数据表是否存在
                if table not in data_tables:
                    # 如果不存在则创建该数据表
                    log.error(f'<MySql -- initialize>: {table} not found in the {self.database}，try cerate it')

                    # 构建创建数据表的sql语句
                    create_table_sql = self.get_table_field(table)

                    pointer.execute(f'USE {self.database}')
                    pointer.execute(create_table_sql)
                else:
                    # 读取数据表的所有字段及字段属性
                    query = f'SHOW COLUMNS FROM `{table}`'
                    query = self.query(self.database, query, data=None)
                    self.all_tables_fields[table] = query

            if len(self.all_tables_fields) == len(tables):
                # 将所有数据表字段信息储存到本地
                with open(config.table_structure, 'w', encoding='utf-8') as f:
                    json.dump(self.all_tables_fields, f, ensure_ascii=False, indent=4)
                log.info('<MySql -- initialize>: Table structure saved to file')

                # 查询所有数据表的字段属性,将所有tinyint(1)字段名记录下来,以确保查询时能正确转换这些字段值成布尔值
                for table, fields in self.all_tables_fields.items():
                    tinyint1 = []
                    for field in fields:
                        if field.get('Type') == 'tinyint(1)':
                            tinyint1.append(field.get('Field'))
                    if tinyint1:
                        self.tinyint1.update({table: tinyint1})

                result = True

        except Exception as e:
            log.warning(f'<MySql -- initialize>: error: {e}')
        finally:
            self.pool_release(conn)
        return result

    def init_table(self, database_name):
        '''
        :param database_name:
        :return: 当前数据库的所有数据表
        '''
        result = []
        conn = self.pool_get()
        try:
            pointer = conn.cursor()
            pointer.execute(f'USE {database_name}')
            pointer.execute('SHOW TABLES')
            for table in pointer.fetchall():
                result.append(table[0])
        except Exception as e:
            log.warning(f'<MySql -- init_table>: Init table error: {e}')
        finally:
            self.pool.put(conn)
        return result

    def get_table_field(self, table_name):
        '''

        :param table_name:
        :return:
        '''

        with open(config.table_structure, encoding='utf-8') as f:
            data = json.load(f)

        fields = self.generate_universal_sql(table_name, data.get(table_name))
        return fields

    @classmethod
    def generate_universal_sql(cls, table_name, columns):
        '''
        构建创建数据表的sql语句
        :param table_name:
        :param columns:
        :return:
        '''
        column_defs = []
        primary_keys = []

        for col in columns:
            # 1. Basic Identity & Type
            field_name = f"`{col['Field']}`"
            col_type = col['Type']

            # 2. Nullability
            null_str = "NOT NULL" if col['Null'] == "NO" else "DEFAULT NULL"

            # 3. Default Value (Smart handling for functions vs strings)
            default_str = ""
            raw_default = col.get('Default')
            if raw_default is not None:
                # Check if it's a function (like CURRENT_TIMESTAMP or a sequence)
                if "(" in str(raw_default) or str(raw_default).upper() == "CURRENT_TIMESTAMP":
                    default_str = f"DEFAULT {raw_default}"
                else:
                    default_str = f"DEFAULT '{raw_default}'"

            # 4. Extra Features (Auto-increment, On Update, etc.)
            # Strip MySQL metadata flags like 'DEFAULT_GENERATED'
            extra_str = col.get('Extra', "").replace("DEFAULT_GENERATED", "").strip()

            # 5. Key Handling (Collect PKs for composite support)
            if col.get('Key') == 'PRI':
                primary_keys.append(field_name)
            elif col.get('Key') == 'UNI':
                extra_str += " UNIQUE"

            # Assemble the column line
            parts = [field_name, col_type, null_str, default_str, extra_str]
            column_defs.append("  " + " ".join(p for p in parts if p))

        # 6. Final Assembly (Handle Multi-column Primary Keys)
        if primary_keys:
            pk_stmt = f"  PRIMARY KEY ({', '.join(primary_keys)})"
            column_defs.append(pk_stmt)

        full_sql = f"CREATE TABLE `{table_name}` (\n" + ",\n".join(
            column_defs) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        return full_sql

sql = Sql('127.0.0.1', 3306, 'root', '', 'utf8mb4')

if __name__ == '__main__':

    query = f"SELECT `video_calls`, `any_group` FROM `{sql.table_users}` WHERE `id`=5304501737"
    query = sql.query(sql.database, query, data=None)
    print(query)





















