"""
销售订单相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class SalesOrderItemBase(BaseModel):
    """销售订单明细基础模式"""
    productUuid: UUID = Field(..., description="产品UUID")
    quantity: int = Field(..., ge=1, description="销售数量")
    unitPrice: float = Field(..., ge=0, description="销售单价")
    notes: Optional[str] = Field(None, max_length=500, description="备注")


class SalesOrderItemCreate(SalesOrderItemBase):
    """销售订单明细创建模式"""
    pass


class SalesOrderItemUpdate(BaseModel):
    """销售订单明细更新模式"""
    quantity: Optional[int] = None
    unitPrice: Optional[float] = None
    shippedQuantity: Optional[int] = None
    notes: Optional[str] = None


class SalesOrderItemResponse(SalesOrderItemBase):
    """销售订单明细响应模式"""
    uuid: UUID
    salesOrderUuid: UUID
    productName: Optional[str] = Field(None, description="商品名称")
    totalPrice: float
    shippedQuantity: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    """销售订单基础模式"""
    customerUuid: UUID = Field(..., description="客户UUID")
    orderDate: str = Field(..., description="订单日期")
    deliveryDate: Optional[str] = Field(None, description="交货日期")
    shippingAddress: Optional[str] = Field(None, max_length=500, description="收货地址")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")


class SalesOrderCreate(SalesOrderBase):
    """销售订单创建模式"""
    items: List[SalesOrderItemCreate] = Field(..., min_items=1, description="订单明细")


class SalesOrderUpdate(BaseModel):
    """销售订单更新模式"""
    customerUuid: Optional[UUID] = None
    customerName: Optional[str] = None
    customerPhone: Optional[str] = None
    customerAddress: Optional[str] = None
    shippingAddress: Optional[str] = Field(None, max_length=500, description="收货地址")
    expectedDeliveryDate: Optional[datetime] = None
    actualDeliveryDate: Optional[datetime] = None
    status: Optional[str] = None
    paymentStatus: Optional[str] = None
    remark: Optional[str] = None


class SalesOrderResponse(SalesOrderBase):
    """销售订单响应模式"""
    uuid: UUID
    orderNumber: str
    customerName: Optional[str] = Field(None, description="客户名称")
    customerPhone: Optional[str] = Field(None, description="客户电话")
    customerAddress: Optional[str] = Field(None, description="客户地址")
    totalAmount: float
    status: str
    paymentStatus: Optional[str] = None
    actualDeliveryDate: Optional[str] = None
    createdBy: UUID
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    items: List[SalesOrderItemResponse]

    class Config:
        from_attributes = True


class SalesOrderListResponse(BaseModel):
    """销售订单列表响应模式"""
    items: List[SalesOrderResponse]
    total: int
    page: int
    size: int
    pages: int