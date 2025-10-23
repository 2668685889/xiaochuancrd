#!/usr/bin/env python3
import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.smart_assistant import AssistantModel

async def check_assistant_config():
    """检查助手配置表中的数据"""
    async with AsyncSessionLocal() as session:
        # 查询助手配置
        result = await session.execute(select(AssistantModel))
        assistant = result.scalar_one_or_none()
        
        if assistant:
            print(f"找到助手配置:")
            print(f"UUID: {assistant.uuid}")
            print(f"模型类型: {assistant.model_type}")
            print(f"模型配置: {assistant.model_config}")
            print(f"是否激活: {assistant.is_active}")
            print(f"创建时间: {assistant.created_at}")
            print(f"更新时间: {assistant.updated_at}")
            
            # 检查prompt字段
            if assistant.model_config and 'prompt' in assistant.model_config:
                print(f"提示词内容: {assistant.model_config['prompt']}")
            else:
                print("提示词字段不存在或为空")
        else:
            print("未找到助手配置")

if __name__ == "__main__":
    asyncio.run(check_assistant_config())