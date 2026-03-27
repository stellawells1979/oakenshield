


import logging
from config import config


# 配置日志
def loginfo(name, log_level=logging.DEBUG, file_log_level=logging.ERROR, log_file=None):
    """
    创建并配置一个日志器
    :param name: 日志器名字（建议为模块名）
    :param log_level: 日志器的总体日志级别（默认是 DEBUG）
    :param file_log_level: 文件处理器的记录级别（默认是 ERROR）
    :param log_file: 日志文件路径（）
    :return: 配置完成的日志器
    """

    if not log_file:
        log_file = config.log_path
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # 避免重复添加处理器
        logger.setLevel(log_level)  # 设置日志器总体级别

        # 定义日志格式
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # 控制台处理器（始终输出所有指定 log_level 的日志信息到终端）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)  # 控制台处理器的日志级别
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器（仅记录指定 file_log_level 级别及以上的日志到文件）

        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(file_log_level)  # 文件处理器的日志级别
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':

    log_Parse = loginfo('TestNode -- ParseNode', logging.DEBUG, logging.ERROR)



