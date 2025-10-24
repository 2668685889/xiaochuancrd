"""
客户相关的Pydantic模式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class CustomerBase(BaseModel):
    """客户基础模型"""
    customerName: str = Field(..., min_length=1, max_length=100, description="客户名称")
    customerCode: str = Field(..., min_length=1, max_length=50, description="客户编码")
    contactPerson: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    address: Optional[str] = Field(None, description="地址信息")


class CustomerCreate(CustomerBase):
    """创建客户请求模型"""
    pass


class CustomerUpdate(BaseModel):
    """更新客户请求模型"""
    customerName: Optional[str] = Field(None, min_length=1, max_length=100, description="客户名称")
    customerCode: Optional[str] = Field(None, min_length=1, max_length=50, description="客户编码")
    contactPerson: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    address: Optional[str] = Field(None, description="地址信息")
    isActive: Optional[bool] = Field(None, description="是否激活")


class CustomerResponse(CustomerBase):
    """客户响应模型"""
    uuid: UUID = Field(..., description="客户UUID")
    isActive: bool = Field(..., description="是否激活")
    createdAt: datetime = Field(..., description="创建时间")
    updatedAt: datetime = Field(..., description="更新时间")
    deletedAt: Optional[datetime] = Field(None, description="软删除时间")
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """客户列表响应模型"""
    items: list[CustomerResponse] = Field(..., description="客户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")