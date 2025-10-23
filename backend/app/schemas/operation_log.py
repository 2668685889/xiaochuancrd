"""
操作日志相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID


class OperationLogBase(BaseModel):
    """操作日志基础模式"""
    operation_type: str = Field(..., description="操作类型")
    operation_module: str = Field(..., description="操作模块")
    operation_description: str = Field(..., description="操作描述")
    target_uuid: Optional[UUID] = Field(None, description="操作目标UUID")
    target_name: Optional[str] = Field(None, description="操作目标名称")
    operator_uuid: UUID = Field(..., description="操作者UUID")
    operator_name: str = Field(..., description="操作者姓名")
    operator_ip: Optional[str] = Field(None, description="操作者IP地址")


class OperationLogCreate(OperationLogBase):
    """操作日志创建模式"""
    before_data: Optional[Dict[str, Any]] = Field(None, description="操作前数据")
    after_data: Optional[Dict[str, Any]] = Field(None, description="操作后数据")
    operation_status: str = Field("SUCCESS", description="操作状态")
    error_message: Optional[str] = Field(None, description="错误信息")


class OperationLogResponse(BaseModel):
    """操作日志响应模式"""
    uuid: UUID = Field(..., description="日志UUID")
    operation_type: str = Field(..., description="操作类型")
    operation_module: str = Field(..., description="操作模块")
    operation_description: str = Field(..., description="操作描述")
    target_uuid: Optional[UUID] = Field(None, description="操作目标UUID")
    target_name: Optional[str] = Field(None, description="操作目标名称")
    before_data: Optional[Dict[str, Any]] = Field(None, description="操作前数据")
    after_data: Optional[Dict[str, Any]] = Field(None, description="操作后数据")
    operator_uuid: UUID = Field(..., description="操作者UUID")
    operator_name: str = Field(..., description="操作者姓名")
    operator_ip: Optional[str] = Field(None, description="操作者IP地址")
    operation_status: str = Field(..., description="操作状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    operation_time: datetime = Field(..., description="操作时间")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class OperationLogListResponse(BaseModel):
    """操作日志列表响应模式"""
    items: list[OperationLogResponse] = Field(..., description="日志列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")


class OperationLogFilter(BaseModel):
    """操作日志过滤模式"""
    operation_type: Optional[str] = Field(None, description="操作类型过滤")
    operation_module: Optional[str] = Field(None, description="操作模块过滤")
    operator_name: Optional[str] = Field(None, description="操作者姓名过滤")
    target_name: Optional[str] = Field(None, description="目标名称过滤")
    operation_status: Optional[str] = Field(None, description="操作状态过滤")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")