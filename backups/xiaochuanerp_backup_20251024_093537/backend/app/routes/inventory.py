"""
库存管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import Optional

from app.core.database import get_async_db
from app.models.inventory import InventoryRecord
from app.models.product import Product
from app.schemas.inventory import (
    InventoryRecordCreate, 
    InventoryRecordResponse, 
    InventoryRecordListResponse,
    ChangeType,
    InventorySummary
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import model_to_dict, model_list_to_dict_list, snake_to_camel, camel_to_snake, paginate_response

router = APIRouter()


@router.get("/Inventory/Summary", response_model=ApiResponse[InventorySummary])
async def get_inventory_summary(db: AsyncSession = Depends(get_async_db)):
    """获取库存汇总信息"""
    # 获取总产品数
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    
    total_products = len(products)
    total_value = sum(product.current_quantity * product.unit_price for product in products)
    
    # 获取库存预警产品
    low_stock_products = [
        product for product in products 
        if product.current_quantity <= product.min_quantity
    ]
    
    # 获取库存过高的产品
    high_stock_products = [
        product for product in products 
        if product.current_quantity >= product.max_quantity
    ]
    
    # 获取今日库存变动
    today = datetime.now().date()
    result = await db.execute(
        select(InventoryRecord).where(InventoryRecord.record_date == today)
    )
    today_records = result.scalars().all()
    
    today_in = sum(record.change_quantity for record in today_records if record.change_type == ChangeType.IN)
    today_out = sum(record.change_quantity for record in today_records if record.change_type == ChangeType.OUT)
    
    summary_data = InventorySummary(
        totalProducts=total_products,
        totalValue=total_value,
        lowStockCount=len(low_stock_products),
        highStockCount=len(high_stock_products),
        todayIn=today_in,
        todayOut=today_out,
        lowStockProducts=[
            {
                "uuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "minQuantity": product.min_quantity,
            }
            for product in low_stock_products
        ],
        highStockProducts=[
            {
                "uuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "maxQuantity": product.max_quantity,
            }
            for product in high_stock_products
        ],
    )
    
    return ApiResponse(
        success=True,
        data=summary_data,
        message="获取库存汇总信息成功"
    )


@router.get("/Inventory/Alerts", response_model=ApiResponse[dict])
async def get_inventory_alerts(db: AsyncSession = Depends(get_async_db)):
    """获取库存预警列表"""
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    
    alerts = []
    
    for product in products:
        if product.current_quantity <= product.min_quantity:
            alerts.append({
                "type": "LOW_STOCK",
                "productUuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "minQuantity": product.min_quantity,
                "severity": "HIGH" if product.current_quantity == 0 else "MEDIUM",
            })
        elif product.current_quantity >= product.max_quantity:
            alerts.append({
                "type": "HIGH_STOCK",
                "productUuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "maxQuantity": product.max_quantity,
                "severity": "LOW",
            })
    
    return ApiResponse(
        success=True,
        data={"alerts": alerts},
        message="获取库存预警列表成功"
    )


@router.get("/Inventory", response_model=ApiPaginatedResponse[InventoryRecordResponse])
async def get_inventory_records(
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    product_uuid: Optional[str] = Query(None, description="产品UUID"),
    change_type: Optional[ChangeType] = Query(None, description="变动类型"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    search: Optional[str] = Query(None, description="搜索关键词"),
):
    """获取库存记录列表"""
    # 构建查询条件
    query = select(InventoryRecord).options(selectinload(InventoryRecord.product)).join(Product)
    
    conditions = []
    
    if product_uuid:
        conditions.append(InventoryRecord.product_uuid == product_uuid)
    
    if change_type:
        conditions.append(InventoryRecord.change_type == change_type)
    
    if start_date:
        conditions.append(InventoryRecord.record_date >= start_date)
    
    if end_date:
        conditions.append(InventoryRecord.record_date <= end_date)
    
    if search:
        conditions.append(
            or_(
                Product.product_name.ilike(f"%{search}%"),
                Product.product_code.ilike(f"%{search}%"),
                InventoryRecord.remark.ilike(f"%{search}%"),
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # 分页查询
    query = query.order_by(InventoryRecord.record_date.desc(), InventoryRecord.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 手动处理数据转换，解决字段映射问题
    record_responses = []
    for record in records:
        # 处理枚举值大小写转换
        change_type_lower = record.change_type.lower() if record.change_type else None
        
        # 使用正确的异步方式获取关联产品信息
        product_name = None
        product_code = None
        if record.product:
            product_name = record.product.product_name
            product_code = record.product.product_code
        
        record_response = {
            "uuid": record.uuid,
            "productUuid": record.product_uuid,
            "productName": product_name,
            "productCode": product_code,
            "previousQuantity": record.current_quantity - record.quantity_change,
            "currentQuantity": record.current_quantity,
            "changeQuantity": record.quantity_change,
            "changeType": change_type_lower,
            "reason": record.remark,
            "recordedBy": record.created_by,
            "recordedAt": record.created_at
        }
        record_responses.append(record_response)
    
    paginated_data = PaginatedResponse(
        items=record_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取库存记录列表成功"
    )


@router.get("/Inventory/{record_uuid}", response_model=ApiResponse[InventoryRecordResponse])
async def get_inventory_record(record_uuid: str, db: AsyncSession = Depends(get_async_db)):
    """获取单个库存记录"""
    result = await db.execute(
        select(InventoryRecord).options(selectinload(InventoryRecord.product)).join(Product).where(InventoryRecord.uuid == record_uuid)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在",
        )
    
    # 手动处理数据转换，解决字段映射问题
    change_type_lower = record.change_type.lower() if record.change_type else None
    
    # 使用正确的异步方式获取关联产品信息
    product_name = None
    product_code = None
    if record.product:
        product_name = record.product.product_name
        product_code = record.product.product_code
    
    record_response = {
        "uuid": record.uuid,
        "productUuid": record.product_uuid,
        "productName": product_name,
        "productCode": product_code,
        "previousQuantity": record.current_quantity - record.quantity_change,
        "currentQuantity": record.current_quantity,
        "changeQuantity": record.quantity_change,
        "changeType": change_type_lower,
        "reason": record.remark,
        "recordedBy": record.created_by,
        "recordedAt": record.created_at
    }
    
    return ApiResponse(
        success=True,
        data=record_response,
        message="获取库存记录成功"
    )


@router.post("/Inventory", response_model=ApiResponse[InventoryRecordResponse])
async def create_inventory_record(
    record_data: InventoryRecordCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """创建库存记录"""
    # 检查产品是否存在
    result = await db.execute(select(Product).where(Product.uuid == record_data.productUuid))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )
    
    # 计算新的库存数量
    if record_data.changeType == ChangeType.IN:
        new_quantity = product.current_quantity + record_data.changeQuantity
    elif record_data.changeType == ChangeType.OUT:
        if product.current_quantity < record_data.changeQuantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="库存不足",
            )
        new_quantity = product.current_quantity - record_data.changeQuantity
    elif record_data.changeType == ChangeType.ADJUST:
        new_quantity = record_data.changeQuantity
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的变动类型",
        )
    
    # 创建库存记录
    record = InventoryRecord(
        product_uuid=record_data.productUuid,
        change_type=record_data.changeType.upper(),  # 转换为大写以匹配数据库枚举
        quantity_change=record_data.changeQuantity,
        current_quantity=new_quantity,
        remark=record_data.reason,
        record_date=datetime.now().date(),
        created_by="system",  # TODO: 从认证信息中获取用户ID
    )
    
    # 更新产品库存
    product.current_quantity = new_quantity
    product.updated_at = datetime.now()
    
    db.add(record)
    await db.commit()
    await db.refresh(record)
    await db.refresh(product)
    
    record_response = {
        "uuid": record.uuid,
        "productUuid": record.product_uuid,
        "productName": product.product_name,
        "productCode": product.product_code,
        "previousQuantity": product.current_quantity - record.quantity_change,
        "currentQuantity": product.current_quantity,
        "changeQuantity": record.quantity_change,
        "changeType": record.change_type.lower() if record.change_type else None,
        "reason": record.remark,
        "recordedBy": record.created_by,
        "recordedAt": record.created_at
    }
    
    return ApiResponse(
        success=True,
        data=record_response,
        message="库存记录创建成功"
    )


@router.get("/Inventory/Summary", response_model=ApiResponse[InventorySummary])
async def get_inventory_summary(db: AsyncSession = Depends(get_async_db)):
    """获取库存汇总信息"""
    # 获取总产品数
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    
    total_products = len(products)
    total_value = sum(product.current_quantity * product.unit_price for product in products)
    
    # 获取库存预警产品
    low_stock_products = [
        product for product in products 
        if product.current_quantity <= product.min_quantity
    ]
    
    # 获取库存过高的产品
    high_stock_products = [
        product for product in products 
        if product.current_quantity >= product.max_quantity
    ]
    
    # 获取今日库存变动
    today = datetime.now().date()
    result = await db.execute(
        select(InventoryRecord).where(InventoryRecord.record_date == today)
    )
    today_records = result.scalars().all()
    
    today_in = sum(record.change_quantity for record in today_records if record.change_type == ChangeType.IN)
    today_out = sum(record.change_quantity for record in today_records if record.change_type == ChangeType.OUT)
    
    summary_data = InventorySummary(
        totalProducts=total_products,
        totalValue=total_value,
        lowStockCount=len(low_stock_products),
        highStockCount=len(high_stock_products),
        todayIn=today_in,
        todayOut=today_out,
        lowStockProducts=[
            {
                "uuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "minQuantity": product.min_quantity,
            }
            for product in low_stock_products
        ],
        highStockProducts=[
            {
                "uuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "maxQuantity": product.max_quantity,
            }
            for product in high_stock_products
        ],
    )
    
    return ApiResponse(
        success=True,
        data=summary_data,
        message="获取库存汇总信息成功"
    )


@router.get("/Inventory/Alerts", response_model=ApiResponse[dict])
async def get_inventory_alerts(db: AsyncSession = Depends(get_async_db)):
    """获取库存预警列表"""
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    
    alerts = []
    
    for product in products:
        if product.current_quantity <= product.min_quantity:
            alerts.append({
                "type": "LOW_STOCK",
                "productUuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "minQuantity": product.min_quantity,
                "severity": "HIGH" if product.current_quantity == 0 else "MEDIUM",
            })
        elif product.current_quantity >= product.max_quantity:
            alerts.append({
                "type": "HIGH_STOCK",
                "productUuid": product.uuid,
                "productName": product.product_name,
                "currentQuantity": product.current_quantity,
                "maxQuantity": product.max_quantity,
                "severity": "LOW",
            })
    
    return ApiResponse(
        success=True,
        data={"alerts": alerts},
        message="获取库存预警列表成功"
    )