"""
产品分类管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import re

from app.core.database import get_db
from app.models.product_category import ProductCategory
from app.schemas.product_category import (
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse,
    ProductCategoryListResponse, ProductCategoryTreeResponse, ProductCategoryWithChildren
)
from app.schemas.response import ApiResponse, PaginatedResponse, ApiPaginatedResponse
from app.utils.mapper import snake_to_camel, camel_to_snake, model_to_dict, model_list_to_dict_list, paginate_response

router = APIRouter()


@router.get("/ProductCategories", response_model=ApiPaginatedResponse[ProductCategoryResponse])
async def get_product_categories(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    parent_uuid: Optional[str] = Query(None, description="父级分类UUID"),
    db: AsyncSession = Depends(get_db)
):
    """获取产品分类列表"""
    # 构建查询条件
    query = select(ProductCategory).where(ProductCategory.is_active == True)
    
    if search:
        query = query.where(
            or_(
                ProductCategory.category_name.ilike(f"%{search}%"),
                ProductCategory.category_code.ilike(f"%{search}%"),
                ProductCategory.description.ilike(f"%{search}%")
            )
        )
    
    if parent_uuid:
        query = query.where(ProductCategory.parent_uuid == parent_uuid)
    # 如果没有提供parent_uuid参数，则显示所有分类（包括有父分类的子分类）
    
    # 获取总数
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(ProductCategory.sort_order, ProductCategory.category_name)
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    categories = result.scalars().all()
    
    # 使用自动映射工具转换响应格式
    category_dicts = model_list_to_dict_list(categories)
    category_responses = snake_to_camel(category_dicts)
    
    paginated_data = PaginatedResponse(
        items=category_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取产品分类列表成功"
    )


@router.get("/ProductCategories/tree", response_model=ApiResponse[ProductCategoryTreeResponse])
async def get_product_category_tree(db: AsyncSession = Depends(get_db)):
    """获取产品分类树形结构"""
    # 获取所有激活的分类
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.is_active == True)
    )
    all_categories = result.scalars().all()
    
    # 构建树形结构
    category_dict = {}
    root_categories = []
    
    # 首先将所有分类存入字典
    for category in all_categories:
        category_dict[str(category.uuid)] = {
            'category': category,
            'children': []
        }
    
    # 构建父子关系
    for category in all_categories:
        if category.parent_uuid:
            parent_uuid = str(category.parent_uuid)
            if parent_uuid in category_dict:
                category_dict[parent_uuid]['children'].append(category_dict[str(category.uuid)])
        else:
            root_categories.append(category_dict[str(category.uuid)])
    
    # 转换为响应格式
    def build_tree_response(categories):
        result = []
        for item in categories:
            category = item['category']
            category_dict = model_to_dict(category)
            category_response = snake_to_camel(category_dict)
            
            # 递归处理子分类
            children = build_tree_response(item['children'])
            
            result.append(ProductCategoryWithChildren(
                **category_response,
                children=children
            ))
        return result
    
    tree_items = build_tree_response(root_categories)
    
    return ApiResponse(
        success=True,
        data=ProductCategoryTreeResponse(
            items=tree_items,
            total=len(all_categories)
        ),
        message="获取产品分类树成功"
    )


@router.get("/ProductCategories/{category_uuid}", response_model=ApiResponse[ProductCategoryResponse])
async def get_product_category(category_uuid: str, db: AsyncSession = Depends(get_db)):
    """获取单个产品分类"""
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.uuid == category_uuid, ProductCategory.is_active == True)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品分类不存在",
        )
    
    # 使用自动映射工具转换响应格式
    category_dict = model_to_dict(category)
    category_response = snake_to_camel(category_dict)
    
    return ApiResponse(
        success=True,
        data=category_response,
        message="获取产品分类成功"
    )


@router.post("/ProductCategories", response_model=ApiResponse[ProductCategoryResponse])
async def create_product_category(category_data: ProductCategoryCreate, db: AsyncSession = Depends(get_db)):
    """创建新产品分类"""
    # 导入编码生成工具
    from app.utils.code_generator import generate_unique_product_category_code
    
    # 自动生成产品分类编码
    category_code = await generate_unique_product_category_code(db)
    
    # 检查分类编码是否已存在
    result = await db.execute(select(ProductCategory).where(ProductCategory.category_code == category_code))
    existing_category = result.scalar_one_or_none()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品分类编码已存在",
        )
    
    # 检查父级分类是否存在（如果提供了父级UUID）
    if category_data.parentUuid:
        # 直接使用_ensure_uuid_format确保UUID格式正确
        from app.utils.mapper import _ensure_uuid_format
        parent_uuid = _ensure_uuid_format(category_data.parentUuid)
        result = await db.execute(select(ProductCategory).where(ProductCategory.uuid == parent_uuid, ProductCategory.is_active == True))
        parent_category = result.scalar_one_or_none()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父级分类不存在",
            )
    
    # 将前端的大驼峰数据转换为蛇形命名
    db_data = camel_to_snake(category_data.dict())
    # 使用生成的编码替换前端传入的编码
    db_data['category_code'] = category_code
    
    # 创建新产品分类
    product_category = ProductCategory(**db_data)
    
    db.add(product_category)
    await db.commit()
    await db.refresh(product_category)
    
    # 使用自动映射工具转换响应格式
    category_dict = model_to_dict(product_category)
    category_response = snake_to_camel(category_dict)
    
    return ApiResponse(
        success=True,
        data=category_response,
        message="产品分类创建成功"
    )


@router.put("/ProductCategories/{category_uuid}", response_model=ApiResponse[ProductCategoryResponse])
async def update_product_category(
    category_uuid: str, 
    category_data: ProductCategoryUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新产品分类信息"""
    result = await db.execute(select(ProductCategory).where(ProductCategory.uuid == category_uuid))
    product_category = result.scalar_one_or_none()
    
    if not product_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品分类不存在",
        )
    
    # 将前端的大驼峰数据转换为蛇形命名，并过滤掉None值
    update_data = {}
    for key, value in category_data.dict(exclude_unset=True).items():
        if value is not None:
            # 正确使用camel_to_snake函数转换单个键
            snake_key = re.sub(r'([A-Z])', r'_\1', key).lower()
            if snake_key.startswith('_'):
                snake_key = snake_key[1:]
            update_data[snake_key] = value
    
    # 特殊处理分类编码冲突检查
    if 'category_code' in update_data and update_data['category_code'] != product_category.category_code:
        result = await db.execute(
            select(ProductCategory).where(
                ProductCategory.category_code == update_data['category_code'],
                ProductCategory.uuid != category_uuid
            )
        )
        existing_category = result.scalar_one_or_none()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="产品分类编码已存在",
            )
    
    # 检查父级分类是否存在（如果提供了父级UUID）
    if 'parent_uuid' in update_data and update_data['parent_uuid']:
        result = await db.execute(select(ProductCategory).where(ProductCategory.uuid == update_data['parent_uuid'], ProductCategory.is_active == True))
        parent_category = result.scalar_one_or_none()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父级分类不存在",
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(product_category, key, value)
    
    await db.commit()
    await db.refresh(product_category)
    
    # 使用自动映射工具转换响应格式
    category_dict = model_to_dict(product_category)
    category_response = snake_to_camel(category_dict)
    
    return ApiResponse(
        success=True,
        data=category_response,
        message="产品分类更新成功"
    )


@router.delete("/ProductCategories/{category_uuid}", response_model=ApiResponse)
async def delete_product_category(category_uuid: str, db: AsyncSession = Depends(get_db)):
    """删除产品分类（软删除）"""
    result = await db.execute(select(ProductCategory).where(ProductCategory.uuid == category_uuid))
    product_category = result.scalar_one_or_none()
    
    if not product_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品分类不存在",
        )
    
    # 检查是否有子分类
    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.parent_uuid == category_uuid,
            ProductCategory.is_active == True
        )
    )
    children = result.scalars().all()
    
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下存在子分类，无法删除",
        )
    
    # 软删除
    product_category.is_active = False
    await db.commit()
    
    return ApiResponse(
        success=True,
        data=None,
        message="产品分类删除成功"
    )