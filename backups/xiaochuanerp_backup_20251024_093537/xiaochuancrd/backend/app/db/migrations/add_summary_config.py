"""
添加总结配置字段的数据库迁移脚本
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.smart_assistant import AssistantModel
from sqlalchemy import text


async def add_summary_config_field():
    """为现有助手配置添加总结配置字段"""
    
    db = SessionLocal()
    try:
        # 查询所有助手配置
        assistants = db.execute(
            text("SELECT uuid, model_config FROM sys_assistant")
        ).fetchall()
        
        updated_count = 0
        
        for assistant in assistants:
            assistant_uuid = assistant[0]
            model_config_str = assistant[1]
            
            # 如果model_config是字符串，尝试解析为JSON
            if isinstance(model_config_str, str):
                try:
                    import json
                    model_config = json.loads(model_config_str)
                except json.JSONDecodeError:
                    print(f"助手 {assistant_uuid} 的model_config不是有效的JSON，跳过")
                    continue
            else:
                model_config = model_config_str or {}
            
            # 如果已经有总结配置，跳过
            if "summary_config" in model_config:
                print(f"助手 {assistant_uuid} 已有总结配置，跳过")
                continue
            
            # 创建总结配置，基于默认配置但调整参数
            summary_config = {
                "api_key": model_config.get("api_key", ""),
                "base_url": model_config.get("base_url", "https://api.deepseek.com"),
                "model": model_config.get("model", "deepseek-chat"),
                "max_tokens": model_config.get("max_tokens", 4000),
                "temperature": 0.3,  # 总结使用较低温度，确保结果更一致
                "system_prompt": """你是一个专业的数据分析助手。你的任务是分析用户提供的SQL查询结果，并以清晰、简洁的方式总结数据中的关键信息。

请遵循以下原则：
1. 提供数据的关键洞察和趋势
2. 使用简洁明了的语言，避免技术术语
3. 突出重要的数字和百分比
4. 如果数据为空，明确说明
5. 保持回答客观，基于数据事实"""
            }
            
            # 更新模型配置
            model_config["summary_config"] = summary_config
            
            # 更新数据库
            db.execute(
                text("UPDATE sys_assistant SET model_config = :model_config WHERE uuid = :uuid"),
                {"model_config": json.dumps(model_config), "uuid": assistant_uuid}
            )
            
            updated_count += 1
            print(f"已为助手 {assistant_uuid} 添加总结配置")
        
        # 提交更改
        db.commit()
        print(f"迁移完成，共更新 {updated_count} 个助手配置")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(add_summary_config_field())