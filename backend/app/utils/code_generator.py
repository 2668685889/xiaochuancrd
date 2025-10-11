"""
编码生成工具
用于生成各种业务编码，如供应商编码、产品编码等
"""

import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional


def generate_supplier_code(length: int = 8) -> str:
    """
    生成供应商编码
    格式：S + 7位大写英文加数字的组合
    
    Args:
        length: 编码长度，默认为8位
        
    Returns:
        str: 生成的供应商编码
    """
    # 供应商编码前缀
    prefix = "S"
    
    # 剩余长度用于随机字符
    remaining_length = length - len(prefix)
    
    if remaining_length <= 0:
        raise ValueError("编码长度必须大于前缀长度")
    
    # 生成字符池：大写字母 + 数字
    characters = string.ascii_uppercase + string.digits
    
    # 生成随机部分
    random_part = ''.join(random.choices(characters, k=remaining_length))
    
    return prefix + random_part


async def generate_unique_supplier_code(db: AsyncSession, length: int = 8, max_attempts: int = 10) -> str:
    """
    生成唯一的供应商编码
    
    Args:
        db: 数据库会话
        length: 编码长度，默认为8位
        max_attempts: 最大尝试次数
        
    Returns:
        str: 唯一的供应商编码
        
    Raises:
        RuntimeError: 无法生成唯一编码时抛出异常
    """
    from app.models.supplier import Supplier
    
    for attempt in range(max_attempts):
        code = generate_supplier_code(length)
        
        # 检查编码是否已存在
        result = await db.execute(select(Supplier).where(Supplier.supplier_code == code))
        existing_supplier = result.scalar_one_or_none()
        
        if not existing_supplier:
            return code
    
    raise RuntimeError(f"无法生成唯一的供应商编码，已尝试 {max_attempts} 次")


def generate_product_code(length: int = 10) -> str:
    """
    生成产品编码
    格式：P + 9位大写英文加数字的组合
    
    Args:
        length: 编码总长度，默认为10位
        
    Returns:
        str: 生成的产品编码
    """
    # 产品编码前缀
    prefix = "P"
    
    # 剩余长度用于随机字符
    remaining_length = length - len(prefix)
    
    if remaining_length <= 0:
        raise ValueError("编码长度必须大于前缀长度")
    
    # 生成随机字符：大写字母 + 数字
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(characters, k=remaining_length))
    
    return prefix + random_part


async def generate_unique_product_code(db: AsyncSession, length: int = 10, max_attempts: int = 10) -> str:
    """
    生成唯一的产品编码
    
    Args:
        db: 数据库会话
        length: 编码长度，默认为10位
        max_attempts: 最大尝试次数
        
    Returns:
        str: 唯一的产品编码
        
    Raises:
        RuntimeError: 无法生成唯一编码时抛出异常
    """
    from app.models.product import Product
    
    for attempt in range(max_attempts):
        code = generate_product_code(length)
        
        # 检查编码是否已存在
        result = await db.execute(select(Product).where(Product.product_code == code))
        existing_product = result.scalar_one_or_none()
        
        if not existing_product:
            return code
    
    raise RuntimeError(f"无法生成唯一的产品编码，已尝试 {max_attempts} 次")


def generate_product_category_code(length: int = 8) -> str:
    """
    生成产品分类编码
    格式：PC + 6位大写英文加数字的组合
    
    Args:
        length: 编码长度，默认为8位
        
    Returns:
        str: 生成的产品分类编码
    """
    # 产品分类编码前缀
    prefix = "PC"
    
    # 剩余长度用于随机字符
    remaining_length = length - len(prefix)
    
    if remaining_length <= 0:
        raise ValueError("编码长度必须大于前缀长度")
    
    # 生成字符池：大写字母 + 数字
    characters = string.ascii_uppercase + string.digits
    
    # 生成随机部分
    random_part = ''.join(random.choices(characters, k=remaining_length))
    
    return prefix + random_part


async def generate_unique_product_category_code(db: AsyncSession, length: int = 8, max_attempts: int = 10) -> str:
    """
    生成唯一的产品分类编码
    
    Args:
        db: 数据库会话
        length: 编码长度，默认为8位
        max_attempts: 最大尝试次数
        
    Returns:
        str: 唯一的产品分类编码
        
    Raises:
        RuntimeError: 无法生成唯一编码时抛出异常
    """
    from app.models.product_category import ProductCategory
    
    for attempt in range(max_attempts):
        code = generate_product_category_code(length)
        
        # 检查编码是否已存在
        result = await db.execute(select(ProductCategory).where(ProductCategory.category_code == code))
        existing_category = result.scalar_one_or_none()
        
        if not existing_category:
            return code
    
    raise RuntimeError(f"无法生成唯一的产品分类编码，已尝试 {max_attempts} 次")


def generate_product_model_code(length: int = 8) -> str:
    """
    生成产品型号编码
    格式：PM + 6位大写英文加数字的组合
    
    Args:
        length: 编码长度，默认为8位
        
    Returns:
        str: 生成的产品型号编码
    """
    # 产品型号编码前缀
    prefix = "PM"
    
    # 剩余长度用于随机字符
    remaining_length = length - len(prefix)
    
    if remaining_length <= 0:
        raise ValueError("编码长度必须大于前缀长度")
    
    # 生成字符池：大写字母 + 数字
    characters = string.ascii_uppercase + string.digits
    
    # 生成随机部分
    random_part = ''.join(random.choices(characters, k=remaining_length))
    
    return prefix + random_part


async def generate_unique_product_model_code(db: AsyncSession, length: int = 8, max_attempts: int = 10) -> str:
    """
    生成唯一的产品型号编码
    
    Args:
        db: 数据库会话
        length: 编码长度，默认为8位
        max_attempts: 最大尝试次数
        
    Returns:
        str: 唯一的产品型号编码
        
    Raises:
        RuntimeError: 无法生成唯一编码时抛出异常
    """
    from app.models.product_model import ProductModel
    
    for attempt in range(max_attempts):
        code = generate_product_model_code(length)
        
        # 检查编码是否已存在
        result = await db.execute(select(ProductModel).where(ProductModel.model_code == code))
        existing_model = result.scalar_one_or_none()
        
        if not existing_model:
            return code
    
    raise RuntimeError(f"无法生成唯一的产品型号编码，已尝试 {max_attempts} 次")


def generate_customer_code(length: int = 8) -> str:
    """
    生成客户编码
    格式：C + 7位大写英文加数字的组合
    
    Args:
        length: 编码长度，默认为8位
        
    Returns:
        str: 生成的客户编码
    """
    # 客户编码前缀
    prefix = "C"
    
    # 剩余长度用于随机字符
    remaining_length = length - len(prefix)
    
    if remaining_length <= 0:
        raise ValueError("编码长度必须大于前缀长度")
    
    # 生成字符池：大写字母 + 数字
    characters = string.ascii_uppercase + string.digits
    
    # 生成随机部分
    random_part = ''.join(random.choices(characters, k=remaining_length))
    
    return prefix + random_part


async def generate_unique_customer_code(db: AsyncSession, length: int = 8, max_attempts: int = 10) -> str:
    """
    生成唯一的客户编码
    
    Args:
        db: 数据库会话
        length: 编码长度，默认为8位
        max_attempts: 最大尝试次数
        
    Returns:
        str: 唯一的客户编码
        
    Raises:
        RuntimeError: 无法生成唯一编码时抛出异常
    """
    from app.models.customer import Customer
    
    for attempt in range(max_attempts):
        code = generate_customer_code(length)
        
        # 检查编码是否已存在
        result = await db.execute(select(Customer).where(Customer.customer_code == code))
        existing_customer = result.scalar_one_or_none()
        
        if not existing_customer:
            return code
    
    raise RuntimeError(f"无法生成唯一的客户编码，已尝试 {max_attempts} 次")