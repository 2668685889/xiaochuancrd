"""
产品相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProductBase(BaseModel):
    """产品基础模式"""
    productName: str = Field(..., min_length=1, max_length=100, description="产品名称")
    productCode: str = Field(..., min_length=1, max_length=50, description="产品编码")
    description: Optional[str] = Field(None, max_length=500, description="产品描述")
    unitPrice: float = Field(..., ge=0, description="单价")
    currentQuantity: int = Field(..., ge=0, description="当前库存")
    minQuantity: int = Field(..., ge=0, description="最小库存")
    maxQuantity: int = Field(..., ge=0, description="最大库存")


class ProductCreate(BaseModel):
    """产品创建模式"""
    productName: str
    productCode: str
    description: Optional[str] = None
    unitPrice: float
    currentQuantity: int = 0
    minQuantity: int = 0
    maxQuantity: int = 0


class ProductUpdate(BaseModel):
    """产品更新模式"""
    productName: Optional[str] = None
    productCode: Optional[str] = None
    description: Optional[str] = None
    unitPrice: Optional[float] = None
    minQuantity: Optional[int] = None
    maxQuantity: Optional[int] = None
    isActive: Optional[bool] = None


class ProductResponse(BaseModel):
    """产品响应模式"""
    uuid: UUID
    productName: str
    productCode: str
    description: Optional[str]
    unitPrice: float
    currentQuantity: int
    minQuantity: int
    maxQuantity: int
    categoryUuid: Optional[UUID]
    supplierUuid: Optional[UUID]
    modelUuid: Optional[UUID]
    supplierName: Optional[str] = None
    modelName: Optional[str] = None
    specifications: Optional[dict] = None
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """产品列表响应模式"""
    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int