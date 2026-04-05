
'''
创建一个数据库通管局程序

此项目依赖数据提供数据支持，你必须熟知本项目数据库结构，数据表的应用场景
在项目维护过程中，开发者应该对数据结构，使用场景的更改及时更新到本描述章节中

本项目使用到的数据库，数据表描述，



manage 储存了机器人程序运行所必须的参数，比如 update_id
manage 包含以下字段：
    id: bigint 机器人标识符
    update_id: bigint 机器人从 telegram bot api 服务器获取更新的重要依据，它保证了机器人获取到更新的唯一性

rules 储存了规则机器人为群组创建并维护的规则数据，包含了以下字段：
    id: bigint 群组标识符
    type: varchar 群组类型，通常是 supergroup 或 channel
    chat_title: varchar 群组的标题
    administrator: json 储存了群组的管理员信息
    register: json 储存了管理员为群组设定的签到规则
    newcomer: json 储存了管理员为群组设定的新人管理规则
    text: json 储存了管理员为群组设定的文本消息管理规则
    photo: json 储存了管理员为群组设定的图片消息管理规则
    video: json 储存了管理员为群组设定的视频消息管理规则
    voice: json 储存了管理员为群组设定的语音消息管理规则
    link: json 储存了管理员为群组设定的链接消息管理规则
    document: json 储存了管理员为群组设定的文档消息管理规则
    multimedia: json 储存了管理员为群组设定的多媒体消息管理规则
    contact: json 储存了管理员为群组设定的名片或联系人消息管理规则
    forward: json 储存了管理员为群组设定的消息转发管理规则
    checkname: json 储存了管理员为群组设定的对用户的用户名关键字检测的管理规则
    intelligent: json 储存了管理员为群组设定的反广告管理规则

stricture 储存了受机器控制的用户的信息，比如规则机器人对用户的限制规则
    id: bigint 用户标识符
    bot: bigint 机器人 ID，当前用户的受限参数由哪个机器人维护


supergroup 储存了客户端运行时收集到的群组信息，一般记录了客户端用户所在群组

'''
import os
import time
import json
import pymysql
from pymysql.constants.FIELD_TYPE import TINY
from queue import Queue
import logging
import run_config
from logmanage import DailyLogManager
from utils.toolbox import toolbox

log = DailyLogManager('Database', logging.ERROR, logging.INFO)


def contains_uppercase(text):
    '''
    判断字符串是否包含大写字母
    :return:
    '''
    return any(char.isupper() for char in text)

class MySql:
    '''
    param
    '''
    def __init__(self, host, port, user, password, charset):

        '''
        初始化数据库
        :param host: 主机地址，应该是你的网络IP或者本地IP
        :param port: 主机的通信端口，此参数应在 MySql 系统设置或者使用 MySql 的默认值
        :param user: 用户名，连接数据库的依据
        :param password: 密码，为了安全，你应该设置一个安全密码
        :param charset:

        :var self.base_database 当前项目使用的数据库文件名
        :var self.table_manage 数据表，储存了程序运行所必须的参数，比如 update_id
        :var self.table_rules 数据表，储存了规则机器人为群组创建并维护的规则数据
        :var self.table_interact 数据表，储存了用户与机器人交互的信息
        :var self.table_stricture 数据表，储存了受机器控制的用户的信息，比如规则机器人对用户的限制规则
        :var self.table_supergroup 数据表，TDlibe 客户端运行时收集到的群组信息，一般记录了客户端用户所在群组
        :var self.table_groups 数据表，由各种渠道获取到的 telegram 群组，这是个很大型的数据表，主要供搜索机器人检索
        :var self.table_chats 数据表，储存了与机器人或 TDlibe 客户端用户相关的聊天
        :var self.table_users 数据表，储存了与机器人或 TDlibe 客户端用户相关的用户
        '''

        log.info(f'Initializing Database.....')

        self.base_database = 'telegram'
        self.table_manage = 'manage'
        self.table_rules = 'rules'
        self.table_interact = 'interact'
        self.table_restriction = 'restriction'
        self.table_register = 'register'
        self.table_marketing = 'marketing'

        # 自定义转换器，将 TINYINT(1) 转为布尔值
        custom_converters = pymysql.converters.conversions.copy()
        custom_converters[pymysql.constants.FIELD_TYPE.TINY] = self.tinyint_to_bool

        # 初始化查询指针池
        self.pool = Queue(maxsize=20)
        self.pool_size = 20

        for _ in range(20):
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                charset=charset,
                autocommit=True  # 自动提交事务
            )
            self.pool.put(connection)

        self.error_codes = {
            1146: '数据表不存在',
            1136: '试插入或更新的值的数量与目标表的列数不匹配',
            1064: 'mysql语句错误',
            1054: '数据表中没有该字段',
            1046: '未选择数据库',
            1050: '数据表已存在'
        }

        # 用于储存数据珍结果的文件路径
        self.structure_path = os.path.join(run_config.table_structure, f'{self.base_database}.json')

        # 用于储存数据表字段信息的容器，数据库初始化完成后会写入 self.structure_path
        self.fields = {}

        # 初始化数据库
        self.initialize()

    def pool_get(self):
        '''
        从连接池获取连接
        :return:
        '''
        try:
            return self.pool.get(timeout=3)
        except Exception as e:
            log.error(f"<MySql -- pool_get>: 连接池已耗尽，无法获取新的数据库连接 {e}")

        return None

    def initialize(self):
        '''
        # 初始化数据库
        :return:
        '''
        result = None
        conn = self.pool_get()
        try:
            pointer = conn.cursor()
            pointer.execute("SHOW DATABASES")  # 列出所有数据库文件名称
            for database in pointer.fetchall():
                if database[0] == self.base_database:
                    result = True
            if not result:
                log.error(f'<MySql -- initialize>: {self.base_database} not found，try cerate it')
                self.create_database(self.base_database)
                time.sleep(2)

            result = None
            data_tables = self.init_table(self.base_database)
            tables = [name for table, name in self.__dict__.items() if table.startswith('table_')]
            for table in tables:
                # 检查运行依赖数据表是否存在
                if table not in data_tables:
                    # 如果不存在则创建该数据表
                    log.error(f'<MySql -- initialize>: {table} not found in the {self.base_database}，try cerate it')

                    # 构建创建数据表的sql语句
                    create_table_sql = self.get_table_field(table)
                    input(create_table_sql)

                    pointer.execute(f'USE {self.base_database}')
                    pointer.execute(create_table_sql)
                else:
                    query = f'SHOW COLUMNS FROM {table}'
                    query = self.querys(self.base_database, query, data=None)
                    self.fields[table] = query
            if len(self.fields) == len(tables):
                with open(self.structure_path, 'w', encoding='utf-8') as f:
                    json.dump(self.fields, f, ensure_ascii=False, indent=4)
                log.info('<MySql -- initialize>: Table structure saved to file')
                result = True

        except Exception as e:
            log.warning(f'<MySql -- initialize>: error: {e}')
        finally:
            self.pool.put(conn)
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

    def query(self, database_name, sql_query, data=None):

        '''
        执行自定义的SQL查询语句
        :param database_name: type(str), 数据库名
        :param sql_query: type(str), SQL查询语句
        :param data: type(tuple), 查询参数
        :return: type(bool)
        '''
        result = []
        conn = self.pool_get()
        try:
            pointer = conn.cursor()
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
            self.pool.put(conn)
        return result

    def querys(self, database_name, sql_query, data, extra=None):
        '''
        执行自定义的SQL查询语句
        :param database_name: type(str), 数据库名
        :param sql_query: type(str), SQL查询语句
        :param data: type(tuple), 查询参数
        :param extra: type(bool), 是否以列表格式返回结果
        :return: type(list) 或 type(bool)
        '''
        result = []
        conn = self.pool_get()
        try:
            if extra:
                pointer = conn.cursor()
            else:
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
            self.pool.put(conn)
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

            pointer = conn.cursor()
            if toolbox.contains_uppercase(database_name):
                raise  f'Error: 数据库文件名不得包含大字母 {database_name}'
            pointer.execute("CREATE DATABASE " + database_name)
            time.sleep(1)
            if database_name in self.initialize():
                result = True
        except Exception as e:
            log.error( f'Error: 创建数据库文件出错 {e}')
        finally:
            self.pool.put(conn)
        return  result

    def error_message(self, message):
        '''

        :param message:
        :return:
        '''
        try:
            result = message[1:5]
            if result.isdigit() and self.error_codes.get(int(result)):
                return self.error_codes.get(int(result))
        except KeyError as e:
            log.info(f"发现KeyError异常: {e}")
        except ValueError:
            print("数值错误，需要检查输入")
        return message

    @staticmethod
    def tinyint_to_bool(value):
        '''
        自定义转换器，将 TINYINT(1) 转为布尔值
        :param value:
        :return:
        '''
        if value is None:
            return None
        if isinstance(value, str):  # 防止字符串类型
            value = int(value) if value.isdigit() else 0
        return bool(value)

    def get_table_field(self, table_name):
        '''

        :param table_name:
        :return:
        '''

        with open(self.structure_path, encoding='utf-8') as f:
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

        full_sql = f"CREATE TABLE `{table_name}` (\n" + ",\n".join(column_defs) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        return full_sql


sql = MySql('127.0.0.1', 3306, 'root', '', 'utf8mb4')

if __name__ == '__main__':
    pass

    # sql = MySql('42.194.237.208', 3306, 'telegram', 'AAE8TW4cmapxMqk', 'utf8mb4')

    rules = [
        {
            "Field": "chat",
            "Type": "bigint",
            "Null": "NO",
            "Key": "PRI",
            "Default": None,
            "Extra": ""
        },
        {
            "Field": "title",
            "Type": "varchar(200)",
            "Null": "NO",
            "Key": "",
            "Default": None,
            "Extra": ""
        },
        {
            "Field": "administrators",
            "Type": "json",
            "Null": "YES",
            "Key": "",
            "Default": None,
            "Extra": ""
        },
        {
            "Field": "created",
            "Type": "datetime",
            "Null": "NO",
            "Key": "",
            "Default": "CURRENT_TIMESTAMP",
            "Extra": "DEFAULT_GENERATED"
        },
        {
            "Field": "edited",
            "Type": "datetime",
            "Null": "NO",
            "Key": "",
            "Default": "CURRENT_TIMESTAMP",
            "Extra": "DEFAULT_GENERATED on update CURRENT_TIMESTAMP"
        }
    ]

















