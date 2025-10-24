"""
供应商相关的Pydantic模式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class SupplierBase(BaseModel):
    """供应商基础模式"""
    supplierName: str = Field(..., min_length=1, max_length=100, description="供应商名称")
    supplierCode: str = Field(..., min_length=1, max_length=50, description="供应商编码")
    contactPerson: str = Field(..., min_length=1, max_length=50, description="联系人")
    phone: str = Field(..., min_length=1, max_length=20, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    address: Optional[str] = Field(None, max_length=500, description="地址")


class SupplierCreate(BaseModel):
    """供应商创建模式"""
    supplierName: str
    supplierCode: Optional[str] = None  # 可选，系统会自动生成
    contactPerson: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class SupplierUpdate(BaseModel):
    """供应商更新模式"""
    supplierName: Optional[str] = None
    supplierCode: Optional[str] = None
    contactPerson: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    isActive: Optional[bool] = None


class SupplierResponse(BaseModel):
    """供应商响应模式"""
    uuid: UUID
    supplierName: str
    supplierCode: str
    contactPerson: str
    phone: str
    email: Optional[str]
    address: Optional[str]
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    """供应商列表响应模式"""
    items: list[SupplierResponse]
    total: int
    page: int
    size: int
    pages: int