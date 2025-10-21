import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.product import Product
from sqlalchemy import select

async def check_products():
    # 使用异步数据库连接
    DATABASE_URL = 'mysql+aiomysql://root:Xiaochuan123!@localhost/xiaochuanERP'
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 查询所有产品
        stmt = select(Product)
        result = await session.execute(stmt)
        products = result.all()
        
        print(f'数据库中共有 {len(products)} 个产品:')
        for product in products:
            product_obj = product[0]  # 获取Product对象
            print(f'- UUID: {product_obj.uuid}, 名称: {product_obj.product_name}, 代码: {product_obj.product_code}, 数量: {product_obj.current_quantity}, 价格: {product_obj.unit_price}')

if __name__ == "__main__":
    asyncio.run(check_products())