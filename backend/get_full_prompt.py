#!/usr/bin/env python3
import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.smart_assistant import AssistantModel
from app.services.deepseek_service import DeepSeekService
import json

async def get_prompt_content():
    """获取数据库中的prompt内容"""
    async with AsyncSessionLocal() as session:
        # 查询助手配置
        result = await session.execute(
            select(AssistantModel).where(AssistantModel.workspace_uuid == 'default')
        )
        assistant = result.scalar_one_or_none()
        
        if assistant and assistant.model_config:
            model_config = assistant.model_config
            
            # 检查所有可能的prompt字段
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
            
            # 创建DeepSeek服务实例并获取默认prompt
            print("\n=== 默认系统提示词 ===")
            service = DeepSeekService()
            default_prompt = "你是一个专业的ERP系统智能助手，帮助用户查询和分析业务数据。请用简洁、专业的语言回答用户问题。"
            print(default_prompt)
            
            # 获取SQL生成提示词
            print("\n=== SQL生成提示词 ===")
            sql_prompt = service._build_sql_generation_prompt()
            print(sql_prompt)
        else:
            print("未找到助手配置或配置为空")

if __name__ == "__main__":
    asyncio.run(get_prompt_content())