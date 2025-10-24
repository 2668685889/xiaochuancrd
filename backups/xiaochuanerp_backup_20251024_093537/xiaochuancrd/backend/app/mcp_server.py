"""
MCP (Model Context Protocol) 服务器
为 xiaochuanERP 提供自然语言查询数据库的 MCP 接口
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.services.mcp_mysql_service import MCPMySQLService
from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取配置
# settings = get_settings()  # 删除这行重复的配置获取

# 创建数据库引擎
# 将MySQL连接URL转换为异步URL
async_database_url = settings.DATABASE_URL.replace("mysql+pymysql:", "mysql+aiomysql:")
engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 全局 MCP 服务实例
mcp_service: Optional[MCPMySQLService] = None


async def get_db():
    """获取数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global mcp_service
    
    # 启动时初始化
    logger.info("正在初始化 MCP 服务...")
    
    # 创建数据库会话
    async with AsyncSessionLocal() as session:
        # 初始化 MCP 服务
        mcp_service = MCPMySQLService(session)
        await mcp_service.initialize()
        
        if mcp_service.is_initialized:
            logger.info("MCP 服务初始化成功")
        else:
            logger.error("MCP 服务初始化失败")
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭 MCP 服务...")
    mcp_service = None


# 创建 FastAPI 应用
app = FastAPI(
    title="xiaochuanERP MCP Server",
    description="为 xiaochuanERP 提供自然语言查询数据库的 MCP 接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "xiaochuanERP MCP Server",
        "version": "1.0.0",
        "status": "running",
        "description": "为 xiaochuanERP 提供自然语言查询数据库的 MCP 接口"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP 服务未初始化")
    
    health_info = await mcp_service.health_check()
    return health_info


@app.get("/capabilities")
async def get_capabilities():
    """获取服务能力信息"""
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP 服务未初始化")
    
    capabilities = await mcp_service.get_capabilities()
    return capabilities


@app.post("/query")
async def natural_language_query(
    query_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    自然语言查询接口
    
    Args:
        query_data: 包含查询信息的字典
            - natural_language_query: 自然语言查询语句（必需）
            - session_id: 会话ID（可选）
            - workspace_id: 工作空间ID（可选）
            - enable_analysis: 是否启用数据分析（可选，默认为False）
    """
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP 服务未初始化")
    
    # 验证输入
    natural_language_query = query_data.get("natural_language_query")
    if not natural_language_query:
        raise HTTPException(
            status_code=400, 
            detail="缺少 natural_language_query 参数"
        )
    
    session_id = query_data.get("session_id")
    workspace_id = query_data.get("workspace_id", "default")
    enable_analysis = query_data.get("enable_analysis", False)  # 默认不启用分析
    
    # 更新工作空间ID
    mcp_service.workspace_id = workspace_id
    
    # 重新初始化DeepSeek服务以使用新的工作空间配置
    await mcp_service._initialize_deepseek_with_config()
    
    # 执行查询，传递enable_analysis参数
    result = await mcp_service.query(natural_language_query, session_id, enable_analysis)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "查询处理失败")
        )


@app.post("/analyze")
async def analyze_data(
    analysis_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    数据分析接口
    
    Args:
        analysis_data: 包含分析信息的字典
            - query: 分析查询语句（必需）
    """
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP 服务未初始化")
    
    # 验证输入
    query = analysis_data.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="缺少 query 参数")
    
    # 执行分析
    result = await mcp_service.analyze(query)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "分析处理失败")
        )


@app.post("/predict")
async def predict_trend(
    prediction_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    趋势预测接口
    
    Args:
        prediction_data: 包含预测信息的字典
            - data: 预测数据（必需）
    """
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP 服务未初始化")
    
    # 验证输入
    data = prediction_data.get("data")
    if not data:
        raise HTTPException(status_code=400, detail="缺少 data 参数")
    
    # 执行预测
    result = await mcp_service.predict(data)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "预测处理失败")
        )


# MCP 协议标准接口
@app.post("/mcp/initialize")
async def mcp_initialize(init_data: Dict[str, Any]):
    """MCP 协议初始化接口"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": ["mcp"],
            "sampling": {}
        },
        "serverInfo": {
            "name": "xiaochuanERP-mysql-server",
            "version": "1.0.0"
        }
    }


@app.post("/mcp/tools/call")
async def mcp_tools_call(tool_call_data: Dict[str, Any]):
    """MCP 协议工具调用接口"""
    if mcp_service is None:
        return {
            "error": "MCP 服务未初始化"
        }
    
    tool_name = tool_call_data.get("name")
    arguments = tool_call_data.get("arguments", {})
    
    try:
        if tool_name == "query":
            result = await mcp_service.query(
                arguments.get("natural_language_query"),
                arguments.get("session_id")
            )
        elif tool_name == "analyze":
            result = await mcp_service.analyze(arguments.get("query"))
        elif tool_name == "predict":
            result = await mcp_service.predict(arguments.get("data"))
        else:
            return {
                "error": f"未知工具: {tool_name}"
            }
        
        return {
            "content": result.get("content", [])
        }
        
    except Exception as e:
        logger.error(f"MCP 工具调用失败: {e}")
        return {
            "error": f"工具调用异常: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # 使用不同端口避免与主应用冲突
        log_level="info"
    )