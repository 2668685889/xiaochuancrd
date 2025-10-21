#!/usr/bin/env python3
"""
修复智能助手模型配置脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# 数据库配置（使用后端配置中的数据库）
DATABASE_URL = "mysql+aiomysql://root:Xiaochuan123!@localhost:3306/xiaochuanERP"

async def fix_model_config():
    """修复模型配置"""
    try:
        # 创建异步数据库引擎
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # 创建异步会话工厂
        AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with AsyncSessionLocal() as session:
            # 导入模型
            from app.models.smart_assistant import AssistantModel
            
            # 查询现有的助手配置
            result = await session.execute(select(AssistantModel))
            assistant = result.scalar_one_or_none()
            
            if assistant:
                print(f"找到现有配置: {assistant.name} (ID: {assistant.uuid})")
                print(f"当前模型类型: {assistant.model_type}")
                print(f"当前配置: {assistant.model_config}")
                
                # 更新为正确的DeepSeek配置
                new_config = {
                    "api_key": "sk-1234567890abcdef",  # 替换为实际的API密钥
                    "api_domain": "api.deepseek.com",
                    "base_url": "https://api.deepseek.com/v1"
                }
                
                assistant.model_type = "deepseek-chat"
                assistant.model_config = new_config
                
                await session.commit()
                print("✅ 配置已更新为正确的DeepSeek配置")
                print(f"新配置: {new_config}")
            else:
                print("❌ 未找到现有的助手配置")
                
                # 创建新的配置
                import uuid
                new_assistant = AssistantModel(
                    uuid=str(uuid.uuid4()),
                    name="智能助手配置",
                    description="AI模型配置",
                    model_type="deepseek-chat",
                    model_config={
                        "api_key": "sk-1234567890abcdef",  # 替换为实际的API密钥
                        "api_domain": "api.deepseek.com",
                        "base_url": "https://api.deepseek.com/v1"
                    }
                )
                
                session.add(new_assistant)
                await session.commit()
                print("✅ 已创建新的DeepSeek配置")
                
    except Exception as e:
        print(f"❌ 修复配置时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始修复智能助手模型配置...")
    asyncio.run(fix_model_config())
    print("修复完成!")