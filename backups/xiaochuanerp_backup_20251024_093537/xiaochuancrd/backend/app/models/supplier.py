"""
供应商数据模型
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class Supplier(Base):
    """供应商模型"""
    __tablename__ = "suppliers"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    supplier_name = Column(String(100), nullable=False, index=True)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)
    contact_person = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    # 关系
    products = relationship("Product", back_populates="supplier", lazy="select")
    
    def __repr__(self):
        return f"<Supplier(name='{self.supplier_name}', code='{self.supplier_code}')>"