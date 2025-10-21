#!/usr/bin/env python3
"""
简化的 MCP 服务器
提供基本的 MCP 协议接口，不依赖数据库连接
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPMySQLService:
    """简化的 MCP MySQL 服务"""
    
    def __init__(self):
        self.is_initialized = True
        
    async def initialize(self):
        """初始化服务"""
        logger.info("简化的 MCP 服务初始化完成")
        return True
        
    async def health_check(self):
        """健康检查"""
        return {
            "status": "healthy",
            "database_connected": False,
            "ai_service_ready": False,
            "message": "简化模式运行中，数据库连接未配置"
        }
        
    async def get_capabilities(self):
        """获取服务能力"""
        return {
            "capabilities": [
                {
                    "name": "query_database",
                    "description": "查询数据库（简化模式）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL 查询语句"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "analyze_data",
                    "description": "数据分析（简化模式）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "分析查询"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ],
            "database_info": {
                "type": "MySQL",
                "database": "xiaochuanERP",
                "tables": ["customers", "products", "orders", "inventory"]
            },
            "ai_service_info": {
                "provider": "DeepSeek",
                "model": "deepseek-chat"
            }
        }
        
    async def query(self, natural_language_query: str, session_id: Optional[str] = None):
        """自然语言查询"""
        return {
            "success": True,
            "content": [
                {
                    "type": "text",
                    "text": f"简化模式：收到查询 '{natural_language_query}'。请配置数据库连接和 AI 服务以启用完整功能。"
                }
            ],
            "session_id": session_id or "simplified-session"
        }
        
    async def analyze(self, query: str):
        """数据分析"""
        return {
            "success": True,
            "content": [
                {
                    "type": "text",
                    "text": f"简化模式：收到分析请求 '{query}'。请配置数据库连接和 AI 服务以启用完整功能。"
                }
            ]
        }
        
    async def predict(self, data: Dict[str, Any]):
        """趋势预测"""
        return {
            "success": True,
            "content": [
                {
                    "type": "text",
                    "text": f"简化模式：收到预测请求。请配置数据库连接和 AI 服务以启用完整功能。"
                }
            ]
        }


# 全局服务实例
mcp_service: Optional[SimpleMCPMySQLService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global mcp_service
    
    # 启动时初始化
    logger.info("正在初始化简化的 MCP 服务...")
    
    # 初始化 MCP 服务
    mcp_service = SimpleMCPMySQLService()
    await mcp_service.initialize()
    
    logger.info("简化的 MCP 服务初始化成功")
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭 MCP 服务...")
    mcp_service = None


# 创建 FastAPI 应用
app = FastAPI(
    title="xiaochuanERP MCP Server (简化模式)",
    description="为 xiaochuanERP 提供自然语言查询数据库的 MCP 接口（简化模式）",
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
        "service": "xiaochuanERP MCP Server (简化模式)",
        "version": "1.0.0",
        "status": "running",
        "description": "为 xiaochuanERP 提供自然语言查询数据库的 MCP 接口（简化模式）",
        "mode": "simplified",
        "message": "数据库连接未配置，运行在简化模式"
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
async def natural_language_query(query_data: Dict[str, Any]):
    """
    自然语言查询接口
    
    Args:
        query_data: 包含查询信息的字典
            - natural_language_query: 自然语言查询语句（必需）
            - session_id: 会话ID（可选）
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
    
    # 执行查询
    result = await mcp_service.query(natural_language_query, session_id)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "查询处理失败")
        )


@app.post("/analyze")
async def analyze_data(analysis_data: Dict[str, Any]):
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
async def predict_trend(prediction_data: Dict[str, Any]):
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
async def mcp_initialize():
    """MCP 协议初始化"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": True
            }
        },
        "serverInfo": {
            "name": "xiaochuanERP MCP Server",
            "version": "1.0.0"
        }
    }


@app.post("/mcp/tools/call")
async def mcp_tools_call(tool_call: Dict[str, Any]):
    """MCP 工具调用"""
    tool_name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})
    
    if tool_name == "query_database":
        query = arguments.get("query", "")
        return {
            "name": tool_name,
            "content": [
                {
                    "type": "text",
                    "text": f"简化模式：收到数据库查询 '{query}'。请配置数据库连接以启用完整功能。"
                }
            ]
        }
    elif tool_name == "analyze_data":
        query = arguments.get("query", "")
        return {
            "name": tool_name,
            "content": [
                {
                    "type": "text",
                    "text": f"简化模式：收到数据分析请求 '{query}'。请配置数据库连接以启用完整功能。"
                }
            ]
        }
    else:
        raise HTTPException(status_code=400, detail=f"未知工具: {tool_name}")


if __name__ == "__main__":
    import uvicorn
    
    print("启动简化的 MCP 服务器...")
    print("服务地址: http://localhost:8001")
    print("模式: 简化模式（数据库连接未配置）")
    print("按 Ctrl+C 停止服务器")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )