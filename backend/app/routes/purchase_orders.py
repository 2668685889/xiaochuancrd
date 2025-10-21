"""
采购订单管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from datetime import datetime
from uuid import uuid4

from app.core.database import get_async_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.product_model import ProductModel
from app.models.user import User
from app.schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse, 
    PurchaseOrderListResponse, PurchaseOrderItemCreate, PurchaseOrderItemResponse
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import model_to_dict, model_list_to_dict_list, snake_to_camel, camel_to_snake, paginate_response

router = APIRouter()


def generate_order_number():
    """生成订单编号"""
    return f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid4().hex[:6].upper()}"


@router.get("/PurchaseOrders", response_model=ApiResponse[PaginatedResponse[PurchaseOrderResponse]])
async def get_purchase_orders(
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词（订单编号）"),
    supplier_uuid: str = Query(None, description="供应商UUID"),
    product_uuid: str = Query(None, description="商品UUID"),
    start_date: str = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: str = Query(None, description="结束日期（YYYY-MM-DD）"),
    min_amount: float = Query(None, ge=0, description="最小金额"),
    max_amount: float = Query(None, ge=0, description="最大金额"),
):
    """获取采购订单列表"""
    # 构建查询条件
    query = select(PurchaseOrder)
    
    if search:
        query = query.where(
            or_(
                PurchaseOrder.order_number.ilike(f"%{search}%"),
            )
        )
    
    if supplier_uuid:
        query = query.where(PurchaseOrder.supplier_uuid == supplier_uuid)
    
    # 商品筛选 - 通过订单明细关联查询
    if product_uuid:
        # 先查询包含指定商品的订单明细
        order_items_query = select(PurchaseOrderItem.purchase_order_uuid).where(
            PurchaseOrderItem.product_uuid == product_uuid
        ).distinct()
        
        # 将查询结果作为子查询条件
        query = query.where(PurchaseOrder.uuid.in_(order_items_query))
    
    # 日期范围筛选
    if start_date:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.where(PurchaseOrder.order_date >= start_datetime)
    
    if end_date:
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.where(PurchaseOrder.order_date <= end_datetime)
    
    # 金额范围筛选
    if min_amount is not None:
        query = query.where(PurchaseOrder.total_amount >= min_amount)
    
    if max_amount is not None:
        query = query.where(PurchaseOrder.total_amount <= max_amount)
    
    # 获取总数
    total_result = await db.execute(select(PurchaseOrder))
    total = len(total_result.scalars().all())
    
    # 分页查询 - 按创建时间倒序排序，确保最新订单显示在顶部
    query = query.order_by(PurchaseOrder.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # 转换为响应格式
    order_responses = []
    for order in orders:
        # 获取供应商信息
        supplier_result = await db.execute(
            select(Supplier).where(Supplier.uuid == order.supplier_uuid)
        )
        supplier = supplier_result.scalar_one_or_none()
        
        # 获取订单明细
        items_result = await db.execute(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_uuid == order.uuid)
        )
        items = items_result.scalars().all()
        
        # 手动处理数据转换，解决字段映射问题
        order_response = {
            "uuid": order.uuid,
            "orderNumber": order.order_number,
            "supplierUuid": order.supplier_uuid,
            "supplierName": supplier.supplier_name if supplier else "未知供应商",
            "totalAmount": order.total_amount,
            "orderDate": order.order_date,
            "expectedDeliveryDate": order.expected_delivery_date,
            "actualDeliveryDate": order.actual_delivery_date,
            "remark": order.remark,
            "createdBy": order.created_by,
            "createdAt": order.created_at,
            "updatedAt": order.updated_at,
            "items": []
        }
        
        # 处理订单明细
        for item in items:
            # 获取商品信息
            product_result = await db.execute(
                select(Product).where(Product.uuid == item.product_uuid)
            )
            product = product_result.scalar_one_or_none()
            
            # 获取产品型号信息
            model_name = None
            if item.model_uuid:
                model_result = await db.execute(
                    select(ProductModel).where(ProductModel.uuid == item.model_uuid)
                )
                model = model_result.scalar_one_or_none()
                if model:
                    model_name = model.model_name
            
            item_response = {
                "uuid": item.uuid,
                "purchaseOrderUuid": item.purchase_order_uuid,
                "productUuid": item.product_uuid,
                "productName": product.product_name if product else "未知商品",
                "modelUuid": item.model_uuid,
                "modelName": model_name,
                "selectedSpecification": item.selected_specification,
                "quantity": item.quantity,
                "unitPrice": item.unit_price,
                "totalPrice": item.total_price,
                "receivedQuantity": item.received_quantity,
                "notes": item.remark,
                "createdAt": item.created_at
            }
            order_response["items"].append(item_response)
        
        order_responses.append(order_response)
    
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
        message="获取采购订单列表成功"
    )


@router.get("/PurchaseOrders/{order_uuid}", response_model=ApiResponse[PurchaseOrderResponse])
async def get_purchase_order(order_uuid: str, db: AsyncSession = Depends(get_async_db)):
    """获取单个采购订单"""
    result = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.uuid == order_uuid)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在",
        )
    
    # 获取供应商信息
    supplier_result = await db.execute(
        select(Supplier).where(Supplier.uuid == order.supplier_uuid)
    )
    supplier = supplier_result.scalar_one_or_none()
    
    # 获取订单明细
    items_result = await db.execute(
        select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_uuid == order.uuid)
    )
    items = items_result.scalars().all()
    
    # 手动构建响应数据，包含供应商名称
    order_response = {
        "uuid": order.uuid,
        "orderNumber": order.order_number,
        "supplierUuid": order.supplier_uuid,
        "supplierName": supplier.supplier_name if supplier else "未知供应商",
        "orderDate": order.order_date,
        "expectedDeliveryDate": order.expected_delivery_date,
        "actualDeliveryDate": order.actual_delivery_date,
        "totalAmount": order.total_amount,
        "status": order.status,
        "remark": order.remark,
        "createdBy": order.created_by,
        "createdAt": order.created_at,
        "updatedAt": order.updated_at,
        "items": []
    }
    
    # 处理订单明细
    for item in items:
        # 获取商品信息
        product_result = await db.execute(
            select(Product).where(Product.uuid == item.product_uuid)
        )
        product = product_result.scalar_one_or_none()
        
        # 获取产品型号信息
        model_name = None
        if item.model_uuid:
            model_result = await db.execute(
                select(ProductModel).where(ProductModel.uuid == item.model_uuid)
            )
            model = model_result.scalar_one_or_none()
            if model:
                model_name = model.model_name
        
        item_response = {
            "uuid": item.uuid,
            "purchaseOrderUuid": item.purchase_order_uuid,
            "productUuid": item.product_uuid,
            "productName": product.product_name if product else "未知商品",
            "modelUuid": item.model_uuid,
            "modelName": model_name,
            "selectedSpecification": item.selected_specification,
            "quantity": item.quantity,
            "unitPrice": item.unit_price,
            "totalPrice": item.total_price,
            "receivedQuantity": item.received_quantity,
            "notes": item.remark,
            "createdAt": item.created_at,
            "updatedAt": None,
        }
        order_response["items"].append(item_response)
    
    return ApiResponse(
        success=True,
        data=order_response,
        message="获取采购订单成功"
    )


@router.post("/PurchaseOrders", response_model=ApiResponse[PurchaseOrderResponse])
async def create_purchase_order(
    order_data: PurchaseOrderCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """创建采购订单"""
    # 处理modelUuid字段，将空字符串转换为None
    processed_items = []
    for item in order_data.items:
        # 如果modelUuid是空字符串，转换为None
        model_uuid = item.modelUuid if item.modelUuid != "" else None
        processed_item = PurchaseOrderItemCreate(
            productUuid=item.productUuid,
            modelUuid=model_uuid,
            selectedSpecification=item.selectedSpecification,
            quantity=item.quantity,
            unitPrice=item.unitPrice,
            remark=item.remark
        )
        processed_items.append(processed_item)
    
    # 使用处理后的items数据
    processed_order_data = PurchaseOrderCreate(
        supplierUuid=order_data.supplierUuid,
        orderDate=order_data.orderDate,
        expectedDeliveryDate=order_data.expectedDeliveryDate,
        remark=order_data.remark,
        items=processed_items
    )
    
    # 检查供应商是否存在
    result = await db.execute(select(Supplier).where(Supplier.uuid == processed_order_data.supplierUuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="供应商不存在",
        )
    
    # 检查产品是否存在
    from app.models.product import Product
    for item in processed_order_data.items:
        result = await db.execute(select(Product).where(Product.uuid == item.productUuid))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"产品 {item.productUuid} 不存在",
            )
    
    # 创建采购订单
    # 使用第一个管理员用户的UUID作为创建者（临时解决方案）
    result = await db.execute(select(User).where(User.role == 'admin').limit(1))
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统中没有管理员用户，无法创建采购订单",
        )
    
    order = PurchaseOrder(
        order_number=generate_order_number(),
        supplier_uuid=processed_order_data.supplierUuid,
        order_date=processed_order_data.orderDate or datetime.now(),
        expected_delivery_date=processed_order_data.expectedDeliveryDate,
        total_amount=0.0,  # 将在计算明细后更新
        status="PENDING",
        remark=processed_order_data.remark,
        created_by=admin_user.uuid,  # 使用管理员用户的UUID
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # 创建订单明细并计算总金额
    total_amount = 0.0
    for item_data in processed_order_data.items:
        item_total = item_data.quantity * item_data.unitPrice
        total_amount += item_total
        
        item = PurchaseOrderItem(
            purchase_order_uuid=order.uuid,
            product_uuid=item_data.productUuid,
            model_uuid=item_data.modelUuid,
            selected_specification=item_data.selectedSpecification,
            quantity=item_data.quantity,
            unit_price=item_data.unitPrice,
            total_price=item_total,
            remark=item_data.remark,
        )
        
        db.add(item)
    
    # 更新订单总金额
    order.total_amount = total_amount
    await db.commit()
    await db.refresh(order)
    
    # 获取订单明细用于响应，同时获取产品信息
    from app.models.product import Product
    from app.models.product_model import ProductModel
    
    items_result = await db.execute(
        select(PurchaseOrderItem, Product, ProductModel)
        .join(Product, PurchaseOrderItem.product_uuid == Product.uuid)
        .outerjoin(ProductModel, PurchaseOrderItem.model_uuid == ProductModel.uuid)
        .where(PurchaseOrderItem.purchase_order_uuid == order.uuid)
    )
    items_with_products = items_result.all()
    
    order_response = PurchaseOrderResponse(
        uuid=order.uuid,
        orderNumber=order.order_number,
        supplierUuid=order.supplier_uuid,
        supplierName=supplier.supplier_name if supplier else "未知供应商",
        orderDate=order.order_date,
        expectedDeliveryDate=order.expected_delivery_date,
        totalAmount=order.total_amount,
        status=order.status,
        actualDeliveryDate=order.actual_delivery_date,
        remark=order.remark,
        createdBy=order.created_by,
        createdAt=order.created_at,
        updatedAt=order.updated_at,
        items=[
            PurchaseOrderItemResponse(
                uuid=item.uuid,
                purchaseOrderUuid=item.purchase_order_uuid,
                productUuid=item.product_uuid,
                productName=product.product_name if product else "未知产品",
                modelUuid=item.model_uuid,
                modelName=product_model.model_name if product_model else None,
                selectedSpecification=item.selected_specification,
                quantity=item.quantity,
                unitPrice=item.unit_price,
                totalPrice=item.total_price,
                receivedQuantity=item.received_quantity,
                remark=item.remark,
                createdAt=item.created_at,
                updatedAt=item.created_at,  # PurchaseOrderItem没有updated_at字段，使用created_at
            )
            for item, product, product_model in items_with_products
        ]
    )
    
    return ApiResponse(
        success=True,
        data=order_response,
        message="采购订单创建成功"
    )


@router.put("/PurchaseOrders/{order_uuid}", response_model=ApiResponse[PurchaseOrderResponse])
async def update_purchase_order(
    order_uuid: str, 
    order_data: PurchaseOrderUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """更新采购订单信息"""
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.uuid == order_uuid))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在",
        )
    
    # 更新订单信息
    supplier = None
    if order_data.supplierUuid is not None:
        # 检查供应商是否存在
        supplier_result = await db.execute(select(Supplier).where(Supplier.uuid == order_data.supplierUuid))
        supplier = supplier_result.scalar_one_or_none()
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="供应商不存在",
            )
        order.supplier_uuid = order_data.supplierUuid
    else:
        # 获取当前订单的供应商信息
        supplier_result = await db.execute(select(Supplier).where(Supplier.uuid == order.supplier_uuid))
        supplier = supplier_result.scalar_one_or_none()
    
    if order_data.orderDate is not None:
        order.order_date = order_data.orderDate
    
    if order_data.expectedDeliveryDate is not None:
        order.expected_delivery_date = order_data.expectedDeliveryDate
    
    if order_data.actualDeliveryDate is not None:
        order.actual_delivery_date = order_data.actualDeliveryDate
    
    if order_data.remark is not None:
        order.remark = order_data.remark
    
    # 处理订单明细更新
    if order_data.items is not None:
        # 先删除原有的订单明细
        items_result = await db.execute(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_uuid == order_uuid)
        )
        existing_items = items_result.scalars().all()
        
        for item in existing_items:
            await db.delete(item)
        
        # 创建新的订单明细并计算总金额
        total_amount = 0.0
        for item_data in order_data.items:
            # 检查产品是否存在
            product_result = await db.execute(select(Product).where(Product.uuid == item_data.productUuid))
            product = product_result.scalar_one_or_none()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"产品 {item_data.productUuid} 不存在",
                )
            
            item_total = item_data.quantity * item_data.unitPrice
            total_amount += item_total
            
            # 处理modelUuid字段，将空字符串转换为None
            model_uuid = item_data.modelUuid if item_data.modelUuid != "" else None
            
            item = PurchaseOrderItem(
                purchase_order_uuid=order.uuid,
                product_uuid=item_data.productUuid,
                model_uuid=model_uuid,
                selected_specification=item_data.selectedSpecification,
                quantity=item_data.quantity,
                unit_price=item_data.unitPrice,
                total_price=item_total,
                remark=item_data.remark,
            )
            
            db.add(item)
        
        # 更新订单总金额
        order.total_amount = total_amount
    
    await db.commit()
    await db.refresh(order)
    
    # 获取订单明细及相关产品信息
    items_with_products = await db.execute(
        select(PurchaseOrderItem, Product, ProductModel)
        .select_from(PurchaseOrderItem)
        .outerjoin(Product, PurchaseOrderItem.product_uuid == Product.uuid)
        .outerjoin(ProductModel, PurchaseOrderItem.model_uuid == ProductModel.uuid)
        .where(PurchaseOrderItem.purchase_order_uuid == order.uuid)
    )
    items_with_products = items_with_products.all()
    
    order_response = PurchaseOrderResponse(
        uuid=order.uuid,
        orderNumber=order.order_number,
        supplierUuid=order.supplier_uuid,
        supplierName=supplier.supplier_name if supplier else "未知供应商",
        orderDate=order.order_date,
        expectedDeliveryDate=order.expected_delivery_date,
        actualDeliveryDate=order.actual_delivery_date,
        totalAmount=order.total_amount,
        status=order.status,
        remark=order.remark,
        createdBy=order.created_by,
        createdAt=order.created_at,
        updatedAt=order.updated_at,
        items=[
            PurchaseOrderItemResponse(
                uuid=item.uuid,
                purchaseOrderUuid=item.purchase_order_uuid,
                productUuid=item.product_uuid,
                productName=product.product_name if product else "未知产品",
                modelUuid=item.model_uuid,
                modelName=product_model.model_name if product_model else None,
                selectedSpecification=item.selected_specification,
                quantity=item.quantity,
                unitPrice=item.unit_price,
                totalPrice=item.total_price,
                receivedQuantity=item.received_quantity,
                remark=item.remark,
                createdAt=item.created_at,
                updatedAt=item.created_at,  # PurchaseOrderItem没有updated_at字段，使用created_at
            )
            for item, product, product_model in items_with_products
        ]
    )
    
    return ApiResponse(
        success=True,
        data=order_response,
        message="采购订单更新成功"
    )


@router.delete("/PurchaseOrders/{order_uuid}", response_model=ApiResponse[dict])
async def delete_purchase_order(order_uuid: str, db: AsyncSession = Depends(get_async_db)):
    """删除采购订单（硬删除）"""
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.uuid == order_uuid))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在",
        )
    
    # 先删除关联的订单明细
    items_result = await db.execute(
        select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_uuid == order_uuid)
    )
    items = items_result.scalars().all()
    
    for item in items:
        await db.delete(item)
    
    # 再删除采购订单
    await db.delete(order)
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"message": "采购订单删除成功"},
        message="采购订单删除成功"
    )