"""
操作日志服务
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import func

from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogCreate, OperationLogFilter
from app.schemas.response import PaginatedResponse


class OperationLogService:
    """操作日志服务类"""
    
    @staticmethod
    async def create_log(
        db: AsyncSession,
        log_data: OperationLogCreate
    ) -> OperationLog:
        """创建操作日志"""
        log = OperationLog(
            operation_type=log_data.operation_type,
            operation_module=log_data.operation_module,
            operation_description=log_data.operation_description,
            target_uuid=str(log_data.target_uuid) if log_data.target_uuid else None,
            target_name=log_data.target_name,
            before_data=log_data.before_data,
            after_data=log_data.after_data,
            operator_uuid=str(log_data.operator_uuid),
            operator_name=log_data.operator_name,
            operator_ip=log_data.operator_ip,
            operation_status=log_data.operation_status,
            error_message=log_data.error_message,
            operation_time=datetime.utcnow()
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        return log
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        filter_data: OperationLogFilter
    ) -> PaginatedResponse[Dict[str, Any]]:
        """获取操作日志列表（带分页和过滤）"""
        # 构建查询条件
        conditions = []
        
        if filter_data.operation_type:
            conditions.append(OperationLog.operation_type == filter_data.operation_type)
        
        if filter_data.operation_module:
            conditions.append(OperationLog.operation_module == filter_data.operation_module)
        
        if filter_data.operator_name:
            conditions.append(OperationLog.operator_name.ilike(f"%{filter_data.operator_name}%"))
        
        if filter_data.target_name:
            conditions.append(OperationLog.target_name.ilike(f"%{filter_data.target_name}%"))
        
        if filter_data.operation_status:
            conditions.append(OperationLog.operation_status == filter_data.operation_status)
        
        if filter_data.start_date:
            conditions.append(OperationLog.operation_time >= filter_data.start_date)
        
        if filter_data.end_date:
            # 结束时间包含当天
            end_date = filter_data.end_date.replace(hour=23, minute=59, second=59)
            conditions.append(OperationLog.operation_time <= end_date)
        
        # 计算总数
        count_query = select(func.count()).select_from(OperationLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 计算分页
        offset = (filter_data.page - 1) * filter_data.size
        pages = (total + filter_data.size - 1) // filter_data.size
        
        # 获取数据
        query = select(OperationLog).order_by(OperationLog.operation_time.desc())
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(offset).limit(filter_data.size)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        # 转换为字典格式
        log_dicts = [log.to_dict() for log in logs]
        
        return PaginatedResponse(
            items=log_dicts,
            total=total,
            page=filter_data.page,
            size=filter_data.size,
            pages=pages
        )
    
    @staticmethod
    async def get_log_by_uuid(
        db: AsyncSession,
        log_uuid: str
    ) -> Optional[OperationLog]:
        """根据UUID获取操作日志"""
        result = await db.execute(
            select(OperationLog).where(OperationLog.uuid == log_uuid)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_recent_logs(
        db: AsyncSession,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """获取最近的操作日志"""
        query = (
            select(OperationLog)
            .order_by(OperationLog.operation_time.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [log.to_dict() for log in logs]
    
    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取操作日志统计信息"""
        # 计算开始日期
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)
        
        # 按操作类型统计
        type_query = (
            select(
                OperationLog.operation_type,
                func.count().label('count')
            )
            .where(OperationLog.operation_time >= start_date)
            .group_by(OperationLog.operation_type)
            .order_by(func.count().desc())
        )
        type_result = await db.execute(type_query)
        type_stats = {row[0]: row[1] for row in type_result}
        
        # 按模块统计
        module_query = (
            select(
                OperationLog.operation_module,
                func.count().label('count')
            )
            .where(OperationLog.operation_time >= start_date)
            .group_by(OperationLog.operation_module)
            .order_by(func.count().desc())
        )
        module_result = await db.execute(module_query)
        module_stats = {row[0]: row[1] for row in module_result}
        
        # 按操作者统计
        operator_query = (
            select(
                OperationLog.operator_name,
                func.count().label('count')
            )
            .where(OperationLog.operation_time >= start_date)
            .group_by(OperationLog.operator_name)
            .order_by(func.count().desc())
            .limit(10)
        )
        operator_result = await db.execute(operator_query)
        operator_stats = {row[0]: row[1] for row in operator_result}
        
        # 今日操作统计
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_query = select(func.count()).where(OperationLog.operation_time >= today_start)
        today_result = await db.execute(today_query)
        today_count = today_result.scalar() or 0
        
        return {
            "type_statistics": type_stats,
            "module_statistics": module_stats,
            "operator_statistics": operator_stats,
            "today_count": today_count,
            "total_count": await OperationLogService.get_total_count(db),
            "success_rate": await OperationLogService.get_success_rate(db, days)
        }
    
    @staticmethod
    async def get_total_count(db: AsyncSession) -> int:
        """获取总操作日志数量"""
        result = await db.execute(select(func.count()).select_from(OperationLog))
        return result.scalar() or 0
    
    @staticmethod
    async def get_success_rate(db: AsyncSession, days: int = 30) -> float:
        """获取操作成功率"""
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)
        
        total_query = select(func.count()).where(OperationLog.operation_time >= start_date)
        success_query = select(func.count()).where(
            and_(
                OperationLog.operation_time >= start_date,
                OperationLog.operation_status == 'SUCCESS'
            )
        )
        
        total_result = await db.execute(total_query)
        success_result = await db.execute(success_query)
        
        total = total_result.scalar() or 0
        success = success_result.scalar() or 0
        
        if total == 0:
            return 100.0
        
        return round((success / total) * 100, 2)