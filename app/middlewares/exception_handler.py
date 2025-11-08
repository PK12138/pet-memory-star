"""
全局异常处理中间件
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import traceback

from utils.exceptions import BusinessException
from utils.response import ApiResponse, ErrorCode
from utils.logger import log_error, log_api_request, log_api_response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        start_time = time.time()
        
        # 记录请求
        log_api_request(
            method=request.method,
            path=request.url.path,
            params=dict(request.query_params)
        )
        
        try:
            response = await call_next(request)
            
            # 记录响应
            duration = time.time() - start_time
            log_api_response(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except BusinessException as e:
            # 业务异常
            log_error(
                f"Business Error: {e.message}",
                error=e,
                path=request.url.path,
                code=e.code
            )
            return ApiResponse.error(
                message=e.message,
                code=e.code,
                data=e.data
            )
            
        except ValueError as e:
            # 参数错误
            log_error(
                f"Value Error: {str(e)}",
                error=e,
                path=request.url.path
            )
            return ApiResponse.error(
                message=str(e),
                code=ErrorCode.PARAM_ERROR
            )
            
        except Exception as e:
            # 未知异常
            log_error(
                f"Unexpected Error: {str(e)}",
                error=e,
                path=request.url.path,
                traceback=traceback.format_exc()
            )
            return ApiResponse.error(
                message="服务器内部错误，请稍后重试",
                code=ErrorCode.UNKNOWN_ERROR
            )

