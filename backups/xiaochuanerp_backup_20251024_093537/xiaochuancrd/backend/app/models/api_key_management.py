"""
API密钥管理模型
实现安全的API密钥存储方案
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class APIKeyModel(Base):
    """API密钥管理模型"""
    __tablename__ = "sys_api_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    workspace_uuid = Column(String(36), nullable=False, index=True, comment="工作空间UUID")
    key_name = Column(String(100), nullable=False, comment="密钥名称")
    key_type = Column(String(50), nullable=False, comment="密钥类型（deepseek, openai等）")
    env_variable = Column(String(100), nullable=False, comment="环境变量名称")
    description = Column(Text, comment="密钥描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class APIKeyReferenceModel(Base):
    """API密钥引用模型"""
    __tablename__ = "sys_api_key_references"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    workspace_uuid = Column(String(36), nullable=False, index=True, comment="工作空间UUID")
    reference_key = Column(String(100), nullable=False, comment="引用密钥标识符")
    key_type = Column(String(50), nullable=False, comment="密钥类型")
    env_variable = Column(String(100), nullable=False, comment="环境变量名称")
    description = Column(Text, comment="密钥描述")
    config_data = Column(JSON, comment="配置数据（不包含真实密钥）")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")