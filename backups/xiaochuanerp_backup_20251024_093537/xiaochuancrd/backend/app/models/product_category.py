"""
产品分类数据模型
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class ProductCategory(Base):
    """产品分类模型"""
    __tablename__ = "product_categories"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    category_name = Column(String(100), nullable=False, index=True)
    category_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_uuid = Column(CHAR(36), ForeignKey('product_categories.uuid'), nullable=True, index=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    # 关系
    parent = relationship("ProductCategory", remote_side=[uuid], back_populates="children", lazy="select")
    children = relationship("ProductCategory", back_populates="parent", lazy="select")
    product_models = relationship("ProductModel", back_populates="category_rel", lazy="select")
    products = relationship("Product", back_populates="category_rel", lazy="select")
    
    def __repr__(self):
        return f"<ProductCategory(name='{self.category_name}', code='{self.category_code}')>"