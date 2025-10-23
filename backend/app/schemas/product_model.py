"""
产品型号相关的Pydantic模式
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class ProductSpecification(BaseModel):
    """规格参数项"""
    key: str = Field(..., description="参数名称")
    value: str = Field(..., description="参数值")
    unit: Optional[str] = Field(None, description="参数单位")


class ProductModelBase(BaseModel):
    """产品型号基础模式"""
    modelName: str = Field(..., min_length=1, max_length=100, description="型号名称")
    modelCode: str = Field(..., min_length=1, max_length=50, description="型号编码")
    description: Optional[str] = Field(None, max_length=500, description="型号描述")
    categoryUuid: Optional[str] = Field(None, description="产品分类UUID")
    specifications: List[ProductSpecification] = Field(default_factory=list, description="规格参数数组")


class ProductModelCreate(BaseModel):
    """产品型号创建模式"""
    modelName: str
    modelCode: str
    description: Optional[str] = None
    categoryUuid: Optional[str] = None
    specifications: List[ProductSpecification] = []


class ProductModelUpdate(BaseModel):
    """产品型号更新模式"""
    modelName: Optional[str] = None
    modelCode: Optional[str] = None
    description: Optional[str] = None
    categoryUuid: Optional[str] = None
    specifications: Optional[List[ProductSpecification]] = None
    isActive: Optional[bool] = None


class ProductModelResponse(BaseModel):
    """产品型号响应模式"""
    uuid: UUID
    modelName: str
    modelCode: str
    description: Optional[str]
    categoryUuid: Optional[str]
    categoryName: Optional[str] = None
    specifications: List[ProductSpecification]
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ProductModelListResponse(BaseModel):
    """产品型号列表响应模式"""
    items: List[ProductModelResponse]
    total: int
    page: int
    size: int
    pages: int


class SpecificationTemplate(BaseModel):
    """规格参数模板"""
    name: str = Field(..., description="规格名称")
    type: str = Field(..., description="规格类型（text, number, select, boolean）")
    required: bool = Field(False, description="是否必填")
    options: Optional[List[str]] = Field(None, description="选项列表（仅适用于select类型）")
    defaultValue: Optional[Any] = Field(None, description="默认值")
    unit: Optional[str] = Field(None, description="单位")


class ProductModelWithSpecs(ProductModelResponse):
    """包含规格模板的产品型号响应"""
    specTemplates: List[SpecificationTemplate] = Field(default_factory=list, description="规格模板")