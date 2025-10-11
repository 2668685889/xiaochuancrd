"""
销售订单管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func, delete
from datetime import datetime
from uuid import uuid4

from app.core.database import get_db
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.customer import Customer
from app.models.product import Product
from app.models.user import User
from app.schemas.sales_order import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderResponse, 
    SalesOrderListResponse, SalesOrderItemCreate, SalesOrderItemResponse
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import model_to_dict, model_list_to_dict_list, snake_to_camel, paginate_response

router = APIRouter()


def generate_order_number():
    """生成订单编号"""
    return f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid4().hex[:6].upper()}"


@router.get("/SalesOrders", response_model=ApiResponse[PaginatedResponse[SalesOrderResponse]])
async def get_sales_orders(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: str = Query(None, description="搜索关键词"),
    status_filter: str = Query(None, description="订单状态过滤"),
    customer_uuid: str = Query(None, description="客户UUID"),
):
    """获取销售订单列表"""
    # 构建查询条件
    query = select(SalesOrder)
    
    if search:
        query = query.where(
            or_(
                SalesOrder.order_number.ilike(f"%{search}%"),
            )
        )
    
    if status_filter:
        query = query.where(SalesOrder.status == status_filter)
    
    if customer_uuid:
        query = query.where(SalesOrder.customer_uuid == customer_uuid)
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # 分页查询 - 按创建时间倒序排序，确保最新订单显示在顶部
    query = query.order_by(SalesOrder.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # 转换为响应格式
    order_responses = []
    for order in orders:
        # 获取订单明细，并关联查询商品表获取商品名称
        items_result = await db.execute(
            select(SalesOrderItem, Product.product_name)
            .join(Product, SalesOrderItem.product_uuid == Product.uuid)
            .where(SalesOrderItem.sales_order_uuid == order.uuid)
        )
        items_with_product = items_result.all()
        
        # 使用自动映射工具转换响应格式，确保字段正确映射
        order_dict = model_to_dict(order)
        order_camel = snake_to_camel(order_dict)
        
        # 处理订单明细
        items_camel = []
        for item, product_name in items_with_product:
            item_dict = model_to_dict(item)
            item_camel = snake_to_camel(item_dict)
            # 添加商品名称到明细中
            item_camel["productName"] = product_name
            items_camel.append(item_camel)
        
        # 将订单明细添加到订单响应中
        order_camel["items"] = items_camel
        
        # 将字典转换为SalesOrderResponse实例，确保响应模型验证通过
        sales_order_response = SalesOrderResponse(**order_camel)
        order_responses.append(sales_order_response)
    
    paginated_data = PaginatedResponse(
        items=order_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取销售订单列表成功"
    )


@router.get("/SalesOrders/{order_uuid}", response_model=ApiResponse[SalesOrderResponse])
async def get_sales_order(order_uuid: str, db: AsyncSession = Depends(get_db)):
    """获取单个销售订单"""
    result = await db.execute(
        select(SalesOrder).where(SalesOrder.uuid == order_uuid)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在",
        )
    
    # 获取订单明细，并关联查询商品表获取商品名称
    items_result = await db.execute(
        select(SalesOrderItem, Product.product_name)
        .join(Product, SalesOrderItem.product_uuid == Product.uuid)
        .where(SalesOrderItem.sales_order_uuid == order.uuid)
    )
    items_with_product = items_result.all()
    
    # 使用自动映射工具转换响应格式，确保字段正确映射
    order_dict = model_to_dict(order)
    order_camel = snake_to_camel(order_dict)
    
    # 确保前端需要的字段正确映射
    # 将数据库中的 customer_address 映射到 shippingAddress
    if 'customerAddress' in order_camel:
        order_camel['shippingAddress'] = order_camel['customerAddress']
    
    # 将数据库中的 expected_delivery_date 映射到 deliveryDate
    if 'expectedDeliveryDate' in order_camel:
        order_camel['deliveryDate'] = order_camel['expectedDeliveryDate']
    
    # 处理订单明细
    items_camel = []
    for item, product_name in items_with_product:
        item_dict = model_to_dict(item)
        item_camel = snake_to_camel(item_dict)
        # 添加商品名称到明细中
        item_camel["productName"] = product_name
        items_camel.append(item_camel)
    
    # 将订单明细添加到订单响应中
    order_camel["items"] = items_camel
    
    # 将字典转换为SalesOrderResponse实例，确保响应模型验证通过
    sales_order_response = SalesOrderResponse(**order_camel)
    
    return ApiResponse(
        success=True,
        data=sales_order_response,
        message="获取销售订单成功"
    )


@router.post("/SalesOrders", response_model=ApiResponse[SalesOrderResponse])
async def create_sales_order(order_data: SalesOrderCreate, db: AsyncSession = Depends(get_db)):
    """创建销售订单"""
    # 将UUID对象转换为字符串格式进行查询
    customer_uuid_str = str(order_data.customerUuid)
    
    # 检查客户是否存在（排除已软删除的客户）
    result = await db.execute(select(Customer).where(
        Customer.uuid == customer_uuid_str,
        Customer.deleted_at.is_(None)  # 只查询未删除的客户
    ))
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="客户不存在",
        )
    
    # 检查产品是否存在
    for item in order_data.items:
        # 将UUID对象转换为字符串格式进行查询
        product_uuid_str = str(item.productUuid)
        result = await db.execute(select(Product).where(Product.uuid == product_uuid_str))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"产品 {product_uuid_str} 不存在",
            )
    
    # 获取管理员用户作为创建者
    admin_result = await db.execute(select(User).where(User.username == "admin"))
    admin_user = admin_result.scalar_one_or_none()
    
    if not admin_user:
        # 如果没有admin用户，使用第一个用户
        first_user_result = await db.execute(select(User).limit(1))
        admin_user = first_user_result.scalar_one_or_none()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统中没有用户数据，无法创建订单",
        )
    
    # 创建销售订单
    order = SalesOrder(
        order_number=generate_order_number(),
        customer_uuid=order_data.customerUuid,
        customer_name=customer.customer_name,  # 设置客户名称
        order_date=datetime.fromisoformat(order_data.orderDate) if order_data.orderDate else datetime.now(),
        expected_delivery_date=datetime.fromisoformat(order_data.deliveryDate) if order_data.deliveryDate else None,
        customer_address=order_data.shippingAddress,  # 添加收货地址字段
        total_amount=0.0,  # 将在计算明细后更新
        status="PENDING",
        remark=order_data.notes,
        created_by=admin_user.uuid,  # 使用真实用户的UUID
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # 创建订单明细并计算总金额
    total_amount = 0.0
    for item_data in order_data.items:
        item_total = item_data.quantity * item_data.unitPrice
        total_amount += item_total
        
        item = SalesOrderItem(
            sales_order_uuid=order.uuid,
            product_uuid=item_data.productUuid,
            quantity=item_data.quantity,
            unit_price=item_data.unitPrice,
            total_price=item_total,
            remark=item_data.notes,
        )
        
        db.add(item)
    
    # 更新订单总金额
    order.total_amount = total_amount
    await db.commit()
    await db.refresh(order)
    
    # 获取订单明细用于响应
    items_result = await db.execute(
        select(SalesOrderItem).where(SalesOrderItem.sales_order_uuid == order.uuid)
    )
    items = items_result.scalars().all()
    
    # 使用自动映射工具
    order_dict = model_to_dict(order)
    order_camel = snake_to_camel(order_dict)
    
    # 处理订单明细
    items_camel = []
    for item in items:
        item_dict = model_to_dict(item)
        items_camel.append(snake_to_camel(item_dict))
    
    order_camel["items"] = items_camel
    
    return ApiResponse(
        success=True,
        data=order_camel,
        message="销售订单创建成功"
    )


@router.put("/SalesOrders/{order_uuid}", response_model=ApiResponse[SalesOrderResponse])
async def update_sales_order(
    order_uuid: str, 
    order_data: SalesOrderUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新销售订单信息"""
    result = await db.execute(select(SalesOrder).where(SalesOrder.uuid == order_uuid))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在",
        )
    
    # 更新订单信息
    if order_data.expectedDeliveryDate is not None:
        order.expected_delivery_date = order_data.expectedDeliveryDate
    
    if order_data.actualDeliveryDate is not None:
        order.actual_delivery_date = order_data.actualDeliveryDate
    
    if order_data.status is not None:
        order.status = order_data.status
    
    if order_data.remark is not None:
        order.remark = order_data.remark
    
    if order_data.shippingAddress is not None:
        order.customer_address = order_data.shippingAddress
    
    await db.commit()
    await db.refresh(order)
    
    # 获取订单明细
    items_result = await db.execute(
        select(SalesOrderItem).where(SalesOrderItem.sales_order_uuid == order.uuid)
    )
    items = items_result.scalars().all()
    
    # 使用自动映射工具
    order_dict = model_to_dict(order)
    order_camel = snake_to_camel(order_dict)
    
    # 处理订单明细
    items_camel = []
    for item in items:
        item_dict = model_to_dict(item)
        items_camel.append(snake_to_camel(item_dict))
    
    order_camel["items"] = items_camel
    
    return ApiResponse(
        success=True,
        data=order_camel,
        message="销售订单更新成功"
    )


@router.delete("/SalesOrders/{order_uuid}", response_model=ApiResponse[dict])
async def delete_sales_order(order_uuid: str, db: AsyncSession = Depends(get_db)):
    """删除销售订单（硬删除）"""
    result = await db.execute(select(SalesOrder).where(SalesOrder.uuid == order_uuid))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在",
        )
    
    # 先删除订单明细
    await db.execute(delete(SalesOrderItem).where(SalesOrderItem.sales_order_uuid == order_uuid))
    
    # 再删除订单
    await db.execute(delete(SalesOrder).where(SalesOrder.uuid == order_uuid))
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"message": "销售订单删除成功"},
        message="销售订单删除成功"
    )