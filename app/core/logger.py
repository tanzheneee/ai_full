import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """自定义 JSON 格式化器"""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logging(
        app_name: str = "fastapi_app",
        log_level: str = "INFO",
        log_dir: str = "/var/log/fastapi",
        enable_console: bool = True,
        enable_file: bool = True
):
    """
    配置应用日志

    Args:
        app_name: 应用名称
        log_level: 日志级别
        log_dir: 日志目录
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 获取 root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除已有的 handlers
    logger.handlers.clear()

    # JSON 格式化器
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    # 控制台 Handler（开发环境）
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        # 控制台使用普通格式
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # 文件 Handler（生产环境，JSON 格式）
    if enable_file:
        # 应用日志
        app_handler = RotatingFileHandler(
            log_path / f"{app_name}.log",
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(json_formatter)
        logger.addHandler(app_handler)

        # 错误日志
        error_handler = RotatingFileHandler(
            log_path / f"{app_name}_error.log",
            maxBytes=100 * 1024 * 1024,
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        logger.addHandler(error_handler)

    return logger


# 全局 logger 实例
logger = logging.getLogger(__name__)