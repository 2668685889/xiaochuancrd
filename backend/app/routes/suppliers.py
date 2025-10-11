"""
供应商管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from app.core.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierResponse, 
    SupplierCreate, 
    SupplierUpdate, 
    SupplierListResponse
)
from app.schemas.response import ApiResponse, ApiPaginatedResponse, PaginatedResponse
from app.utils.mapper import snake_to_camel, camel_to_snake, model_to_dict, model_list_to_dict_list, paginate_response

router = APIRouter()


@router.get("/Suppliers", response_model=ApiPaginatedResponse[SupplierResponse])
async def get_suppliers(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """获取供应商列表"""
    # 构建查询条件
    query = select(Supplier).where(Supplier.is_active == True)
    
    if search:
        query = query.where(
            or_(
                Supplier.supplier_name.ilike(f"%{search}%"),
                Supplier.supplier_code.ilike(f"%{search}%"),
                Supplier.contact_person.ilike(f"%{search}%"),
                Supplier.phone.ilike(f"%{search}%"),
                Supplier.email.ilike(f"%{search}%")
            )
        )
    
    # 获取总数
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    suppliers = result.scalars().all()
    
    # 使用自动映射工具转换响应格式
    supplier_dicts = model_list_to_dict_list(suppliers)
    supplier_responses = snake_to_camel(supplier_dicts)
    
    paginated_data = PaginatedResponse(
        items=supplier_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
    
    return ApiResponse(
        success=True,
        data=paginated_data,
        message="获取供应商列表成功"
    )


@router.get("/Suppliers/{supplier_uuid}", response_model=ApiResponse[SupplierResponse])
async def get_supplier(supplier_uuid: str, db: AsyncSession = Depends(get_db)):
    """获取单个供应商"""
    result = await db.execute(
        select(Supplier).where(Supplier.uuid == supplier_uuid, Supplier.is_active == True)
    )
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在",
        )
    
    # 使用自动映射工具转换响应格式
    supplier_dict = model_to_dict(supplier)
    supplier_response = snake_to_camel(supplier_dict)
    
    return ApiResponse(
        success=True,
        data=supplier_response,
        message="获取供应商成功"
    )


@router.post("/Suppliers", response_model=ApiResponse[SupplierResponse])
async def create_supplier(supplier_data: SupplierCreate, db: AsyncSession = Depends(get_db)):
    """创建新供应商"""
    # 导入编码生成工具
    from app.utils.code_generator import generate_unique_supplier_code
    
    # 自动生成供应商编码
    supplier_code = await generate_unique_supplier_code(db)
    
    # 创建新供应商
    supplier = Supplier(
        supplier_name=supplier_data.supplierName,
        supplier_code=supplier_code,
        contact_person=supplier_data.contactPerson,
        phone=supplier_data.phone,
        email=supplier_data.email,
        address=supplier_data.address,
    )
    
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    
    supplier_response = SupplierResponse(
        uuid=supplier.uuid,
        supplierName=supplier.supplier_name,
        supplierCode=supplier.supplier_code,
        contactPerson=supplier.contact_person,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        isActive=supplier.is_active,
        createdAt=supplier.created_at,
        updatedAt=supplier.updated_at,
    )
    
    return ApiResponse(
        success=True,
        data=supplier_response,
        message="供应商创建成功"
    )


@router.put("/Suppliers/{supplier_uuid}", response_model=ApiResponse[SupplierResponse])
async def update_supplier(
    supplier_uuid: str, 
    supplier_data: SupplierUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新供应商信息"""
    result = await db.execute(select(Supplier).where(Supplier.uuid == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在",
        )
    
    # 更新供应商信息
    if supplier_data.supplierName is not None:
        supplier.supplier_name = supplier_data.supplierName
    
    if supplier_data.supplierCode is not None:
        # 检查供应商编码是否与其他供应商冲突
        if supplier_data.supplierCode != supplier.supplier_code:
            result = await db.execute(
                select(Supplier).where(
                    Supplier.supplier_code == supplier_data.supplierCode,
                    Supplier.uuid != supplier_uuid
                )
            )
            existing_supplier = result.scalar_one_or_none()
            
            if existing_supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="供应商编码已存在",
                )
        supplier.supplier_code = supplier_data.supplierCode
    
    if supplier_data.contactPerson is not None:
        supplier.contact_person = supplier_data.contactPerson
    
    if supplier_data.phone is not None:
        supplier.phone = supplier_data.phone
    
    if supplier_data.email is not None:
        supplier.email = supplier_data.email
    
    if supplier_data.address is not None:
        supplier.address = supplier_data.address
    
    if supplier_data.isActive is not None:
        supplier.is_active = supplier_data.isActive
    
    await db.commit()
    await db.refresh(supplier)
    
    supplier_response = SupplierResponse(
        uuid=supplier.uuid,
        supplierName=supplier.supplier_name,
        supplierCode=supplier.supplier_code,
        contactPerson=supplier.contact_person,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        isActive=supplier.is_active,
        createdAt=supplier.created_at,
        updatedAt=supplier.updated_at,
    )
    
    return ApiResponse(
        success=True,
        data=supplier_response,
        message="供应商更新成功"
    )


@router.delete("/Suppliers/{supplier_uuid}", response_model=ApiResponse[dict])
async def delete_supplier(supplier_uuid: str, db: AsyncSession = Depends(get_db)):
    """删除供应商（软删除）"""
    result = await db.execute(select(Supplier).where(Supplier.uuid == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在",
        )
    
    # 检查是否有产品关联该供应商
    from app.models.product import Product
    result = await db.execute(
        select(Product).where(
            Product.supplier_uuid == supplier_uuid, 
            Product.is_active == True
        )
    )
    related_products = result.scalars().all()
    
    if related_products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该供应商下有关联的产品，无法删除",
        )
    
    # 软删除：标记为不活跃
    supplier.is_active = False
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"message": "供应商删除成功"},
        message="供应商删除成功"
    )