"""
客户数据模型
"""

from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base


class Customer(Base):
    """客户模型"""
    __tablename__ = "customers"
    
    # 主键
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    customer_name = Column(String(100), nullable=False, comment="客户名称")
    customer_code = Column(String(50), nullable=False, unique=True, comment="客户编码")
    
    # 联系信息
    contact_person = Column(String(50), nullable=True, comment="联系人")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱地址")
    address = Column(Text, nullable=True, comment="地址信息")
    
    # 状态信息
    is_active = Column(Boolean, nullable=False, default=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(TIMESTAMP, nullable=True, comment="软删除时间")
    
    # 关系映射
    sales_orders = relationship("SalesOrder", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(uuid='{self.uuid}', customer_name='{self.customer_name}', customer_code='{self.customer_code}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "uuid": self.uuid,
            "customer_name": self.customer_name,
            "customer_code": self.customer_code,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }