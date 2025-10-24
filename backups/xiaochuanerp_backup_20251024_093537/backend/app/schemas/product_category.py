"""
产品分类相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ProductCategoryBase(BaseModel):
    """产品分类基础模式"""
    categoryName: str = Field(..., min_length=1, max_length=100, description="分类名称")
    categoryCode: str = Field(..., min_length=1, max_length=50, description="分类编码")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")
    parentUuid: Optional[UUID] = Field(None, description="父级分类UUID")
    sortOrder: int = Field(0, ge=0, description="排序顺序")


class ProductCategoryCreate(BaseModel):
    """产品分类创建模式"""
    categoryName: str
    categoryCode: str
    description: Optional[str] = None
    parentUuid: Optional[UUID] = None
    sortOrder: int = 0


class ProductCategoryUpdate(BaseModel):
    """产品分类更新模式"""
    categoryName: Optional[str] = None
    categoryCode: Optional[str] = None
    description: Optional[str] = None
    parentUuid: Optional[UUID] = None
    sortOrder: Optional[int] = None
    isActive: Optional[bool] = None


class ProductCategoryResponse(BaseModel):
    """产品分类响应模式"""
    uuid: UUID
    categoryName: str
    categoryCode: str
    description: Optional[str]
    parentUuid: Optional[UUID]
    sortOrder: int
    isActive: bool
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True


class ProductCategoryWithChildren(ProductCategoryResponse):
    """包含子分类的产品分类响应"""
    children: List['ProductCategoryResponse'] = Field(default_factory=list, description="子分类列表")


class ProductCategoryListResponse(BaseModel):
    """产品分类列表响应模式"""
    items: List[ProductCategoryResponse]
    total: int
    page: int
    size: int
    pages: int


class ProductCategoryTreeResponse(BaseModel):
    """产品分类树形结构响应模式"""
    items: List[ProductCategoryWithChildren]
    total: int