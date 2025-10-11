"""
操作日志API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.operation_log_service import OperationLogService
from app.schemas.operation_log import (
    OperationLogCreate, 
    OperationLogResponse, 
    OperationLogListResponse,
    OperationLogFilter
)
from app.schemas.response import ApiResponse

router = APIRouter()


@router.get("/OperationLogs", response_model=ApiResponse[OperationLogListResponse])
async def get_operation_logs(
    operation_type: Optional[str] = Query(None, description="操作类型"),
    operation_module: Optional[str] = Query(None, description="操作模块"),
    operator_name: Optional[str] = Query(None, description="操作者姓名"),
    target_name: Optional[str] = Query(None, description="目标名称"),
    operation_status: Optional[str] = Query(None, description="操作状态"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志列表"""
    try:
        filter_data = OperationLogFilter(
            operation_type=operation_type,
            operation_module=operation_module,
            operator_name=operator_name,
            target_name=target_name,
            operation_status=operation_status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size
        )
        
        result = await OperationLogService.get_logs(db, filter_data)
        
        return ApiResponse(
            success=True,
            data=OperationLogListResponse(
                items=result.items,
                total=result.total,
                page=result.page,
                size=result.size,
                pages=result.pages
            ),
            message="获取操作日志成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志失败: {str(e)}")


@router.get("/OperationLogs/{log_uuid}", response_model=ApiResponse[OperationLogResponse])
async def get_operation_log(
    log_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    """根据UUID获取操作日志详情"""
    try:
        log = await OperationLogService.get_log_by_uuid(db, log_uuid)
        if not log:
            raise HTTPException(status_code=404, detail="操作日志不存在")
        
        return ApiResponse(
            success=True,
            data=log.to_dict(),
            message="获取操作日志详情成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志详情失败: {str(e)}")


@router.get("/OperationLogs/Recent", response_model=ApiResponse[list[OperationLogResponse]])
async def get_recent_operation_logs(
    limit: int = Query(10, ge=1, le=50, description="限制数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取最近的操作日志"""
    try:
        logs = await OperationLogService.get_recent_logs(db, limit)
        
        return ApiResponse(
            success=True,
            data=logs,
            message="获取最近操作日志成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近操作日志失败: {str(e)}")


@router.get("/OperationLogs/Statistics", response_model=ApiResponse[dict])
async def get_operation_log_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志统计信息"""
    try:
        statistics = await OperationLogService.get_statistics(db, days)
        
        return ApiResponse.success(
            data=statistics,
            message="获取操作日志统计成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志统计失败: {str(e)}")


@router.post("/OperationLogs", response_model=ApiResponse[OperationLogResponse])
async def create_operation_log(
    log_data: OperationLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建操作日志（内部使用，不对外公开）"""
    try:
        log = await OperationLogService.create_log(db, log_data)
        
        return ApiResponse.success(
            data=log.to_dict(),
            message="创建操作日志成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建操作日志失败: {str(e)}")


# 工具函数：记录操作日志
async def log_operation(
    db: AsyncSession,
    operation_type: str,
    operation_module: str,
    operation_description: str,
    operator_uuid: str,
    operator_name: str,
    target_uuid: Optional[str] = None,
    target_name: Optional[str] = None,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
    operator_ip: Optional[str] = None,
    operation_status: str = "SUCCESS",
    error_message: Optional[str] = None
):
    """记录操作日志的工具函数"""
    try:
        log_data = OperationLogCreate(
            operation_type=operation_type,
            operation_module=operation_module,
            operation_description=operation_description,
            target_uuid=target_uuid,
            target_name=target_name,
            before_data=before_data,
            after_data=after_data,
            operator_uuid=operator_uuid,
            operator_name=operator_name,
            operator_ip=operator_ip,
            operation_status=operation_status,
            error_message=error_message
        )
        
        await OperationLogService.create_log(db, log_data)
    except Exception as e:
        # 记录日志失败不应该影响主业务流程
        print(f"记录操作日志失败: {str(e)}")