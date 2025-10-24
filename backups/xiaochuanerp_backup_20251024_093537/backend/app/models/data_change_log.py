"""数据变化日志模型"""
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class DataChangeLog(Base):
    """数据变化日志表"""
    __tablename__ = "data_change_logs"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    table_name = Column(String(100), nullable=False, comment="表名")
    record_uuid = Column(CHAR(36), nullable=False, comment="记录UUID")
    operation_type = Column(String(20), nullable=False, comment="操作类型: INSERT, UPDATE, DELETE")
    change_data = Column(JSON, comment="变化数据")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    processed = Column(Integer, default=0, comment="是否已处理: 0-未处理, 1-已处理")
    processed_at = Column(DateTime, nullable=True, comment="处理时间")
    
    def __repr__(self):
        return f"<DataChangeLog(table_name={self.table_name}, operation_type={self.operation_type})>"