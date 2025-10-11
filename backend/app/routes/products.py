"""
产品管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from app.core.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.product_model import ProductModel
from app.schemas.product import (
    ProductResponse, 
    ProductCreate, 
    ProductUpdate, 
    ProductListResponse
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import snake_to_camel, snake_to_pascal, camel_to_snake, model_to_dict, model_list_to_dict_list, paginate_response

router = APIRouter()


@router.get("/Products", response_model=ApiPaginatedResponse[ProductResponse])
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """获取产品列表"""
    # 构建查询条件，包含关联的供货商和产品型号
    query = (
        select(Product, Supplier.supplier_name, ProductModel.model_name, ProductModel.specifications)
        .outerjoin(Supplier, Product.supplier_uuid == Supplier.uuid)
        .outerjoin(ProductModel, Product.model_uuid == ProductModel.uuid)
        .where(Product.is_active == True)
    )
    
    if search:
        query = query.where(
            or_(
                Product.product_name.ilike(f"%{search}%"),
                Product.product_code.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Supplier.supplier_name.ilike(f"%{search}%"),
                ProductModel.model_name.ilike(f"%{search}%")
            )
        )
    
    # 获取总数
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    products_with_relations = result.all()
    
    # 处理查询结果，将关联数据合并到产品对象中
    products_with_extra_data = []
    for product, supplier_name, model_name, specifications in products_with_relations:
        product_dict = model_to_dict(product)
        # 添加关联的供货商和产品型号信息
        product_dict['supplier_name'] = supplier_name
        product_dict['model_name'] = model_name
        product_dict['specifications'] = specifications or {}
        products_with_extra_data.append(product_dict)
    
    # 使用自动映射工具转换响应格式（使用小驼峰命名）
    product_responses = snake_to_camel(products_with_extra_data)
    
    paginated_data = PaginatedResponse(
        items=product_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取产品列表成功"
    )


@router.get("/Products/{product_uuid}", response_model=ApiResponse[ProductResponse])
async def get_product(product_uuid: str, db: AsyncSession = Depends(get_db)):
    """获取单个产品"""
    # 构建查询条件，包含关联的供货商和产品型号
    query = (
        select(Product, Supplier.supplier_name, ProductModel.model_name, ProductModel.specifications)
        .outerjoin(Supplier, Product.supplier_uuid == Supplier.uuid)
        .outerjoin(ProductModel, Product.model_uuid == ProductModel.uuid)
        .where(Product.uuid == product_uuid, Product.is_active == True)
    )
    
    result = await db.execute(query)
    product_with_relations = result.first()
    
    if not product_with_relations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )
    
    product, supplier_name, model_name, specifications = product_with_relations
    
    # 使用自动映射工具转换响应格式，并添加关联数据
    product_dict = model_to_dict(product)
    product_dict['supplier_name'] = supplier_name
    product_dict['model_name'] = model_name
    product_dict['specifications'] = specifications or {}
    product_response = snake_to_camel(product_dict)
    
    return ApiResponse(
        success=True,
        data=product_response,
        message="获取产品成功"
    )


@router.post("/Products", response_model=ApiResponse[ProductResponse])
async def create_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """创建新产品"""
    # 导入编码生成工具
    from app.utils.code_generator import generate_unique_product_code
    
    # 自动生成产品编码
    product_code = await generate_unique_product_code(db)
    
    # 检查产品编码是否已存在
    result = await db.execute(select(Product).where(Product.product_code == product_code))
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品编码已存在",
        )
    
    # 将前端的大驼峰数据转换为蛇形命名
    db_data = camel_to_snake(product_data.dict())
    # 使用生成的编码替换前端传入的编码
    db_data['product_code'] = product_code
    
    # 创建新产品
    product = Product(**db_data)
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    # 使用自动映射工具转换响应格式
    product_dict = model_to_dict(product)
    product_response = snake_to_camel(product_dict)
    
    return ApiResponse(
        success=True,
        data=product_response,
        message="产品创建成功"
    )


@router.put("/Products/{product_uuid}", response_model=ApiResponse[ProductResponse])
async def update_product(
    product_uuid: str, 
    product_data: ProductUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新产品信息"""
    result = await db.execute(select(Product).where(Product.uuid == product_uuid))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )
    
    # 将前端的大驼峰数据转换为蛇形命名，并过滤掉None值
    update_data = {}
    for key, value in product_data.dict(exclude_unset=True).items():
        if value is not None:
            snake_key = camel_to_snake({key: value})[key]
            update_data[snake_key] = value
    
    # 特殊处理产品编码冲突检查
    if 'product_code' in update_data and update_data['product_code'] != product.product_code:
        result = await db.execute(
            select(Product).where(
                Product.product_code == update_data['product_code'],
                Product.uuid != product_uuid
            )
        )
        existing_product = result.scalar_one_or_none()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="产品编码已存在",
            )
    

    

    
    # 更新产品信息
    for key, value in update_data.items():
        setattr(product, key, value)
    
    await db.commit()
    await db.refresh(product)
    
    # 使用自动映射工具转换响应格式
    product_dict = model_to_dict(product)
    product_response = snake_to_camel(product_dict)
    
    return ApiResponse(
        success=True,
        data=product_response,
        message="产品更新成功"
    )


@router.delete("/Products/{product_uuid}", response_model=ApiResponse[dict])
async def delete_product(product_uuid: str, db: AsyncSession = Depends(get_db)):
    """删除产品（软删除）"""
    result = await db.execute(select(Product).where(Product.uuid == product_uuid))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )
    
    # 软删除：标记为不活跃
    product.is_active = False
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"message": "产品删除成功"},
        message="产品删除成功"
    )