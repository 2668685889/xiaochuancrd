"""
库存相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class ChangeType(str, Enum):
    """库存变更类型"""
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"


class InventoryRecordBase(BaseModel):
    """库存记录基础模式"""
    productUuid: UUID = Field(..., description="产品UUID")
    previousQuantity: int = Field(..., ge=0, description="变更前数量")
    currentQuantity: int = Field(..., ge=0, description="变更后数量")
    changeQuantity: int = Field(..., description="变更数量")
    changeType: ChangeType = Field(..., description="变更类型")
    reason: Optional[str] = Field(None, max_length=500, description="变更原因")
    recordedBy: UUID = Field(..., description="记录人UUID")


class InventoryRecordCreate(BaseModel):
    """库存记录创建模式"""
    productUuid: UUID
    changeQuantity: int
    changeType: ChangeType
    reason: Optional[str] = None


class InventoryRecordResponse(BaseModel):
    """库存记录响应模式"""
    uuid: UUID
    productUuid: UUID
    productName: Optional[str] = None
    productCode: Optional[str] = None
    previousQuantity: int
    currentQuantity: int
    changeQuantity: int
    changeType: ChangeType
    reason: Optional[str] = None
    recordedBy: Optional[UUID] = None
    recordedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryRecordListResponse(BaseModel):
    """库存记录列表响应模式"""
    items: list[InventoryRecordResponse]
    total: int
    page: int
    size: int
    pages: int


class InventorySummary(BaseModel):
    """库存汇总信息"""
    totalProducts: int
    totalValue: float
    lowStockCount: int
    highStockCount: int
    todayIn: int
    todayOut: int
    lowStockProducts: list[dict]
    highStockProducts: list[dict]