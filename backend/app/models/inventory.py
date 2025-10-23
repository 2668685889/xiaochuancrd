"""
库存记录数据模型
"""

from sqlalchemy import Column, Integer, Float, DateTime, Text, ForeignKey, Enum, Date
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class InventoryRecord(Base):
    """库存记录模型"""
    __tablename__ = "inventory_records"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    product_uuid = Column(CHAR(36), ForeignKey('products.uuid'), nullable=False, index=True)
    change_type = Column(Enum('IN', 'OUT', 'ADJUST'), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    current_quantity = Column(Integer, nullable=False)
    remark = Column(Text, nullable=True)
    record_date = Column(Date, nullable=False)
    created_by = Column(CHAR(36), ForeignKey('users.uuid'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    product = relationship("Product", back_populates="inventory_records")
    user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<InventoryRecord(product='{self.product_uuid}', change={self.quantity_change})>"