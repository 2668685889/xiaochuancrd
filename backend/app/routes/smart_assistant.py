"""
智能助手路由 - 基于MCP的智能助手服务
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

from app.core.database import get_async_db
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.schemas.smart_assistant import (
    ChatRequest,
    ModelConfigUpdate,
    DatabaseConfigUpdate,
    SettingsSaveRequest
)
from app.models.smart_assistant import (
    ChatSessionModel, ChatMessageModel, AssistantModel, DataSourceModel, WorkspaceModel
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/smart-assistant/chat", response_model=ApiResponse[dict])
async def chat_with_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """与智能助手聊天"""
    try:
        logger.info(f"🔍 智能助手收到消息: {request.message}")  # 调试日志
        
        from app.services.mcp_service import get_mcp_service
        
        # 获取MCP服务实例
        mcp_service = get_mcp_service()
        logger.info(f"🔍 MCP服务实例获取成功: {mcp_service}")  # 调试日志
        
        # 如果服务未初始化，先进行初始化
        if not mcp_service.is_initialized:
            logger.info("🔍 MCP服务未初始化，开始初始化...")  # 调试日志
            await mcp_service.initialize()
        
        # 检查MCP服务是否就绪
        mcp_ready = await mcp_service.is_ready()
        logger.info(f"🔍 MCP服务就绪状态: {mcp_ready}")  # 调试日志
        
        if not mcp_ready:
            # 如果MCP服务未就绪，直接返回错误
            logger.error("❌ MCP服务未就绪")  # 调试日志
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP服务正在初始化中，请稍后再试"
            )
        
        logger.info("🔍 开始调用MCP服务处理消息...")  # 调试日志
        # 使用MCP服务处理聊天消息
        result = await mcp_service.process_chat_message(
            message=request.message,
            session_id=request.session_id,
            workspace_id=request.workspace_id
        )
        logger.info(f"🔍 MCP服务返回结果: {result}")  # 调试日志
        print(f"🔍 DEBUG: MCP服务返回结果: {result}")  # 调试日志
        
        if result["success"]:
            response_data = {
                "response": result["response"],
                "session_id": result["session_id"],
                "timestamp": result["timestamp"],
                "source": result["source"]
            }
            
            # 添加额外的数据字段（如果存在）
            if "data" in result and result["data"]:
                response_data["data"] = result["data"]
                print(f"🔍 DEBUG: 添加了data字段到响应中: {result['data'][:200] if isinstance(result['data'], str) else result['data']}")  # 调试日志
            if "sql" in result and result["sql"]:
                response_data["sql"] = result["sql"]
            if "chart" in result and result["chart"]:
                response_data["chart"] = result["chart"]
            
            print(f"🔍 DEBUG: 最终响应数据: {response_data}")  # 调试日志
            return ApiResponse(
                success=True,
                data=response_data,
                message="聊天响应成功"
            )
        else:
            # 如果MCP处理失败，返回错误信息
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"MCP处理失败：{result['response']}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天处理失败：{str(e)}"
        )


@router.get("/smart-assistant/data-sources", response_model=ApiResponse[dict])
async def get_data_sources(db: AsyncSession = Depends(get_async_db)):
    """获取可用的数据源列表"""
    try:
        # 使用同步方式查询数据库表信息
        from app.core.database import engine
        from sqlalchemy import text
        
        # 创建同步连接
        with engine.connect() as conn:
            # 查询information_schema获取表信息
            result = conn.execute(text("""
                SELECT TABLE_NAME, TABLE_COMMENT 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_NAME
            """))
            
            tables = []
            for row in result:
                tables.append({
                    "name": row[0],
                    "description": row[1] or ""
                })
        
        data_sources = [
            {
                "name": table["name"],
                "type": "table",
                "description": table["description"] or f"数据库表: {table['name']}"
            }
            for table in tables
        ]
        
        return ApiResponse(
            success=True,
            data={"data_sources": data_sources},
            message="获取数据源列表成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据源失败：{str(e)}"
        )


@router.post("/smart-assistant/query", response_model=ApiResponse[dict])
async def query_data(
    query: str = Query(..., description="查询语句"),
    data_source: str = Query(..., description="数据源类型"),
    workspace_id: Optional[str] = Query(None, description="工作空间ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """执行数据查询"""
    try:
        # 使用本地实现的智能助手服务
        from app.services.mcp_service import MCPService
        
        # 创建智能助手服务实例（MCPService不需要数据库连接参数）
        mcp_service = MCPService()
        
        # 执行数据查询，传递工作空间ID
        query_result = await mcp_service.process_chat_message(
            message=query,
            workspace_id=workspace_id
        )
        
        result = {
            "query": query,
            "data_source": data_source,
            "workspace_id": workspace_id,
            "result": query_result
        }
        
        return ApiResponse(
            success=True,
            data=result,
            message="数据查询成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据查询失败：{str(e)}"
        )


@router.post("/smart-assistant/upload", response_model=ApiResponse[dict])
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
    file_type: str = Query(..., description="文件类型"),
    db: AsyncSession = Depends(get_async_db)
):
    """上传文件到智能助手"""
    try:
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 获取当前时间
        from datetime import datetime
        uploaded_at = datetime.utcnow().isoformat() + "Z"
        
        # 这里可以添加文件处理逻辑，比如保存到数据库或文件系统
        # 暂时返回文件基本信息
        file_info = {
            "filename": file.filename,
            "file_type": file_type,
            "size": file_size,
            "uploaded_at": uploaded_at
        }
        
        return ApiResponse(
            success=True,
            data=file_info,
            message="文件上传成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败：{str(e)}"
        )








@router.get("/smart-assistant/history", response_model=ApiPaginatedResponse[dict])
async def get_chat_history(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    session_uuid: Optional[str] = Query(None, description="会话UUID"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取聊天历史"""
    try:
        # 查询数据库中的真实聊天历史记录
        from app.models.smart_assistant import ChatMessageModel
        
        # 构建查询条件
        query = select(ChatMessageModel)
        if session_uuid:
            query = query.where(ChatMessageModel.session_uuid == session_uuid)
        
        # 计算分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(ChatMessageModel.created_at.desc())
        
        # 执行查询
        result = await db.execute(query)
        history_records = result.scalars().all()
        
        # 获取总记录数
        count_query = select(func.count(ChatMessageModel.id))
        if session_uuid:
            count_query = count_query.where(ChatMessageModel.session_uuid == session_uuid)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # 转换数据格式
        history_items = [
            {
                "id": str(record.id),
                "session_uuid": record.session_uuid,
                "role": record.role,
                "content": record.content,
                "timestamp": record.created_at.isoformat() + "Z"
            }
            for record in history_records
        ]
        
        # 如果没有历史记录，返回空列表
        if not history_items:
            history_items = []
        
        paginated_data = PaginatedResponse(
            items=history_items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )
        
        return ApiResponse(
            success=True,
            data=paginated_data,
            message="获取聊天历史成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取聊天历史失败：{str(e)}"
        )


@router.post("/smart-assistant/settings", response_model=ApiResponse[dict])
async def save_settings(
    request: SettingsSaveRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """保存智能助手设置"""
    try:
        # 查找或创建工作空间
        workspace_id = request.workspace_id or "default"
        workspace = await db.execute(
            select(WorkspaceModel).where(WorkspaceModel.uuid == workspace_id)
        )
        workspace = workspace.scalar_one_or_none()
        
        if not workspace:
            # 创建新的工作空间
            workspace = WorkspaceModel(
                uuid=workspace_id,
                name="默认工作空间",
                description="智能助手默认工作空间",
                settings={}
            )
            db.add(workspace)
            await db.flush()
        
        # 查找或创建助手模型
        assistant = await db.execute(
            select(AssistantModel).where(AssistantModel.workspace_uuid == workspace_id)
        )
        assistant = assistant.scalar_one_or_none()
        
        if not assistant:
            # 创建新的助手模型
            assistant = AssistantModel(
                uuid=str(uuid.uuid4()),
                workspace_uuid=workspace_id,
                name="智能助手",
                description="基于MCP的智能助手",
                model_type=request.ai_model_config.model_id or "deepseek-chat",  # 设置模型类型
                model_config={}
            )
            db.add(assistant)
            await db.flush()
        
        # 更新模型配置
        model_config = {
            "model_id": request.ai_model_config.model_id,
            "api_key": request.ai_model_config.api_key,
            "api_domain": request.ai_model_config.api_domain,
            "base_url": request.ai_model_config.base_url,
            "prompt": request.ai_model_config.prompt
        }
        assistant.model_config = model_config
        
        # 查找或创建数据源
        data_source = await db.execute(
            select(DataSourceModel).where(DataSourceModel.workspace_uuid == workspace_id)
        )
        data_source = data_source.scalar_one_or_none()
        
        if not data_source:
            # 创建新的数据源
            data_source = DataSourceModel(
                uuid=str(uuid.uuid4()),
                workspace_uuid=workspace_id,
                name="主数据库",
                type="mysql",
                connection_config={}
            )
            db.add(data_source)
            await db.flush()
        
        # 更新数据库配置
        db_config = {
            "host": request.database_config.host,
            "port": request.database_config.port,
            "database": request.database_config.database,
            "username": request.database_config.username,
            "password": request.database_config.password,
            "schema_name": request.database_config.schema_name
        }
        data_source.connection_config = db_config
        
        # 更新工作空间设置
        workspace.settings = {
            "last_updated": datetime.utcnow().isoformat(),
            "is_configured": True
        }
        
        # 提交事务
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "message": "设置保存成功",
                "workspace_id": workspace_id,
                "last_updated": workspace.settings["last_updated"]
            },
            message="设置保存成功"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存设置失败：{str(e)}"
        )


@router.get("/smart-assistant/settings", response_model=ApiResponse[dict])
async def get_settings(
    workspace_id: Optional[str] = Query("default", description="工作空间ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取智能助手设置"""
    try:
        # 查找工作空间
        workspace = await db.execute(
            select(WorkspaceModel).where(WorkspaceModel.uuid == workspace_id)
        )
        workspace = workspace.scalar_one_or_none()
        
        if not workspace:
            return ApiResponse(
                success=True,
                data={
                    "is_configured": False,
                    "message": "未找到工作空间设置"
                },
                message="未找到工作空间设置"
            )
        
        # 查找助手模型
        assistant = await db.execute(
            select(AssistantModel).where(AssistantModel.workspace_uuid == workspace_id)
        )
        assistant = assistant.scalar_one_or_none()
        
        # 查找数据源
        data_source = await db.execute(
            select(DataSourceModel).where(DataSourceModel.workspace_uuid == workspace_id)
        )
        data_source = data_source.scalar_one_or_none()
        
        if not assistant or not data_source:
            return ApiResponse(
                success=True,
                data={
                    "is_configured": False,
                    "message": "设置未配置"
                },
                message="设置未配置"
            )
        
        # 构建响应数据
        model_config = assistant.model_config or {}
        db_config = data_source.connection_config or {}
        
        settings_data = {
            "ai_model_config": {
                "model_id": model_config.get("model_id", ""),
                "api_key": model_config.get("api_key", ""),
                "api_domain": model_config.get("api_domain", ""),
                "base_url": model_config.get("base_url", ""),
                "prompt": model_config.get("prompt", ""),
                "is_configured": bool(model_config.get("api_key"))
            },
            "database_config": {
                "host": db_config.get("host", ""),
                "port": db_config.get("port", 3306),
                "database": db_config.get("database", ""),
                "username": db_config.get("username", ""),
                "password": db_config.get("password", ""),
                "schema_name": db_config.get("schema_name", "")
            },
            "is_configured": workspace.settings.get("is_configured", False) if workspace.settings else False,
            "last_updated": workspace.settings.get("last_updated", "") if workspace.settings else ""
        }
        
        return ApiResponse(
            success=True,
            data=settings_data,
            message="获取设置成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设置失败：{str(e)}"
        )