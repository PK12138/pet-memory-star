"""
统一API响应格式
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse
from datetime import datetime


class ApiResponse:
    """统一API响应类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> JSONResponse:
        """
        成功响应
        :param data: 返回数据
        :param message: 提示消息
        :param code: 业务状态码
        """
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "code": code,
                "message": message,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> JSONResponse:
        """
        错误响应
        :param message: 错误消息
        :param code: 业务错误码
        :param data: 额外数据
        """
        return JSONResponse(
            status_code=200,  # HTTP状态码仍为200，业务错误通过code区分
            content={
                "success": False,
                "code": code,
                "message": message,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def paginated(data: list, total: int, page: int = 1, page_size: int = 20, message: str = "查询成功") -> JSONResponse:
        """
        分页响应
        :param data: 数据列表
        :param total: 总数
        :param page: 当前页
        :param page_size: 每页大小
        :param message: 提示消息
        """
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "code": 200,
                "message": message,
                "data": {
                    "list": data,
                    "pagination": {
                        "total": total,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
        )


# 业务错误码定义
class ErrorCode:
    """业务错误码"""
    # 通用错误 1xxx
    SUCCESS = 200
    UNKNOWN_ERROR = 1000
    PARAM_ERROR = 1001
    NOT_FOUND = 1004
    
    # 认证错误 2xxx
    UNAUTHORIZED = 2001
    TOKEN_EXPIRED = 2002
    TOKEN_INVALID = 2003
    PERMISSION_DENIED = 2004
    
    # 用户错误 3xxx
    USER_NOT_FOUND = 3001
    USER_EXISTS = 3002
    PASSWORD_ERROR = 3003
    
    # 业务错误 4xxx
    INSUFFICIENT_COINS = 4001
    ALREADY_SIGNED_IN = 4002
    TASK_LIMIT_REACHED = 4003
    MEMORIAL_NOT_FOUND = 4004
    
    # 系统错误 5xxx
    DATABASE_ERROR = 5001
    FILE_UPLOAD_ERROR = 5002
    EXTERNAL_API_ERROR = 5003

