"""
采购订单数据模型
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class PurchaseOrder(Base):
    """采购订单模型"""
    __tablename__ = "purchase_orders"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_uuid = Column(CHAR(36), ForeignKey('suppliers.uuid'), nullable=False, index=True)
    total_amount = Column(Float(precision=2), nullable=False, default=0.0)
    status = Column(Enum('PENDING', 'CONFIRMED', 'RECEIVED', 'CANCELLED'), 
                   nullable=False, default='PENDING', index=True)
    order_date = Column(DateTime, nullable=False, index=True)  # 数据库中是date类型，但DateTime兼容
    expected_delivery_date = Column(DateTime, nullable=True)  # 数据库中是date类型，但DateTime兼容
    actual_delivery_date = Column(DateTime, nullable=True)  # 数据库中是date类型，但DateTime兼容
    remark = Column(Text, nullable=True)  # 数据库中是remark字段
    created_by = Column(CHAR(36), ForeignKey('users.uuid'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    supplier = relationship("Supplier")
    creator = relationship("User", foreign_keys=[created_by])
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", 
                        cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PurchaseOrder(number='{self.order_number}')>"


class PurchaseOrderItem(Base):
    """采购订单明细模型"""
    __tablename__ = "purchase_order_items"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    purchase_order_uuid = Column(CHAR(36), ForeignKey('purchase_orders.uuid'), nullable=False, index=True)
    product_uuid = Column(CHAR(36), ForeignKey('products.uuid'), nullable=False, index=True)
    model_uuid = Column(CHAR(36), ForeignKey('product_models.uuid'), nullable=True, index=True)
    selected_specification = Column(Text, nullable=True, comment="选择的规格参数")
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float(precision=2), nullable=False, default=0.0)
    total_price = Column(Float(precision=2), nullable=False, default=0.0)
    received_quantity = Column(Integer, nullable=False, default=0)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
    product_model = relationship("ProductModel")
    
    def __repr__(self):
        return f"<PurchaseOrderItem(product='{self.product_uuid}', quantity={self.quantity})>"