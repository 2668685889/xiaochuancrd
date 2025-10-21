"""
产品型号管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from app.core.database import get_async_db
from app.models.product_model import ProductModel
from app.schemas.product_model import (
    ProductModelResponse, 
    ProductModelCreate, 
    ProductModelUpdate, 
    ProductModelListResponse
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import snake_to_camel, camel_to_snake, model_to_dict, model_list_to_dict_list, paginate_response

router = APIRouter()


@router.get("/ProductModels", response_model=ApiPaginatedResponse[ProductModelResponse])
async def get_product_models(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    category_uuid: Optional[str] = Query(None, description="产品分类UUID"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取产品型号列表"""
    # 构建查询条件
    query = select(ProductModel).where(ProductModel.is_active == True)
    
    if search:
        query = query.where(
            or_(
                ProductModel.model_name.ilike(f"%{search}%"),
                ProductModel.model_code.ilike(f"%{search}%"),
                ProductModel.description.ilike(f"%{search}%")
            )
        )
    
    if category_uuid:
        query = query.where(ProductModel.category_uuid == category_uuid)
    
    # 获取总数
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    product_models = result.scalars().all()
    
    # 获取分类名称信息
    from app.models.product_category import ProductCategory
    category_uuids = [str(model.category_uuid) for model in product_models if model.category_uuid]
    categories_dict = {}
    if category_uuids:
        categories_result = await db.execute(
            select(ProductCategory).where(ProductCategory.uuid.in_(category_uuids))
        )
        categories = categories_result.scalars().all()
        categories_dict = {str(category.uuid): category.category_name for category in categories}
    
    # 使用自动映射工具转换响应格式，并添加分类名称
    model_dicts = model_list_to_dict_list(product_models)
    model_responses = snake_to_camel(model_dicts)
    
    # 特殊处理规格参数：将字典格式转换为数组格式返回给前端
    for model_response in model_responses:
        if 'specifications' in model_response and isinstance(model_response['specifications'], dict):
            specifications_list = []
            for key, value in model_response['specifications'].items():
                # 解析值和单位
                if isinstance(value, str) and ' ' in value:
                    parts = value.rsplit(' ', 1)
                    if len(parts) == 2:
                        spec_value, unit = parts
                        specifications_list.append({
                            'key': key,
                            'value': spec_value,
                            'unit': unit
                        })
                    else:
                        specifications_list.append({
                            'key': key,
                            'value': value,
                            'unit': ''
                        })
                else:
                    specifications_list.append({
                        'key': key,
                        'value': str(value),
                        'unit': ''
                    })
            model_response['specifications'] = specifications_list
    
    # 添加分类名称信息
    for model_response in model_responses:
        if model_response.get('categoryUuid') and model_response['categoryUuid'] in categories_dict:
            model_response['categoryName'] = categories_dict[model_response['categoryUuid']]
    
    paginated_data = PaginatedResponse(
        items=model_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取产品型号列表成功"
    )


@router.get("/ProductModels/{model_uuid}", response_model=ApiResponse[ProductModelResponse])
async def get_product_model(model_uuid: str, db: AsyncSession = Depends(get_async_db)):
    """获取单个产品型号"""
    result = await db.execute(
        select(ProductModel).where(ProductModel.uuid == model_uuid, ProductModel.is_active == True)
    )
    product_model = result.scalar_one_or_none()
    
    if not product_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品型号不存在",
        )
    
    # 获取分类名称信息
    category_name = None
    if product_model.category_uuid:
        from app.models.product_category import ProductCategory
        result = await db.execute(
            select(ProductCategory).where(ProductCategory.uuid == product_model.category_uuid)
        )
        category = result.scalar_one_or_none()
        category_name = category.category_name if category else None
    
    # 使用自动映射工具转换响应格式
    model_dict = model_to_dict(product_model)
    model_response = snake_to_camel(model_dict)
    
    # 特殊处理规格参数：将字典格式转换为数组格式返回给前端
    if 'specifications' in model_response and isinstance(model_response['specifications'], dict):
        specifications_list = []
        for key, value in model_response['specifications'].items():
            # 解析值和单位
            if isinstance(value, str) and ' ' in value:
                parts = value.rsplit(' ', 1)
                if len(parts) == 2:
                    spec_value, unit = parts
                    specifications_list.append({
                        'key': key,
                        'value': spec_value,
                        'unit': unit
                    })
                else:
                    specifications_list.append({
                        'key': key,
                        'value': value,
                        'unit': ''
                    })
            else:
                specifications_list.append({
                    'key': key,
                    'value': str(value),
                    'unit': ''
                })
        model_response['specifications'] = specifications_list
    
    # 添加分类名称信息
    if category_name:
        model_response['categoryName'] = category_name
    
    return ApiResponse(
        success=True,
        data=model_response,
        message="获取产品型号成功"
    )


@router.post("/ProductModels", response_model=ApiResponse[ProductModelResponse])
async def create_product_model(model_data: ProductModelCreate, db: AsyncSession = Depends(get_async_db)):
    """创建新产品型号"""
    # 导入编码生成工具
    from app.utils.code_generator import generate_unique_product_model_code
    
    # 自动生成产品型号编码
    model_code = await generate_unique_product_model_code(db)
    
    # 检查型号编码是否已存在
    result = await db.execute(select(ProductModel).where(ProductModel.model_code == model_code))
    existing_model = result.scalar_one_or_none()
    
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品型号编码已存在",
        )
    
    # 检查产品分类是否存在
    if model_data.categoryUuid:
        from app.models.product_category import ProductCategory
        result = await db.execute(
            select(ProductCategory).where(
                ProductCategory.uuid == model_data.categoryUuid,
                ProductCategory.is_active == True
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="产品分类不存在",
            )
    
    # 将前端的大驼峰数据转换为蛇形命名
    db_data = camel_to_snake(model_data.dict())
    # 使用生成的编码替换前端传入的编码
    db_data['model_code'] = model_code
    
    # 特殊处理规格参数：将数组格式转换为字典格式
    if 'specifications' in db_data and db_data['specifications']:
        specifications_dict = {}
        for spec in db_data['specifications']:
            if spec.get('key') and spec.get('value'):
                # 如果包含单位，将值和单位组合
                if spec.get('unit'):
                    specifications_dict[spec['key']] = f"{spec['value']} {spec['unit']}"
                else:
                    specifications_dict[spec['key']] = spec['value']
        db_data['specifications'] = specifications_dict
    else:
        db_data['specifications'] = {}
    
    # 创建新产品型号
    product_model = ProductModel(**db_data)
    
    db.add(product_model)
    await db.commit()
    await db.refresh(product_model)
    
    # 使用自动映射工具转换响应格式
    model_dict = model_to_dict(product_model)
    model_response = snake_to_camel(model_dict)
    
    # 特殊处理规格参数：将字典格式转换为数组格式返回给前端
    if 'specifications' in model_response and isinstance(model_response['specifications'], dict):
        specifications_list = []
        for key, value in model_response['specifications'].items():
            # 解析值和单位
            if isinstance(value, str) and ' ' in value:
                parts = value.rsplit(' ', 1)
                if len(parts) == 2:
                    spec_value, unit = parts
                    specifications_list.append({
                        'key': key,
                        'value': spec_value,
                        'unit': unit
                    })
                else:
                    specifications_list.append({
                        'key': key,
                        'value': value,
                        'unit': ''
                    })
            else:
                specifications_list.append({
                    'key': key,
                    'value': str(value),
                    'unit': ''
                })
        model_response['specifications'] = specifications_list
    
    # 调试信息：打印转换后的响应数据
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"创建产品型号响应数据: {model_response}")
    
    return ApiResponse(
        success=True,
        data=model_response,
        message="产品型号创建成功"
    )


@router.put("/ProductModels/{model_uuid}", response_model=ApiResponse[ProductModelResponse])
async def update_product_model(
    model_uuid: str, 
    model_data: ProductModelUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """更新产品型号信息"""
    result = await db.execute(select(ProductModel).where(ProductModel.uuid == model_uuid))
    product_model = result.scalar_one_or_none()
    
    if not product_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品型号不存在",
        )
    
    # 将前端的大驼峰数据转换为蛇形命名，并过滤掉None值
    update_data = {}
    for key, value in model_data.dict(exclude_unset=True).items():
        if value is not None:
            snake_key = camel_to_snake(key)
            update_data[snake_key] = value
    
    # 特殊处理规格参数：将数组格式转换为字典格式
    if 'specifications' in update_data and update_data['specifications'] is not None:
        specifications_dict = {}
        for spec in update_data['specifications']:
            if spec.get('key') and spec.get('value'):
                # 如果包含单位，将值和单位组合
                if spec.get('unit'):
                    specifications_dict[spec['key']] = f"{spec['value']} {spec['unit']}"
                else:
                    specifications_dict[spec['key']] = spec['value']
        update_data['specifications'] = specifications_dict
    
    # 特殊处理型号编码冲突检查
    if 'model_code' in update_data and update_data['model_code'] != product_model.model_code:
        result = await db.execute(
            select(ProductModel).where(
                ProductModel.model_code == update_data['model_code'],
                ProductModel.uuid != model_uuid
            )
        )
        existing_model = result.scalar_one_or_none()
        
        if existing_model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="产品型号编码已存在",
            )
    
    # 检查产品分类是否存在（如果提供了分类UUID）
    if 'category_uuid' in update_data and update_data['category_uuid']:
        from app.models.product_category import ProductCategory
        result = await db.execute(
            select(ProductCategory).where(
                ProductCategory.uuid == update_data['category_uuid'],
                ProductCategory.is_active == True
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="产品分类不存在",
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(product_model, key, value)
    
    await db.commit()
    await db.refresh(product_model)
    
    # 使用自动映射工具转换响应格式
    model_dict = model_to_dict(product_model)
    model_response = snake_to_camel(model_dict)
    
    # 特殊处理规格参数：将字典格式转换为数组格式返回给前端
    if 'specifications' in model_response and isinstance(model_response['specifications'], dict):
        specifications_list = []
        for key, value in model_response['specifications'].items():
            # 解析值和单位
            if isinstance(value, str) and ' ' in value:
                parts = value.rsplit(' ', 1)
                if len(parts) == 2:
                    spec_value, unit = parts
                    specifications_list.append({
                        'key': key,
                        'value': spec_value,
                        'unit': unit
                    })
                else:
                    specifications_list.append({
                        'key': key,
                        'value': value,
                        'unit': ''
                    })
            else:
                specifications_list.append({
                    'key': key,
                    'value': str(value),
                    'unit': ''
                })
        model_response['specifications'] = specifications_list
    
    return ApiResponse(
        success=True,
        data=model_response,
        message="产品型号更新成功"
    )


@router.delete("/ProductModels/{model_uuid}")
async def delete_product_model(model_uuid: str, db: AsyncSession = Depends(get_async_db)):
    """删除产品型号（软删除）"""
    result = await db.execute(select(ProductModel).where(ProductModel.uuid == model_uuid))
    product_model = result.scalar_one_or_none()
    
    if not product_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品型号不存在",
        )
    
    # 检查是否有产品关联此型号
    from app.models.product import Product
    result = await db.execute(
        select(func.count()).where(Product.model_uuid == model_uuid, Product.is_active == True)
    )
    product_count = result.scalar()
    
    if product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该型号已被{product_count}个产品使用，无法删除",
        )
    
    # 软删除
    product_model.is_active = False
    await db.commit()
    
    return ApiResponse(
        success=True,
        message="产品型号删除成功"
    )


@router.get("/ProductModels/categories")
async def get_model_categories(db: AsyncSession = Depends(get_async_db)):
    """获取所有产品分类"""
    result = await db.execute(
        select(ProductModel.category).where(ProductModel.is_active == True).distinct()
    )
    categories = [row[0] for row in result.all()]
    
    return ApiResponse(
        success=True,
        data=categories,
        message="获取产品分类成功"
    )