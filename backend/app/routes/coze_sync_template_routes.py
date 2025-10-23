"""
通用Coze同步模板API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.services.coze_sync_template import CozeSyncTemplate

router = APIRouter(prefix="/api/v1/coze-sync-templates", tags=["Coze同步模板"])


@router.post("/", response_model=Dict[str, Any])
async def create_sync_template(
    table_name: str,
    config_title: str,
    coze_workflow_id: str,
    coze_api_url: str = "https://api.coze.cn",
    coze_api_key: Optional[str] = None,
    selected_fields: Optional[List[str]] = None,
    sync_on_insert: bool = True,
    sync_on_update: bool = True,
    sync_on_delete: bool = False,
    created_by: Optional[UUID] = None
):
    """
    创建通用同步模板
    
    Args:
        table_name: 数据表名
        config_title: 配置标题
        coze_workflow_id: Coze工作流ID
        coze_api_url: Coze API地址
        coze_api_key: Coze API密钥
        selected_fields: 选择的字段列表
        sync_on_insert: 是否同步插入操作
        sync_on_update: 是否同步更新操作
        sync_on_delete: 是否同步删除操作
        created_by: 创建者UUID
    """
    result = await CozeSyncTemplate.create_sync_template(
        table_name=table_name,
        config_title=config_title,
        coze_workflow_id=coze_workflow_id,
        coze_api_url=coze_api_url,
        coze_api_key=coze_api_key,
        selected_fields=selected_fields,
        sync_on_insert=sync_on_insert,
        sync_on_update=sync_on_update,
        sync_on_delete=sync_on_delete,
        created_by=created_by
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/{config_uuid}/manual-sync", response_model=Dict[str, Any])
async def manual_sync_all_records(
    config_uuid: UUID,
    batch_size: int = 100,
    filters: Optional[Dict[str, Any]] = None
):
    """
    手动同步所有记录到Coze
    
    Args:
        config_uuid: 同步配置UUID
        batch_size: 批次大小
        filters: 数据过滤条件
    """
    result = await CozeSyncTemplate.manual_sync_all_records(
        config_uuid=config_uuid,
        batch_size=batch_size,
        filters=filters
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/", response_model=List[Dict[str, Any]])
async def get_sync_templates():
    """获取所有同步模板"""
    templates = await CozeSyncTemplate.get_sync_templates()
    return templates


@router.get("/preview", response_model=Dict[str, Any])
async def get_template_preview(
    table_name: str,
    selected_fields: Optional[List[str]] = None
):
    """
    获取同步模板预览
    
    Args:
        table_name: 数据表名
        selected_fields: 选择的字段列表
    """
    result = await CozeSyncTemplate.get_template_preview(
        table_name=table_name,
        selected_fields=selected_fields
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.put("/{config_uuid}", response_model=Dict[str, Any])
async def update_sync_template(
    config_uuid: UUID,
    updates: Dict[str, Any]
):
    """
    更新同步模板
    
    Args:
        config_uuid: 同步配置UUID
        updates: 更新字段
    """
    result = await CozeSyncTemplate.update_sync_template(
        config_uuid=config_uuid,
        updates=updates
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.delete("/{config_uuid}", response_model=Dict[str, Any])
async def delete_sync_template(config_uuid: UUID):
    """删除同步模板"""
    result = await CozeSyncTemplate.delete_sync_template(config_uuid)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/{config_uuid}", response_model=Dict[str, Any])
async def get_sync_template(config_uuid: UUID):
    """获取单个同步模板详情"""
    templates = await CozeSyncTemplate.get_sync_templates()
    
    for template in templates:
        if template["uuid"] == str(config_uuid):
            return template
    
    raise HTTPException(status_code=404, detail="同步模板不存在")