#!/usr/bin/env python3
import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.smart_assistant import AssistantModel
import json

async def get_prompt():
    """获取助手配置中的prompt内容"""
    async with AsyncSessionLocal() as session:
        # 查询助手配置
        result = await session.execute(
            select(AssistantModel).where(AssistantModel.workspace_uuid == 'default')
        )
        assistant = result.scalar_one_or_none()
        
        if assistant and assistant.model_config:
            # 尝试获取prompt内容
            model_config = assistant.model_config
            
            # 检查各种可能的prompt字段
            prompt_fields = ['system_prompt', 'prompt', 'system_message', 'instruction']
            
            for field in prompt_fields:
                if field in model_config:
                    print(f"=== {field} 内容 ===")
                    print(model_config[field])
                    print("\n")
                    return
            
            # 如果没有找到标准字段，打印完整配置
            print("=== 完整模型配置 ===")
            print(json.dumps(model_config, indent=2, ensure_ascii=False))
        else:
            print("未找到助手配置或配置为空")

if __name__ == "__main__":
    asyncio.run(get_prompt())