"""
测试通用Coze同步模板功能
"""

import asyncio
import logging
from uuid import UUID

from app.services.coze_sync_template import CozeSyncTemplate

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_create_sync_template():
    """测试创建同步模板"""
    logger.info("=== 测试创建同步模板 ===")
    
    result = await CozeSyncTemplate.create_sync_template(
        table_name="customers",
        config_title="客户数据同步模板",
        coze_workflow_id="your_workflow_id_here",
        coze_api_url="https://api.coze.cn",
        coze_api_key="your_api_key_here",
        selected_fields=["customer_name", "customer_code", "phone", "email"],
        sync_on_insert=True,
        sync_on_update=True,
        sync_on_delete=False
    )
    
    logger.info(f"创建结果: {result}")
    return result


async def test_get_template_preview():
    """测试获取模板预览"""
    logger.info("=== 测试获取模板预览 ===")
    
    result = await CozeSyncTemplate.get_template_preview(
        table_name="customers",
        selected_fields=["customer_name", "customer_code", "phone", "email"]
    )
    
    logger.info(f"预览结果: {result}")
    return result


async def test_get_sync_templates():
    """测试获取所有同步模板"""
    logger.info("=== 测试获取所有同步模板 ===")
    
    templates = await CozeSyncTemplate.get_sync_templates()
    
    logger.info(f"模板数量: {len(templates)}")
    for template in templates:
        logger.info(f"模板: {template['config_title']} - {template['table_name']}")
    
    return templates


async def test_manual_sync():
    """测试手动同步"""
    logger.info("=== 测试手动同步 ===")
    
    # 先获取所有模板
    templates = await CozeSyncTemplate.get_sync_templates()
    
    if not templates:
        logger.info("没有找到同步模板，跳过手动同步测试")
        return None
    
    # 使用第一个模板进行测试
    template = templates[0]
    config_uuid = UUID(template["uuid"])
    
    logger.info(f"使用模板进行手动同步: {template['config_title']}")
    
    # 只同步少量数据用于测试
    result = await CozeSyncTemplate.manual_sync_all_records(
        config_uuid=config_uuid,
        batch_size=5,  # 小批次测试
        filters=None
    )
    
    logger.info(f"手动同步结果: {result}")
    return result


async def main():
    """主测试函数"""
    logger.info("开始测试通用Coze同步模板功能")
    
    try:
        # 测试模板预览
        await test_get_template_preview()
        
        # 测试创建模板（需要有效的API密钥和工作流ID）
        # await test_create_sync_template()
        
        # 测试获取模板
        await test_get_sync_templates()
        
        # 测试手动同步（需要有效的模板）
        # await test_manual_sync()
        
        logger.info("测试完成")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())