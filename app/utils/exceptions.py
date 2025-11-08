"""
自定义异常类
"""


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, message: str = "业务错误", code: int = 400, data: any = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class AuthException(BusinessException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", code: int = 2001):
        super().__init__(message, code)


class PermissionException(BusinessException):
    """权限异常"""
    
    def __init__(self, message: str = "权限不足", code: int = 2004):
        super().__init__(message, code)


class NotFoundException(BusinessException):
    """资源不found异常"""
    
    def __init__(self, message: str = "资源不存在", code: int = 1004):
        super().__init__(message, code)


class ValidationException(BusinessException):
    """参数验证异常"""
    
    def __init__(self, message: str = "参数错误", code: int = 1001):
        super().__init__(message, code)


class InsufficientCoinsException(BusinessException):
    """星币不足异常"""
    
    def __init__(self, message: str = "星币余额不足", code: int = 4001):
        super().__init__(message, code)


class DatabaseException(BusinessException):
    """数据库异常"""
    
    def __init__(self, message: str = "数据库操作失败", code: int = 5001):
        super().__init__(message, code)

