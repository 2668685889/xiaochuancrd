"""
采购订单相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class PurchaseOrderItemBase(BaseModel):
    """采购订单明细基础模式"""
    productUuid: str = Field(..., description="产品UUID")
    modelUuid: Optional[str] = Field(None, description="产品型号UUID")
    selectedSpecification: Optional[str] = Field(None, description="选择的规格参数")
    quantity: int = Field(..., ge=1, description="采购数量")
    unitPrice: float = Field(..., ge=0, description="采购单价")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """采购订单明细创建模式"""
    pass


class PurchaseOrderItemUpdate(BaseModel):
    """采购订单明细更新模式"""
    quantity: Optional[int] = None
    unitPrice: Optional[float] = None
    receivedQuantity: Optional[int] = None
    remark: Optional[str] = None


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    """采购订单明细响应模式"""
    uuid: UUID
    purchaseOrderUuid: UUID
    productName: str = Field(..., description="商品名称")
    modelName: Optional[str] = Field(None, description="产品型号名称")
    selectedSpecification: Optional[str] = Field(None, description="选择的规格参数")
    totalPrice: float
    receivedQuantity: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    """采购订单基础模式"""
    supplierUuid: str = Field(..., description="供应商UUID")
    orderDate: datetime = Field(..., description="订单日期")
    expectedDeliveryDate: Optional[datetime] = Field(None, description="预计交货日期")
    remark: Optional[str] = Field(None, max_length=1000, description="备注")


class PurchaseOrderCreate(PurchaseOrderBase):
    """采购订单创建模式"""
    items: List[PurchaseOrderItemCreate] = Field(..., min_items=1, description="订单明细")


class PurchaseOrderUpdate(BaseModel):
    """采购订单更新模式"""
    supplierUuid: Optional[str] = None
    orderDate: Optional[datetime] = None
    expectedDeliveryDate: Optional[datetime] = None
    actualDeliveryDate: Optional[datetime] = None
    remark: Optional[str] = None
    items: Optional[List[PurchaseOrderItemCreate]] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """采购订单响应模式"""
    uuid: UUID
    orderNumber: str
    supplierName: str = Field(..., description="供应商名称")
    totalAmount: float
    actualDeliveryDate: Optional[datetime]
    createdBy: UUID
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse]

    class Config:
        from_attributes = True


class PurchaseOrderListResponse(BaseModel):
    """采购订单列表响应模式"""
    items: List[PurchaseOrderResponse]
    total: int
    page: int
    size: int
    pages: int