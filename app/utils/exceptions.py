class InsufficientCoinsException(Exception):
    """星币余额不足异常"""
    pass

class DatabaseException(Exception):
    """数据库操作异常"""
    pass

class ValidationException(Exception):
    """请求数据校验异常"""
    pass
