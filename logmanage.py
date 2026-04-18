
'''
h
'''

import os
import logging
from datetime import datetime
import config


class DailyLogManager:
    '''
    r
    '''
    def __init__(self, head, write_level, console_level):
        """
        初始化日志管理器
        :param head: 自定义日志头部信息
        :param write_level: 写入日志文件的最低日志级别，例如：logging.ERROR 或 logging.INFO
        :param console_level: 打印到控制台的最低日志级别，例如：logging.INFO
        """
        self.log_dir = run_config.logs_path
        self.retention_days = run_config.retention_days
        self.current_date = None
        self.head = head
        self.file_log_level = write_level
        self.console_log_level = console_level

        # 创建日志目录（如果不存在）
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 配置日志记录器，确保每个实例都有唯一名称
        self.logger = logging.getLogger(f"{head}_Logger")  # 使用唯一名称，避免冲突
        self.logger.setLevel(logging.DEBUG)

        # 自定义日志格式
        self.log_format = f"%(asctime)s [{self.head}] [%(levelname)s] %(message)s"

        # 避免重复添加处理器（每次实例化时检查处理器）
        if not self.logger.handlers:
            # 添加控制台输出
            self._setup_console_handler()
            # 初始化日志文件处理器
            self._update_log_file(force=True)

        # 防止日志向父级记录器传播，避免日志重复打印
        self.logger.propagate = False

    def _setup_console_handler(self):
        """
        配置控制台日志处理器（StreamHandler）
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_log_level)
        console_handler.setFormatter(logging.Formatter(self.log_format))

        # 检查是否已存在相应的控制台处理器
        if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
            self.logger.addHandler(console_handler)

    def _update_log_file(self, force=False):
        """
        基于当前日期更新日志文件路径，并清理过期日志
        :param force: 是否强制更新
        """
        today = datetime.now().strftime('%Y-%m-%d')

        if not force and self.current_date == today:
            return

        self.current_date = today
        log_file = os.path.join(self.log_dir, f"{today}.log")

        # 查找并移除已有的文件处理器
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)

        # 添加新的文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(self.file_log_level)
        file_handler.setFormatter(logging.Formatter(self.log_format))

        self.logger.addHandler(file_handler)

    def info(self, message):
        """
        输出 INFO 级别日志
        """
        self._update_log_file()
        self.logger.info(message)

    def error(self, message):
        """
        输出 ERROR 级别日志
        """
        self._update_log_file()
        self.logger.error(message)

    def warning(self, message):
        """
        输出 WARNING 级别日志
        """
        self._update_log_file()
        self.logger.warning(message)

    def critical(self, message):
        """
        输出 CRITICAL 级别日志
        """
        self._update_log_file()
        self.logger.critical(message)

    def debug(self, message):
        """
        输出 DEBUG 级别日志
        """
        self._update_log_file()
        self.logger.debug(message)


# 示例用法
if __name__ == "__main__":
    # 初始化日志管理器
    log = DailyLogManager('mylogs', logging.ERROR, logging.INFO)

    # 写入控制台的 INFO（不会写入文件）
    log.info("这是一条普通信息，仅打印到控制台。")

    # 写入日志文件的 ERROR（同时打印到控制台）
    log.error("这是一个错误信息，将写入日志文件以及打印到控制台。")

    # 写入 CRITICAL 日志（严重错误）
    log.critical("系统遇到了严重错误！快速定位文件来源")

    # DEBUG 信息，仅在调试模式时可用
    log.debug("调试信息，仅适用于开发环境")