"""
智能助手数据库模型
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AssistantModel(Base):
    """助手模型"""
    __tablename__ = "sys_assistant"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    workspace_uuid = Column(String(36), nullable=False, index=True, comment="工作空间UUID")
    name = Column(String(100), nullable=False, comment="助手名称")
    description = Column(Text, comment="助手描述")
    model_type = Column(String(50), nullable=False, comment="模型类型")
    model_config = Column(JSON, comment="模型配置")
    capabilities = Column(JSON, comment="功能列表")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ChatSessionModel(Base):
    """聊天会话模型"""
    __tablename__ = "sys_chat_session"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True, comment="会话ID")
    user_id = Column(String(36), nullable=True, index=True, comment="用户ID")
    title = Column(String(200), comment="会话标题")
    assistant_uuid = Column(String(36), nullable=False, index=True, comment="助手UUID")
    session_metadata = Column(JSON, comment="会话元数据")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ChatMessageModel(Base):
    """聊天消息模型"""
    __tablename__ = "sys_chat_message"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    session_uuid = Column(String(36), nullable=False, index=True, comment="会话UUID")
    role = Column(String(20), nullable=False, comment="消息角色(user/assistant)")
    content = Column(Text, nullable=False, comment="消息内容")
    message_metadata = Column(JSON, comment="消息元数据")
    is_processed = Column(Boolean, default=False, comment="是否已处理")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class DataSourceModel(Base):
    """数据源模型"""
    __tablename__ = "sys_data_source"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    workspace_uuid = Column(String(36), nullable=False, index=True, comment="工作空间UUID")
    name = Column(String(100), nullable=False, comment="数据源名称")
    type = Column(String(50), nullable=False, comment="数据源类型")
    description = Column(Text, comment="数据源描述")
    connection_config = Column(JSON, comment="连接配置")
    schema_info = Column(JSON, comment="数据模式信息")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class QueryHistoryModel(Base):
    """查询历史模型"""
    __tablename__ = "sys_query_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    session_uuid = Column(String(36), nullable=False, index=True, comment="会话UUID")
    query_text = Column(Text, nullable=False, comment="查询文本")
    data_source_uuid = Column(String(36), nullable=False, index=True, comment="数据源UUID")
    result_data = Column(JSON, comment="查询结果数据")
    execution_time = Column(Integer, comment="执行时间(毫秒)")
    is_success = Column(Boolean, default=True, comment="是否成功")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class FileUploadModel(Base):
    """文件上传模型"""
    __tablename__ = "sys_file_upload"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False, comment="文件名")
    file_type = Column(String(50), nullable=False, comment="文件类型")
    file_size = Column(Integer, comment="文件大小(字节)")
    storage_path = Column(String(500), comment="存储路径")
    file_metadata = Column(JSON, comment="文件元数据")
    is_processed = Column(Boolean, default=False, comment="是否已处理")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class WorkspaceModel(Base):
    """工作空间模型"""
    __tablename__ = "sys_workspace"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, comment="工作空间名称")
    description = Column(Text, comment="工作空间描述")
    settings = Column(JSON, comment="工作空间设置")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")