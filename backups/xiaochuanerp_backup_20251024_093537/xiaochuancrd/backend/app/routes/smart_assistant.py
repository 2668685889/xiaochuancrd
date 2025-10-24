"""
智能助手路由 - 基于MCP的智能助手服务
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional, List, Dict, Any
import json
import uuid
import time
import random
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
        
        # 保存用户消息到数据库
        await save_message_to_db(db, request.session_id, "user", request.message)
        
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
            response_content = result["response"]
            
            # 保存助手回复到数据库
            await save_message_to_db(db, request.session_id, "assistant", response_content)
            
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
            
            # 处理分析结果
            if "analysis" in result and result["analysis"]:
                response_data["analysis"] = result["analysis"]
                print(f"🔍 DEBUG: 添加了analysis字段到响应中: {result['analysis'][:200] if isinstance(result['analysis'], str) else result['analysis']}")  # 调试日志
            
            # 处理原始数据
            if "raw_data" in result and result["raw_data"]:
                response_data["raw_data"] = result["raw_data"]
                print(f"🔍 DEBUG: 添加了raw_data字段到响应中: {result['raw_data'][:200] if isinstance(result['raw_data'], str) else result['raw_data']}")  # 调试日志
            
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


async def save_message_to_db(db: AsyncSession, session_id: str, role: str, content: str):
    """保存消息到数据库"""
    try:
        # 查找或创建会话
        session = await db.execute(
            select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
        )
        session = session.scalar_one_or_none()
        
        if not session:
            # 创建新会话
            session_uuid = str(uuid.uuid4())
            session = ChatSessionModel(
                uuid=session_uuid,
                session_id=session_id,
                title=f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                assistant_uuid="default",  # 默认助手UUID
                session_metadata={},
                is_active=True
            )
            db.add(session)
            await db.flush()
            session_uuid = session.uuid
        else:
            session_uuid = session.uuid
        
        # 保存消息
        message_uuid = str(uuid.uuid4())
        message = ChatMessageModel(
            uuid=message_uuid,
            session_uuid=session_uuid,
            role=role,
            content=content,
            message_metadata={},
            is_processed=True
        )
        db.add(message)
        await db.commit()
        
        logger.info(f"✅ 消息已保存到数据库: session_id={session_id}, role={role}")
    except Exception as e:
        logger.error(f"❌ 保存消息到数据库失败: {str(e)}")
        # 不抛出异常，避免影响主要功能


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








@router.get("/smart-assistant/sessions", response_model=ApiResponse[List[dict]])
async def get_chat_sessions(db: AsyncSession = Depends(get_async_db)):
    """获取所有聊天会话"""
    try:
        # 查询所有会话
        sessions = await db.execute(
            select(ChatSessionModel).order_by(ChatSessionModel.created_at.desc())
        )
        sessions = sessions.scalars().all()
        
        # 转换为字典格式
        session_list = []
        for session in sessions:
            # 获取会话的消息数量
            message_count = await db.execute(
                select(func.count(ChatMessageModel.uuid)).where(
                    ChatMessageModel.session_uuid == session.uuid
                )
            )
            message_count = message_count.scalar()
            
            session_list.append({
                "uuid": session.uuid,
                "session_id": session.session_id,
                "title": session.title,
                "message_count": message_count,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            })
        
        return ApiResponse(
            success=True,
            data=session_list,
            message="获取会话列表成功"
        )
    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败：{str(e)}"
        )


@router.get("/smart-assistant/sessions/{session_id}/messages", response_model=ApiResponse[List[dict]])
async def get_session_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """获取指定会话的消息"""
    try:
        # 查找会话
        session = await db.execute(
            select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
        )
        session = session.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {session_id} 不存在"
            )
        
        # 分页查询消息
        offset = (page - 1) * page_size
        messages = await db.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.session_uuid == session.uuid)
            .order_by(ChatMessageModel.created_at)
            .offset(offset)
            .limit(page_size)
        )
        messages = messages.scalars().all()
        
        # 转换为字典格式
        message_list = []
        for message in messages:
            message_list.append({
                "uuid": message.uuid,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None
            })
        
        return ApiResponse(
            success=True,
            data=message_list,
            message="获取会话消息成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话消息失败：{str(e)}"
        )


@router.post("/smart-assistant/sessions", response_model=ApiResponse[dict])
async def create_session(
    title: str = Query(..., description="会话标题"),
    db: AsyncSession = Depends(get_async_db)
):
    """创建新的聊天会话"""
    try:
        # 生成会话ID
        session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        session_uuid = str(uuid.uuid4())
        
        # 创建会话
        session = ChatSessionModel(
            uuid=session_uuid,
            session_id=session_id,
            title=title,
            assistant_uuid="default",  # 默认助手UUID
            session_metadata={},
            is_active=True
        )
        db.add(session)
        await db.commit()
        
        # 刷新对象以获取数据库生成的值
        await db.refresh(session)
        
        return ApiResponse(
            success=True,
            data={
                "uuid": session.uuid,
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None
            },
            message="创建会话成功"
        )
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败：{str(e)}"
        )


@router.delete("/smart-assistant/sessions/{session_id}", response_model=ApiResponse[dict])
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """删除聊天会话"""
    try:
        # 查找会话
        session = await db.execute(
            select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
        )
        session = session.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {session_id} 不存在"
            )
        
        # 删除会话相关的消息
        await db.execute(
            delete(ChatMessageModel).where(
                ChatMessageModel.session_uuid == session.uuid
            )
        )
        
        # 删除会话
        await db.delete(session)
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={"session_id": session_id},
            message="删除会话成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话失败：{str(e)}"
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
        
        # 如果有分析模型配置，添加到model_config中
        if request.analysis_model_config:
            model_config["analysis_config"] = {
                "model": request.analysis_model_config.model_id,
                "api_key": request.analysis_model_config.api_key,
                "api_domain": request.analysis_model_config.api_domain,
                "base_url": request.analysis_model_config.base_url,
                "system_prompt": request.analysis_model_config.prompt or _get_default_analysis_prompt(),
                "temperature": 0.3,
                "max_tokens": 1500
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
        
        # 添加分析模型配置（如果存在）
        if "analysis_config" in model_config:
            analysis_config = model_config["analysis_config"]
            settings_data["analysis_model_config"] = {
                "model_id": analysis_config.get("model", ""),
                "api_key": analysis_config.get("api_key", ""),
                "api_domain": analysis_config.get("api_domain", ""),
                "base_url": analysis_config.get("base_url", ""),
                "prompt": analysis_config.get("system_prompt", ""),
                "is_configured": bool(analysis_config.get("api_key"))
            }
        else:
            # 如果没有分析模型配置，添加默认值
            settings_data["analysis_model_config"] = {
                "model_id": "",
                "api_key": "",
                "api_domain": "",
                "base_url": "",
                "prompt": "",
                "is_configured": False
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


def _get_default_analysis_prompt() -> str:
    """获取默认的分析提示词"""
    return """
    你是一个专业的数据分析助手，专门负责对ERP系统数据进行深度分析、挖掘业务洞察和提供决策建议。
    
    请按照以下步骤进行数据分析：
    1. 数据理解：解析数据结构，识别数据类型和来源
    2. 质量评估：评估数据完整性、准确性和时效性
    3. 指标计算：计算关键业务指标和KPI
    4. 趋势分析：识别数据趋势、模式和异常
    5. 关联分析：探索不同数据维度间的关联性
    6. 洞察提取：从数据中提取有价值的业务洞察
    7. 建议生成：基于分析结果提供具体可行的建议
    
    请按以下结构提供分析结果：
    1. 数据概览：简要描述数据来源、时间范围和基本特征
    2. 关键指标：列出最重要的业务指标及其数值
    3. 深度分析：
       - 趋势分析：数据变化趋势和模式
       - 对比分析：不同维度间的对比
       - 异常分析：异常值和特殊现象
    4. 业务洞察：从数据中提取的关键洞察
    5. 行动建议：基于分析结果的具体建议
    6. 局限性说明：分析的局限性和注意事项
    """