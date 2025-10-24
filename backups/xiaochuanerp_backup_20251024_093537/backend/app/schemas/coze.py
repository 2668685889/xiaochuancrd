"""
Coze数据上传相关模式定义
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class CozeTableInfo(BaseModel):
    """数据表信息"""
    tableName: str = Field(..., description="表名")
    displayName: str = Field(..., description="显示名称")
    description: str = Field(..., description="表描述")
    recordCount: int = Field(..., description="记录数量")
    lastUpdated: Optional[datetime] = Field(None, description="最后更新时间")
    
    class Config:
        from_attributes = True
        alias_generator = lambda s: ''.join(word.capitalize() for word in s.split('_')) if '_' in s else s


class CozeUploadFilter(BaseModel):
    """上传筛选条件"""
    field: str = Field(..., description="字段名")
    operator: str = Field(..., description="操作符: =, >, <, >=, <=, LIKE, IN")
    value: Any = Field(..., description="筛选值")


class CozeUploadRequest(BaseModel):
    """Coze数据上传请求"""
    tableName: str = Field(..., description="要上传的表名")
    cozeWorkflowId: Optional[str] = Field(None, description="Coze工作流ID（向后兼容）")
    cozeWorkflowIdInsert: Optional[str] = Field(None, description="新增操作工作流ID")
    cozeWorkflowIdUpdate: Optional[str] = Field(None, description="更新操作工作流ID")
    cozeWorkflowIdDelete: Optional[str] = Field(None, description="删除操作工作流ID")
    cozeApiKey: Optional[str] = Field(None, description="Coze API密钥")
    cozeApiUrl: str = Field(default="https://api.coze.cn", description="Coze API地址")
    filters: Optional[List[CozeUploadFilter]] = Field(None, description="筛选条件")
    batchSize: int = Field(default=100, description="批次大小")
    selectedFields: Optional[List[str]] = Field(None, description="选择的字段列表")
    configTitle: Optional[str] = Field(None, description="同步配置标题")
    
    class Config:
        from_attributes = True
        alias_generator = lambda s: ''.join(word.capitalize() for word in s.split('_')) if '_' in s else s


class CozeUploadResponse(BaseModel):
    """Coze数据上传响应"""
    uploadId: str = Field(..., description="上传任务ID")
    message: str = Field(..., description="响应消息")
    status: str = Field(..., description="任务状态: PENDING, PROCESSING, COMPLETED, FAILED")
    
    class Config:
        from_attributes = True
        alias_generator = lambda s: ''.join(word.capitalize() for word in s.split('_')) if '_' in s else s


class CozeUploadStatus(BaseModel):
    """上传任务状态"""
    uploadId: str = Field(..., description="上传任务ID")
    tableName: str = Field(..., description="表名")
    status: str = Field(..., description="任务状态")
    progress: int = Field(..., description="进度百分比")
    totalRecords: int = Field(..., description="总记录数")
    processedRecords: int = Field(..., description="已处理记录数")
    failedRecords: int = Field(..., description="失败记录数")
    startTime: Optional[datetime] = Field(None, description="开始时间")
    endTime: Optional[datetime] = Field(None, description="结束时间")
    errorMessage: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        from_attributes = True
        alias_generator = lambda s: ''.join(word.capitalize() for word in s.split('_')) if '_' in s else s


class CozeUploadHistory(BaseModel):
    """上传历史记录"""
    uploadId: str = Field(..., description="上传任务ID")
    tableName: str = Field(..., description="表名")
    cozeWorkflowId: str = Field(..., description="Coze工作流ID")
    status: str = Field(..., description="任务状态")
    totalRecords: int = Field(..., description="总记录数")
    successRecords: int = Field(..., description="成功记录数")
    failedRecords: int = Field(..., description="失败记录数")
    startTime: datetime = Field(..., description="开始时间")
    endTime: Optional[datetime] = Field(None, description="结束时间")
    operatorName: str = Field(..., description="操作者姓名")
    
    class Config:
        from_attributes = True
        alias_generator = lambda s: ''.join(word.capitalize() for word in s.split('_')) if '_' in s else s


class CozeWorkflowInfo(BaseModel):
    """Coze工作流信息"""
    workflow_id: str = Field(..., description="工作流ID")
    workflow_name: str = Field(..., description="工作流名称")
    description: str = Field(..., description="工作流描述")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class CozeApiConfig(BaseModel):
    """Coze API配置"""
    api_key: str = Field(..., description="API密钥")
    base_url: str = Field(default="https://api.coze.cn", description="API基础URL")
    timeout: int = Field(default=30, description="请求超时时间(秒)")
    
    class Config:
        from_attributes = True


class CozeSyncConfigResponse(BaseModel):
    """Coze同步配置响应模型"""
    uuid: str = Field(..., description="配置UUID")
    configTitle: str = Field(..., description="配置标题")
    tableName: str = Field(..., description="表名")
    cozeWorkflowId: Optional[str] = Field(None, description="Coze工作流ID（向后兼容）")
    cozeWorkflowIdInsert: Optional[str] = Field(None, description="新增操作工作流ID")
    cozeWorkflowIdUpdate: Optional[str] = Field(None, description="更新操作工作流ID")
    cozeWorkflowIdDelete: Optional[str] = Field(None, description="删除操作工作流ID")
    cozeApiUrl: str = Field(..., description="Coze API地址")
    cozeApiKey: Optional[str] = Field(None, description="Coze API密钥")
    syncOnInsert: bool = Field(default=True, description="新增时同步")
    syncOnUpdate: bool = Field(default=True, description="更新时同步")
    syncOnDelete: bool = Field(default=True, description="删除时同步")
    enabled: bool = Field(default=True, description="是否启用")
    selectedFields: Optional[List[str]] = Field(None, description="选择的字段列表")
    status: str = Field(default="ACTIVE", description="配置状态")
    lastSyncTime: Optional[datetime] = Field(None, description="最后同步时间")
    lastError: Optional[str] = Field(None, description="最后错误信息")
    totalSyncCount: int = Field(default=0, description="总同步次数")
    successSyncCount: int = Field(default=0, description="成功同步次数")
    failedSyncCount: int = Field(default=0, description="失败同步次数")
    insertSyncCount: int = Field(default=0, description="新增数据同步次数")
    updateSyncCount: int = Field(default=0, description="更新数据同步次数")
    deleteSyncCount: int = Field(default=0, description="删除数据同步次数")
    
    # 手动同步和自动同步统计
    manualSyncCount: int = Field(default=0, description="手动同步次数")
    autoSyncCount: int = Field(default=0, description="自动同步次数")
    lastManualSyncTime: Optional[datetime] = Field(None, description="最后手动同步时间")
    lastAutoSyncTime: Optional[datetime] = Field(None, description="最后自动同步时间")
    
    lastSyncType: Optional[str] = Field(None, description="最后同步类型: MANUAL/AUTO")
    createdAt: datetime = Field(..., description="创建时间")
    updatedAt: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        alias_generator = lambda s: ''.join(word.capitalize() for word in s.split('_')) if '_' in s else s


class CozeSyncConfigListResponse(BaseModel):
    """Coze同步配置列表响应"""
    items: List[CozeSyncConfigResponse] = Field(..., description="配置列表")
    total: int = Field(..., description="总数")
    
    class Config:
        from_attributes = True