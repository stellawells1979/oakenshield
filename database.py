'''
创建一个数据库通管局程序
'''

import subprocess
from pathlib import Path
import json
import pymysql
import logging
import config
from queue import Queue
from logg import LogManager

log = LogManager('Dabase', logging.ERROR, logging.INFO)


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
        self.connection_name = f"{self.user}@{self.host}:{self.port}"

        # 初始化数据库连接池
        self.pool = Queue(maxsize=100)
        self.pool_size = 5
        self.closed = False
        self.connected = False

        self.connect()

    def connect(self):
        """
        创建数据库连接池。
        只在程序启动阶段建立连接；连接成功后，上层再执行数据库初始化。
        """
        log.info(f"<MySql -- connect>: [{self.connection_name}] 开始创建数据库连接池，pool_size={self.pool_size}")

        try:
            for index in range(self.pool_size):
                connection = self._create_connection()
                self.pool.put(connection)
            self.connected = True
            log.info(f"<MySql -- connect>: [{self.connection_name}] 数据库连接池创建成功")
            return True

        except pymysql.err.OperationalError as e:
            self.connected = False
            self.closed = True

            error_code = e.args[0] if e.args else None
            error_message = e.args[1] if len(e.args) > 1 else str(e)

            log.error(
                f"<MySql -- connect>: [{self.connection_name}] 连接数据库失败，"
                f"error_code={error_code}, error_message={error_message}"
            )

            self._explain_connection_error(error_code, error_message)
            self._clear_pool()
            return False

        except Exception as e:
            self.connected = False
            self.closed = True

            log.error(f"<MySql -- connect>: [{self.connection_name}] 连接数据库失败，error={e}")
            self._clear_pool()
            return False

    def _clear_pool(self):
        """
        清理连接池中已经创建成功的连接。
        主要用于连接池初始化过程中部分连接成功、后续连接失败的场景。
        """
        closed_count = 0

        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
                closed_count += 1
            except Exception as e:
                log.warning(f"<MySql -- _clear_pool>: [{self.connection_name}] 关闭数据库连接失败 {e}")

        if closed_count:
            log.info(f"<MySql -- _clear_pool>: [{self.connection_name}] 已清理 {closed_count} 个数据库连接")

    def close_all(self):
        """
        关闭连接池中的所有数据库连接。
        注意：只能关闭当前还在池子里的连接；
        如果有连接正在被业务代码使用，需要等它 release 回池后才能关闭。
        """
        self.closed = True
        closed_count = 0

        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
                closed_count += 1
            except Exception as e:
                log.warning(f"<MySql -- close_all>: 关闭数据库连接失败 {e}")

        log.info(f"<MySql -- close_all>: 已关闭 {closed_count} 个数据库连接")

    def _create_connection(self):
        """
        创建一个新的数据库连接。
        """
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset=self.charset,
            autocommit=True
        )

    def pool_get(self):
        '''
        从连接池获取连接。
        这里不再检测连接时效性，只负责从连接池取连接。
        :return:
        '''
        if self.closed:
            log.warning("<MySql -- pool_get>: 数据库连接池已关闭")
            return None

        try:
            conn = self.pool.get(timeout=3)

            try:
                conn.ping(reconnect=True)
            except Exception as e:
                log.warning(f"<MySql -- pool_get>: 数据库连接已失效，准备重建连接，error={repr(e)}")
                try:
                    conn.close()
                except Exception:
                    pass
                conn = self._create_connection()

            return conn

        except Exception as e:
            log.error(f"<MySql -- pool_get>: 连接池已耗尽，无法获取数据库连接 {e}")
            return None

    def pool_release(self, conn):
        """
        释放连接回连接池。
        这里不再检测连接时效性，只负责归还连接。
        """
        if conn is None:
            return

        if self.closed:
            try:
                conn.close()
            except Exception as e:
                log.warning(f"<MySql -- pool_release>: 关闭连接失败 {e}")
            return

        try:
            self.pool.put(conn)
        except Exception as e:
            log.error(f"<MySql -- pool_release>: 释放连接失败 {e}")

    def _explain_connection_error(self, error_code, error_message):
        """
        根据 MySQL 错误码输出更明确的排查建议。
        """
        if error_code == 1130:
            log.error(
                f"<MySql -- connect>: [{self.connection_name}] MySQL 拒绝当前客户端主机连接。"
                f"通常原因：数据库用户没有授权当前公网 IP 访问。"
            )
            log.error(
                "<MySql -- connect>: 请在 MySQL 服务端检查用户授权，例如 user@'%' 或指定客户端 IP。"
            )

        elif error_code == 1045:
            log.error(
                f"<MySql -- connect>: [{self.connection_name}] 用户名或密码错误，或该用户没有当前来源主机的登录权限。"
            )

        elif error_code == 2003:
            log.error(
                f"<MySql -- connect>: [{self.connection_name}] 无法连接到 MySQL 服务。"
                f"请检查服务器 IP、端口、防火墙、安全组、MySQL bind-address。"
            )

        elif error_code == 2013:
            log.error(
                f"<MySql -- connect>: [{self.connection_name}] 连接过程中断。"
                f"请检查网络稳定性、MySQL 超时配置或服务端连接限制。"
            )

        else:
            log.error(
                f"<MySql -- connect>: [{self.connection_name}] 未识别的连接错误：{error_code} - {error_message}"
            )

    def sql_query(self, database_name, sql_query, data=None, extra=None):
        '''
        执行自定义的SQL查询语句
        :param database_name: type(str), 数据库名
        :param sql_query: type(str), SQL查询语句
        :param data: type(tuple/list/None), 查询参数
        :param extra: type(bool), 是否以列表格式返回结果
        :return: type(list) 或 type(bool), 此方法默认输出字典格式
        '''
        result = []
        conn = self.pool_get()
        pointer = None
        connection_broken = False

        try:
            if conn is None:
                return result

            if extra:
                # 输出普通 tuple 格式查询结果
                pointer = conn.cursor()
            else:
                # 输出字典格式查询结果
                pointer = conn.cursor(cursor=pymysql.cursors.DictCursor)

            pointer.execute(f"USE `{database_name}`")
            pointer.execute(sql_query, data)

            sql_type = sql_query.strip().upper()
            if sql_type.startswith(("SELECT", "SHOW", "DESC", "DESCRIBE")):
                result = pointer.fetchall()
            else:
                result = True

        except SyntaxError:
            log.error(f'SQL语法错误，请检查查询语句: {sql_query}')
        except pymysql.err.InterfaceError as e:
            connection_broken = True
            log.error(
                f'数据库连接不可用-- type={type(e).__name__}, '
                f'args={getattr(e, "args", None)}, error={repr(e)}--{sql_query}'
            )
        except pymysql.err.OperationalError as e:
            error_code = e.args[0] if e.args else None
            connection_broken = error_code in [0, 2003, 2006, 2013]

            log.error(
                f'数据库操作失败-- type={type(e).__name__}, '
                f'args={getattr(e, "args", None)}, error={repr(e)}--{sql_query}'
            )
        except Exception as e:
            log.error(
                f'执行SQL查询失败-- type={type(e).__name__}, '
                f'args={getattr(e, "args", None)}, error={repr(e)}--{sql_query}'
            )
        finally:
            if pointer:
                try:
                    pointer.close()
                except Exception as e:
                    connection_broken = True
                    log.warning(f"<MySql -- sql_query>: 关闭游标失败 {repr(e)}")

            if connection_broken and conn:
                try:
                    conn.close()
                except Exception:
                    pass

                try:
                    conn = self._create_connection()
                except Exception as e:
                    conn = None
                    log.error(f"<MySql -- sql_query>: 重建数据库连接失败 {repr(e)}")

            self.pool_release(conn)

        return result

    def create_database(self, database_name):
        '''
        创建数据库
        :param database_name: 数据库名
        :return: type(bool)
        '''
        result = False
        conn = self.pool_get()
        pointer = None

        try:
            if conn is None:
                return result

            pointer = conn.cursor()
            pointer.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
            result = True

        except Exception as e:
            log.error(f'Error: 创建数据库出错 {e}')
        finally:
            if pointer:
                try:
                    pointer.close()
                except Exception as e:
                    log.warning(f"<MySql -- create_database>: 关闭游标失败 {e}")

            self.pool_release(conn)

        return result

class DatabaseUploader:
    """
    本地 MySQL 上传到远程 MySQL 的工具类。

    说明：
    1. 只在需要迁移数据库时使用；
    2. 不影响 Sql 类的日常连接、查询和初始化；
    3. 底层使用 mysqldump + mysql，适合百万级数据；
    4. 支持上传整个数据库或指定数据表；
    5. 默认是覆盖式上传，请谨慎使用。
    """

    def __init__(self, local_config, remote_config, dump_dir=None):
        """
        :param local_config: 本地数据库配置
        :param remote_config: 远程数据库配置
        :param dump_dir: SQL 临时文件目录
        """
        self.local_config = self._normalize_config(local_config)
        self.remote_config = self._normalize_config(remote_config)

        if dump_dir is None:
            self.dump_dir = Path(config.base_path) / 'data' / 'mysql_dump'
        else:
            self.dump_dir = Path(dump_dir)

        self.dump_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _normalize_config(db_config):
        """
        标准化数据库配置。
        """
        return {
            'host': db_config.get('host', '127.0.0.1'),
            'port': str(db_config.get('port', 3306)),
            'user': db_config.get('user', 'root'),
            'password': db_config.get('password', ''),
            'charset': db_config.get('charset', 'utf8mb4'),
            'database': db_config.get('database', 'telegram'),
        }

    @staticmethod
    def _password_arg(password):
        """
        构建 mysql / mysqldump 密码参数。
        注意：-p 和密码之间不能有空格。
        """
        if password:
            return f'-p{password}'

        return None

    @staticmethod
    def _safe_command(command):
        """
        隐藏命令中的密码，避免日志泄露。
        """
        safe = []

        for item in command:
            if isinstance(item, str) and item.startswith('-p') and len(item) > 2:
                safe.append('-p******')
            else:
                safe.append(item)

        return safe

    @classmethod
    def _run_command(cls, command, input_file=None, output_file=None, error_file=None):
        """
        执行系统命令。
        """
        log.info(f'<DatabaseUploader>: 执行命令 {" ".join(cls._safe_command(command))}')

        stdin = None
        stdout = None
        stderr = None

        try:
            if input_file:
                stdin = open(input_file, 'rb')

            if output_file:
                stdout = open(output_file, 'wb')

            if error_file:
                stderr = open(error_file, 'ab')

            result = subprocess.run(
                command,
                stdin=stdin,
                stdout=stdout if stdout else subprocess.DEVNULL,
                stderr=stderr if stderr else subprocess.PIPE
            )

            if result.returncode != 0:
                if error_file:
                    log.error(f'<DatabaseUploader>: 命令执行失败，详情请查看 {error_file}')
                else:
                    error_message = result.stderr.decode('utf-8', errors='ignore')
                    log.error(f'<DatabaseUploader>: 命令执行失败 {error_message}')

                return False

            return True

        except FileNotFoundError as e:
            log.error(
                '<DatabaseUploader>: 未找到 mysql 或 mysqldump 命令，'
                '请确认 MySQL bin 目录已经加入 Windows Path 环境变量'
            )
            log.error(f'<DatabaseUploader>: error: {e}')
            return False

        except Exception as e:
            log.error(f'<DatabaseUploader>: 命令执行异常 {e}')
            return False

        finally:
            if stdin:
                stdin.close()

            if stdout:
                stdout.close()

            if stderr:
                stderr.close()

    def _mysql_command(self, db_config, database_name=None, execute_sql=None):
        """
        构建 mysql 命令。
        """
        command = [
            'mysql',
            '-h', db_config['host'],
            '-P', db_config['port'],
            '-u', db_config['user'],
        ]

        password_arg = self._password_arg(db_config['password'])
        if password_arg:
            command.append(password_arg)

        command.append(f'--default-character-set={db_config["charset"]}')

        if database_name:
            command.append(database_name)

        if execute_sql:
            command.extend(['-e', execute_sql])

        return command

    def _mysqldump_command(self, db_config, tables=None):
        """
        构建 mysqldump 命令。
        """
        command = [
            'mysqldump',
            '-h', db_config['host'],
            '-P', db_config['port'],
            '-u', db_config['user'],
        ]

        password_arg = self._password_arg(db_config['password'])
        if password_arg:
            command.append(password_arg)

        command.extend([
            f'--default-character-set={db_config["charset"]}',
            '--single-transaction',
            '--quick',
            '--routines',
            '--triggers',
            '--events',
            '--set-gtid-purged=OFF',
            '--add-drop-table',
            db_config['database'],
        ])

        if tables:
            command.extend(tables)

        return command

    def _dump_file_path(self, mode, tables=None):
        """
        生成 dump 文件路径。
        """
        database = self.local_config['database']

        if mode == 'database':
            return self.dump_dir / f'{database}_full.sql'

        table_part = '_'.join(tables)
        return self.dump_dir / f'{database}_{table_part}.sql'

    def _dump_local_database(self, mode, tables=None):
        """
        导出本地数据库或指定数据表。
        """
        dump_file = self._dump_file_path(mode, tables)

        log.info(f'<DatabaseUploader>: 开始导出本地数据，mode={mode}, dump_file={dump_file}')

        command = self._mysqldump_command(
            db_config=self.local_config,
            tables=tables if mode == 'tables' else None
        )

        if not self._run_command(command, output_file=dump_file):
            return None

        log.info(f'<DatabaseUploader>: 本地数据导出完成 {dump_file}')

        return dump_file

    def _recreate_remote_database(self):
        """
        删除并重建远程数据库。
        """
        database = self.remote_config['database']
        charset = self.remote_config['charset']

        sql = (
            f"DROP DATABASE IF EXISTS `{database}`; "
            f"CREATE DATABASE `{database}` "
            f"DEFAULT CHARACTER SET {charset} "
            f"COLLATE {charset}_unicode_ci;"
        )

        command = self._mysql_command(
            db_config=self.remote_config,
            execute_sql=sql
        )

        log.warning(f'<DatabaseUploader>: 即将覆盖远程数据库 `{database}`')

        return self._run_command(command)

    def _drop_remote_tables(self, tables):
        """
        删除远程指定数据表。
        """
        database = self.remote_config['database']

        table_sql = ' '.join(
            f'DROP TABLE IF EXISTS `{table}`;'
            for table in tables
        )

        sql = (
            f"USE `{database}`; "
            f"SET FOREIGN_KEY_CHECKS=0; "
            f"{table_sql} "
            f"SET FOREIGN_KEY_CHECKS=1;"
        )

        command = self._mysql_command(
            db_config=self.remote_config,
            execute_sql=sql
        )

        log.warning(f'<DatabaseUploader>: 即将覆盖远程数据表 {tables}')

        return self._run_command(command)

    def _import_to_remote(self, dump_file):
        """
        将 SQL 文件导入远程数据库。
        """
        database = self.remote_config['database']

        command = self._mysql_command(
            db_config=self.remote_config,
            database_name=database
        )

        log.info(f'<DatabaseUploader>: 开始导入到远程数据库 `{database}`')

        return self._run_command(command, input_file=dump_file)

    def upload_database(self, remove_dump_file=False, confirm=False):
        """
        上传整个本地数据库到远程，并覆盖远程数据库。
        :param remove_dump_file: 上传完成后是否删除临时 SQL 文件
        :param confirm: 是否已经确认覆盖
        :return: bool
        """
        if not confirm:
            log.error('<DatabaseUploader>: 覆盖整个远程数据库属于危险操作，请设置 confirm=True')
            return False

        dump_file = None

        try:
            dump_file = self._dump_local_database(mode='database')

            if not dump_file:
                return False

            if not self._recreate_remote_database():
                return False

            if not self._import_to_remote(dump_file):
                return False

            log.info('<DatabaseUploader>: 整个数据库上传完成')
            return True

        finally:
            self._remove_dump_file(dump_file, remove_dump_file)

    def upload_tables(self, tables, remove_dump_file=False, confirm=False):
        """
        上传指定数据表到远程，并覆盖远程同名表。
        :param tables: 要上传的数据表列表
        :param remove_dump_file: 上传完成后是否删除临时 SQL 文件
        :param confirm: 是否已经确认覆盖
        :return: bool
        """
        if not confirm:
            log.error('<DatabaseUploader>: 覆盖远程数据表属于危险操作，请设置 confirm=True')
            return False

        if not tables:
            log.error('<DatabaseUploader>: upload_tables 必须提供 tables')
            return False

        dump_file = None

        try:
            dump_file = self._dump_local_database(
                mode='tables',
                tables=tables
            )

            if not dump_file:
                return False

            if not self._drop_remote_tables(tables):
                return False

            if not self._import_to_remote(dump_file):
                return False

            log.info(f'<DatabaseUploader>: 指定数据表上传完成 {tables}')
            return True

        finally:
            self._remove_dump_file(dump_file, remove_dump_file)

    @staticmethod
    def _remove_dump_file(dump_file, remove_dump_file):
        """
        删除临时 SQL 文件。
        """
        if remove_dump_file and dump_file and dump_file.exists():
            try:
                dump_file.unlink()
                log.info(f'<DatabaseUploader>: 已删除临时 SQL 文件 {dump_file}')
            except Exception as e:
                log.warning(f'<DatabaseUploader>: 删除临时 SQL 文件失败 {e}')

class Sql(MySql):
    '''
    初始化项目数据库
    '''

    def __init__(self, host, port, user, password, charset, database, extra=None):
        '''
        初始化数据库
        :param host:
        :param port:
        :param user:
        :param password:
        :param charset:
        :param database:
        :param extra: 此参数有效时会在mysql系统中创建指定数据库文件及相关数据表
        '''
        super().__init__(host, port, user, password, charset)

        self.mysqldump = None       # 初始化一个数据库远程dump服务
        self.remote_query = None    # 初始化一个远程数据库查询服务
        self.database = database
        self.table_users = 'users'
        self.table_chats = 'chats'
        self.table_shares = 'shares'

        # 收集数据表中的 tinyint(1) 类型字段，以便将这些字段的值转换为布尔值
        self.tinyint1 = {}

        # 储存数据表的字段信息
        self.all_tables_fields = {}

        # 连接池创建成功后，再执行数据库初始化
        if self.connected and not self.closed:

            if extra:
                self.initialize()
                log.warning("<Sql -- __init__>: 连接数据库成功，正在执行初始化")
            else:
                log.warning("<Sql -- __init__>: 连接数据库成功")
        else:
            log.error("<Sql -- __init__>: 连接数据库失败")

    def create_service(self, host, port, user, password, charset, database, extra=None):
        '''
        创建一个远程数据库查询服务
        :return:
        '''
        if not self.remote_query:
            self.remote_query = Sql(host, port, user, password, charset, database, extra)

        return self.remote_query

    def remote_update(self, tables=None):
        '''
        远程更新数据库
        将本的数据库或者数据表履盖到远程mysql的同名数据库
        本函数调用命令行命令启动sql系统的底层基础功能实现系统级履盖操作
        '''
        local_config = {
            'host': config.database_account['host'],
            'port': config.database_account['port'],
            'user': config.database_account['user'],
            'password': config.database_account['password'],
            'charset': config.database_account['charset'],
            'database': 'telegram',
        }

        remote_config = {
            'host': config.database_remote['host'],
            'port': config.database_remote['port'],
            'user': config.database_remote['user'],
            'password': config.database_remote['password'],
            'charset': config.database_remote['charset'],
            'database': 'telegram',
        }

        if not self.mysqldump:
            self.mysqldump = DatabaseUploader(
                local_config=local_config,
                remote_config=remote_config
            )

        if tables:
            # 如果只想上传指定表，使用下面这个：
            self.mysqldump.upload_tables(
                tables=tables,
                confirm=True,
                remove_dump_file=False
            )
        else:
            # 上传整个数据库，并覆盖远程数据库
            self.mysqldump.upload_database(
                confirm=True,
                remove_dump_file=False
            )

    def query(self, database_name, sql_query, data=None, extra=None):
        '''
        查询结果预处理
        :param database_name:
        :param sql_query:
        :param data:
        :param extra:
        :return:
        '''
        result = self.sql_query(database_name, sql_query, data, extra)
        if not result:
            return []

        if result and sql_query.strip().upper().startswith("SELECT"):
            clean_sql = sql_query.replace('`', '')

            try:
                # 截取查询语句中的数据表名
                query_table = clean_sql.split('FROM', 1)[1].strip().split(' ')[0]
            except Exception:
                return result

            tinyint1_field = self.tinyint1.get(query_table, [])
            table_fields = self.all_tables_fields.get(query_table, [])
            json_fields = [
                field.get('Field')
                for field in table_fields
                if field.get('Type') == 'json'
            ]

            for row in result:
                for key, value in row.items():
                    if key in tinyint1_field:
                        row.update({key: bool(value)})

                    if key in json_fields and value:
                        try:
                            row.update({key: json.loads(value)})
                        except Exception:
                            log.warning(f"<Sql -- query>: JSON 字段解析失败 {query_table}.{key}")

        return result

    def initialize(self):
        '''
        初始化数据库、数据表结构，并收集字段信息。
        前提：连接池已经成功创建。
        :return:
        '''
        result = False
        conn = self.pool_get()
        pointer = None

        try:
            if conn is None:
                return result

            pointer = conn.cursor()

            # 创建数据库并切换到当前数据库
            pointer.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}`")
            pointer.execute(f"USE `{self.database}`")

            # 获取当前数据库中已有的数据表
            data_tables = self.init_table(self.database)

            # 获取项目运行依赖的数据表名
            tables = [
                name
                for attr, name in self.__dict__.items()
                if attr.startswith('table_')
            ]

            for table in tables:
                if table not in data_tables:
                    log.error(f'<MySql -- initialize>: {table} not found in {self.database}，try create it')

                    create_table_sql = self.get_table_field(table)
                    pointer.execute(create_table_sql)

                # 不管是已有表还是刚创建的表，都重新读取字段结构
                query = f'SHOW COLUMNS FROM `{table}`'
                self.all_tables_fields[table] = self.sql_query(self.database, query, data=None)

            if len(self.all_tables_fields) == len(tables):
                self._save_table_structure()
                self._collect_tinyint_fields()
                result = True

        except Exception as e:
            log.warning(f'<MySql -- initialize>: error: {e}')
        finally:
            if pointer:
                try:
                    pointer.close()
                except Exception as e:
                    log.warning(f"<Sql -- initialize>: 关闭游标失败 {e}")

            self.pool_release(conn)

        return result

    def _save_table_structure(self):
        """
        将当前数据表字段信息保存到本地结构文件。
        """
        with open(config.structure_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_tables_fields, f, ensure_ascii=False, indent=4)

        log.info('<MySql -- initialize>: Table structure saved to file')

    def _collect_tinyint_fields(self):
        """
        收集 tinyint(1) 字段，用于查询结果布尔值转换。
        """
        self.tinyint1.clear()

        for table, fields in self.all_tables_fields.items():
            tinyint1 = [
                field.get('Field')
                for field in fields
                if field.get('Type') == 'tinyint(1)'
            ]

            if tinyint1:
                self.tinyint1[table] = tinyint1

    def init_table(self, database_name):
        '''
        :param database_name:
        :return: 当前数据库的所有数据表
        '''
        result = []
        conn = self.pool_get()
        pointer = None

        try:
            if conn is None:
                return result

            pointer = conn.cursor()
            pointer.execute(f'USE `{database_name}`')
            pointer.execute('SHOW TABLES')

            for table in pointer.fetchall():
                result.append(table[0])

        except Exception as e:
            log.warning(f'<MySql -- init_table>: Init table error: {e}')
        finally:
            if pointer:
                try:
                    pointer.close()
                except Exception as e:
                    log.warning(f"<Sql -- init_table>: 关闭游标失败 {e}")

            self.pool_release(conn)

        return result

    def get_table_field(self, table_name):
        '''
        从本地结构文件读取数据表字段信息，并生成 CREATE TABLE SQL。
        :param table_name:
        :return:
        '''
        with open(config.structure_path, encoding='utf-8') as f:
            data = json.load(f)

        fields = self.generate_universal_sql(table_name, data.get(table_name))
        return fields

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

# 构建本地数据库服务
sql = Sql(
    config.database_account['host'],
    config.database_account['port'],
    config.database_account['user'],
    config.database_account['password'],
    config.database_account['charset'],
    'telegram',
    extra=True
)


if __name__ == '__main__':

    all_urls = f"SELECT * FROM `{sql.table_chats}`"








