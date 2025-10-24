"""
操作日志数据模型
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Enum, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    
    # 操作信息
    operation_type = Column(String(50), nullable=False, index=True, comment="操作类型：CREATE, UPDATE, DELETE, LOGIN, LOGOUT等")
    operation_module = Column(String(50), nullable=False, index=True, comment="操作模块：products, suppliers, purchase_orders等")
    operation_description = Column(Text, nullable=False, comment="操作描述")
    
    # 操作目标
    target_uuid = Column(CHAR(36), nullable=True, index=True, comment="操作目标UUID（如产品UUID、订单UUID等）")
    target_name = Column(String(200), nullable=True, comment="操作目标名称")
    
    # 操作前后数据（用于审计）
    before_data = Column(JSON, nullable=True, comment="操作前数据（JSON格式）")
    after_data = Column(JSON, nullable=True, comment="操作后数据（JSON格式）")
    
    # 操作者信息
    operator_uuid = Column(CHAR(36), nullable=False, index=True, comment="操作者UUID")
    operator_name = Column(String(100), nullable=False, comment="操作者姓名")
    operator_ip = Column(String(45), nullable=True, comment="操作者IP地址")
    
    # 操作结果
    operation_status = Column(Enum('SUCCESS', 'FAILED'), nullable=False, default='SUCCESS', index=True, comment="操作状态")
    error_message = Column(Text, nullable=True, comment="错误信息（操作失败时）")
    
    # 时间戳
    operation_time = Column(DateTime, server_default=func.now(), index=True, comment="操作时间")
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<OperationLog(type='{self.operation_type}', module='{self.operation_module}', operator='{self.operator_name}')>"
    
    def to_dict(self):
        """转换为字典格式（蛇形命名）"""
        return {
            "uuid": self.uuid,
            "operation_type": self.operation_type,
            "operation_module": self.operation_module,
            "operation_description": self.operation_description,
            "target_uuid": self.target_uuid,
            "target_name": self.target_name,
            "before_data": self.before_data,
            "after_data": self.after_data,
            "operator_uuid": self.operator_uuid,
            "operator_name": self.operator_name,
            "operator_ip": self.operator_ip,
            "operation_status": self.operation_status,
            "error_message": self.error_message,
            "operation_time": self.operation_time.isoformat() if self.operation_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }