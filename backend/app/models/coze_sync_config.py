"""
Coze同步配置数据模型
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class CozeSyncConfig(Base):
    """Coze同步配置模型"""
    __tablename__ = "coze_sync_configs"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    
    # 配置基本信息
    config_title = Column(String(200), nullable=False, comment="配置标题")
    table_name = Column(String(100), nullable=False, index=True, comment="同步的数据表名")
    
    # Coze API配置
    coze_workflow_id = Column(String(100), nullable=True, comment="Coze工作流ID（向后兼容）")
    coze_workflow_id_insert = Column(String(100), nullable=True, comment="新增操作工作流ID")
    coze_workflow_id_update = Column(String(100), nullable=True, comment="更新操作工作流ID")
    coze_workflow_id_delete = Column(String(100), nullable=True, comment="删除操作工作流ID")
    coze_api_url = Column(String(500), nullable=False, default="https://api.coze.cn", comment="Coze API地址")
    coze_api_key = Column(Text, nullable=True, comment="Coze API密钥")
    
    # 同步设置
    sync_on_insert = Column(Boolean, nullable=False, default=True, comment="是否同步插入操作")
    sync_on_update = Column(Boolean, nullable=False, default=True, comment="是否同步更新操作")
    sync_on_delete = Column(Boolean, nullable=False, default=False, comment="是否同步删除操作")
    enabled = Column(Boolean, nullable=False, default=True, comment="是否启用同步")
    
    # 字段选择
    selected_fields = Column(JSON, nullable=True, comment="选择的字段列表")
    
    # 状态信息
    status = Column(String(20), nullable=False, default="ACTIVE", comment="同步状态：ACTIVE, PAUSED, ERROR")
    last_sync_time = Column(DateTime, nullable=True, comment="最后同步时间")
    last_error = Column(Text, nullable=True, comment="最后错误信息")
    
    # 同步统计信息
    total_sync_count = Column(Integer, nullable=False, default=0, comment="总同步次数")
    success_sync_count = Column(Integer, nullable=False, default=0, comment="成功同步次数")
    failed_sync_count = Column(Integer, nullable=False, default=0, comment="失败同步次数")
    insert_sync_count = Column(Integer, nullable=False, default=0, comment="新增数据同步次数")
    update_sync_count = Column(Integer, nullable=False, default=0, comment="更新数据同步次数")
    delete_sync_count = Column(Integer, nullable=False, default=0, comment="删除数据同步次数")
    
    # 手动同步和自动同步统计
    manual_sync_count = Column(Integer, nullable=False, default=0, comment="手动同步次数")
    auto_sync_count = Column(Integer, nullable=False, default=0, comment="自动同步次数")
    last_manual_sync_time = Column(DateTime, nullable=True, comment="最后手动同步时间")
    last_auto_sync_time = Column(DateTime, nullable=True, comment="最后自动同步时间")
    
    last_sync_type = Column(String(20), nullable=True, comment="最后同步类型：MANUAL, AUTO_INSERT, AUTO_UPDATE, AUTO_DELETE")
    
    # 创建者信息
    created_by = Column(CHAR(36), ForeignKey('users.uuid'), nullable=True, index=True, comment="创建者UUID")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CozeSyncConfig(title='{self.config_title}', table='{self.table_name}')>"