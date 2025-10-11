"""
客户管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerResponse, 
    CustomerCreate, 
    CustomerUpdate, 
    CustomerListResponse
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import snake_to_camel, snake_to_pascal, camel_to_snake, model_to_dict, model_list_to_dict_list, paginate_response

router = APIRouter()


@router.get("/Customers", response_model=ApiPaginatedResponse[CustomerResponse])
async def get_customers(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: str = Query(None, description="搜索关键词"),
    is_active: bool = Query(None, description="是否激活过滤"),
):
    """获取客户列表"""
    # 构建查询条件
    query = select(Customer).where(Customer.deleted_at.is_(None))
    
    if search:
        query = query.where(
            or_(
                Customer.customer_name.ilike(f"%{search}%"),
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.contact_person.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.where(Customer.is_active == is_active)
    
    # 获取总数
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    customers = result.scalars().all()
    
    # 使用自动映射工具转换响应格式
    customer_dicts = model_list_to_dict_list(customers)
    customer_responses = snake_to_camel(customer_dicts)
    
    paginated_data = PaginatedResponse(
        items=customer_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取客户列表成功"
    )


@router.get("/Customers/{customer_uuid}", response_model=ApiResponse[CustomerResponse])
async def get_customer(customer_uuid: str, db: AsyncSession = Depends(get_db)):
    """获取单个客户"""
    result = await db.execute(
        select(Customer).where(Customer.uuid == customer_uuid, Customer.deleted_at.is_(None))
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )
    
    # 使用自动映射工具转换响应格式
    customer_dict = model_to_dict(customer)
    customer_response = snake_to_camel(customer_dict)
    
    return ApiResponse(
        success=True,
        data=customer_response,
        message="获取客户成功"
    )


@router.post("/Customers", response_model=ApiResponse[CustomerResponse])
async def create_customer(customer_data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    """创建客户"""
    # 导入编码生成工具
    from app.utils.code_generator import generate_unique_customer_code
    
    # 自动生成客户编码
    customer_code = await generate_unique_customer_code(db)
    
    # 检查客户编码是否已存在
    result = await db.execute(
        select(Customer).where(Customer.customer_code == customer_code)
    )
    existing_customer = result.scalar_one_or_none()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="客户编码已存在",
        )
    
    # 创建客户
    customer = Customer(
        customer_name=customer_data.customerName,
        customer_code=customer_code,
        contact_person=customer_data.contactPerson,
        phone=customer_data.phone,
        email=customer_data.email,
        address=customer_data.address,
    )
    
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    
    # 直接使用Pydantic模型转换，避免映射工具可能的问题
    customer_response = CustomerResponse(
        uuid=customer.uuid,
        customerName=customer.customer_name,
        customerCode=customer.customer_code,
        contactPerson=customer.contact_person,
        phone=customer.phone,
        email=customer.email,
        address=customer.address,
        isActive=customer.is_active,
        createdAt=customer.created_at,
        updatedAt=customer.updated_at,
        deletedAt=customer.deleted_at
    )
    
    return ApiResponse(
        success=True,
        data=customer_response,
        message="客户创建成功"
    )


@router.put("/Customers/{customer_uuid}", response_model=ApiResponse[CustomerResponse])
async def update_customer(
    customer_uuid: str, 
    customer_data: CustomerUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新客户信息"""
    result = await db.execute(
        select(Customer).where(Customer.uuid == customer_uuid, Customer.deleted_at.is_(None))
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )
    
    # 检查客户编码是否已存在（如果更新了编码）
    if customer_data.customer_code and customer_data.customer_code != customer.customer_code:
        result = await db.execute(
            select(Customer).where(Customer.customer_code == customer_data.customer_code)
        )
        existing_customer = result.scalar_one_or_none()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="客户编码已存在",
            )
    
    # 更新客户信息
    if customer_data.customer_name is not None:
        customer.customer_name = customer_data.customer_name
    
    if customer_data.customer_code is not None:
        customer.customer_code = customer_data.customer_code
    
    if customer_data.contact_person is not None:
        customer.contact_person = customer_data.contact_person
    
    if customer_data.phone is not None:
        customer.phone = customer_data.phone
    
    if customer_data.email is not None:
        customer.email = customer_data.email
    
    if customer_data.address is not None:
        customer.address = customer_data.address
    
    if customer_data.is_active is not None:
        customer.is_active = customer_data.is_active
    
    await db.commit()
    await db.refresh(customer)
    
    # 使用自动映射工具转换响应格式
    customer_dict = model_to_dict(customer)
    customer_response = snake_to_camel(customer_dict)
    
    return ApiResponse(
        success=True,
        data=customer_response,
        message="客户更新成功"
    )


@router.delete("/Customers/{customer_uuid}", response_model=ApiResponse[dict])
async def delete_customer(customer_uuid: str, db: AsyncSession = Depends(get_db)):
    """删除客户（软删除）"""
    result = await db.execute(
        select(Customer).where(Customer.uuid == customer_uuid, Customer.deleted_at.is_(None))
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )
    
    # 软删除：设置删除时间
    customer.deleted_at = datetime.now()
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"message": "客户删除成功"},
        message="客户删除成功"
    )