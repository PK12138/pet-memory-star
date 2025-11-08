"""
统一日志系统
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    """日志管理类"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        """
        获取日志记录器
        :param name: 日志记录器名称
        :return: logging.Logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        # 创建日志记录器
        logger = logging.Logger(name)
        logger.setLevel(logging.DEBUG)
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器（自动轮转）
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, f"{name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 错误日志单独记录
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, f"{name}_error.log"),
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        
        cls._loggers[name] = logger
        return logger


# 创建默认日志记录器
logger = Logger.get_logger("app")


# 便捷函数
def log_info(message: str, **kwargs):
    """记录信息日志"""
    logger.info(f"{message} {kwargs if kwargs else ''}")


def log_error(message: str, error: Exception = None, **kwargs):
    """记录错误日志"""
    if error:
        logger.error(f"{message} | Error: {str(error)} {kwargs if kwargs else ''}", exc_info=True)
    else:
        logger.error(f"{message} {kwargs if kwargs else ''}")


def log_warning(message: str, **kwargs):
    """记录警告日志"""
    logger.warning(f"{message} {kwargs if kwargs else ''}")


def log_debug(message: str, **kwargs):
    """记录调试日志"""
    logger.debug(f"{message} {kwargs if kwargs else ''}")


# API请求日志
def log_api_request(method: str, path: str, user_id: int = None, params: dict = None):
    """记录API请求"""
    log_info(
        f"API Request: {method} {path}",
        user_id=user_id,
        params=params
    )


def log_api_response(method: str, path: str, status_code: int, duration: float):
    """记录API响应"""
    log_info(
        f"API Response: {method} {path}",
        status_code=status_code,
        duration_ms=f"{duration*1000:.2f}ms"
    )

