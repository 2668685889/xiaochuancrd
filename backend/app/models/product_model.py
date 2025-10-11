"""
产品型号数据模型
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class ProductModel(Base):
    """产品型号模型"""
    __tablename__ = "product_models"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    model_name = Column(String(100), nullable=False, index=True)
    model_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_uuid = Column(CHAR(36), ForeignKey('product_categories.uuid'), nullable=True, index=True)
    specifications = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    # 关系
    products = relationship("Product", back_populates="product_model", lazy="select")
    category_rel = relationship("ProductCategory", back_populates="product_models", lazy="select")
    
    def __repr__(self):
        return f"<ProductModel(name='{self.model_name}', code='{self.model_code}')>"