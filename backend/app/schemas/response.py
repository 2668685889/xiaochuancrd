"""
API响应模式定义
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API统一响应格式"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应格式"""
    success: bool = Field(False, description="请求是否成功")
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[dict] = Field(None, description="错误详情")


# 分页响应包装器
class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    items: list[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")


# 分页API响应包装器
class ApiPaginatedResponse(BaseModel, Generic[T]):
    """分页API响应格式"""
    success: bool = Field(True, description="请求是否成功")
    data: PaginatedResponse[T] = Field(..., description="分页数据")
    message: Optional[str] = Field(None, description="响应消息")