"""
智能助手数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AssistantInfo(BaseModel):
    """助手信息"""
    name: str = Field(..., description="助手名称")
    description: str = Field(..., description="助手描述")
    version: str = Field(..., description="版本号")
    capabilities: List[str] = Field(..., description="功能列表")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息角色(user/assistant)")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(None, description="时间戳")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[List[ChatMessage]] = Field(None, description="上下文消息")
    workspace_id: Optional[str] = Field(None, description="工作空间ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="助手回复")
    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(..., description="响应时间")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


class DataSourceInfo(BaseModel):
    """数据源信息"""
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    description: str = Field(..., description="数据源描述")
    is_available: bool = Field(True, description="是否可用")


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询语句")
    data_source: str = Field(..., description="数据源类型")
    session_id: Optional[str] = Field(None, description="会话ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="查询参数")


class QueryResponse(BaseModel):
    """查询响应"""
    query: str = Field(..., description="原始查询")
    data_source: str = Field(..., description="数据源类型")
    result: Dict[str, Any] = Field(..., description="查询结果")
    execution_time: Optional[int] = Field(None, description="执行时间(毫秒)")
    session_id: Optional[str] = Field(None, description="会话ID")


class FileUploadRequest(BaseModel):
    """文件上传请求"""
    file_type: str = Field(..., description="文件类型")
    description: Optional[str] = Field(None, description="文件描述")


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小")
    uploaded_at: datetime = Field(..., description="上传时间")
    file_id: str = Field(..., description="文件ID")


class ChatHistoryItem(BaseModel):
    """聊天历史项"""
    id: str = Field(..., description="消息ID")
    session_id: str = Field(..., description="会话ID")
    user_message: str = Field(..., description="用户消息")
    assistant_response: str = Field(..., description="助手回复")
    timestamp: datetime = Field(..., description="时间戳")
    data_source: Optional[str] = Field(None, description="数据源类型")


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str = Field(..., description="会话ID")
    title: str = Field(..., description="会话标题")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    message_count: int = Field(..., description="消息数量")


class AssistantConfig(BaseModel):
    """助手配置"""
    model_type: str = Field(..., description="模型类型")
    temperature: float = Field(0.7, description="温度参数")
    max_tokens: int = Field(2048, description="最大token数")
    system_prompt: Optional[str] = Field(None, description="系统提示")
    data_sources: List[str] = Field([], description="数据源列表")


class AssistantCreate(BaseModel):
    """创建助手请求"""
    name: str = Field(..., description="助手名称")
    description: str = Field(..., description="助手描述")
    model_type: str = Field(..., description="模型类型")
    config: AssistantConfig = Field(..., description="助手配置")


class AssistantUpdate(BaseModel):
    """更新助手请求"""
    name: Optional[str] = Field(None, description="助手名称")
    description: Optional[str] = Field(None, description="助手描述")
    config: Optional[AssistantConfig] = Field(None, description="助手配置")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ModelConfigUpdate(BaseModel):
    """模型配置更新请求"""
    model_id: str = Field(..., description="模型ID")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_domain: Optional[str] = Field(None, description="API域名")
    base_url: Optional[str] = Field(None, description="基础URL")
    prompt: Optional[str] = Field(None, description="模型提示词")


class ModelConfigResponse(BaseModel):
    """模型配置响应"""
    model_id: str = Field(..., description="模型ID")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_domain: Optional[str] = Field(None, description="API域名")
    base_url: Optional[str] = Field(None, description="基础URL")
    is_configured: bool = Field(..., description="是否已配置")


class DatabaseConfigUpdate(BaseModel):
    """数据库配置更新请求"""
    host: str = Field(..., description="数据库主机")
    port: int = Field(..., description="数据库端口")
    database: str = Field(..., description="数据库名称")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    schema_name: Optional[str] = Field(None, description="模式名称")


class SettingsSaveRequest(BaseModel):
    """设置保存请求"""
    ai_model_config: ModelConfigUpdate
    analysis_model_config: Optional[ModelConfigUpdate] = Field(None, description="分析模型配置")
    database_config: DatabaseConfigUpdate
    workspace_id: Optional[str] = Field(None, description="工作空间ID")


class SettingsResponse(BaseModel):
    """设置响应"""
    ai_model_config: ModelConfigResponse
    analysis_model_config: Optional[ModelConfigResponse] = Field(None, description="分析模型配置")
    database_config: DatabaseConfigUpdate
    is_configured: bool = Field(..., description="是否已配置")
    last_updated: datetime = Field(..., description="最后更新时间")