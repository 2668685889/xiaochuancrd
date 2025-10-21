"""
调试数据库连接和事务问题
"""

import asyncio
import aiohttp
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from sqlalchemy.pool import NullPool

# 数据库配置
DATABASE_URL = "mysql+aiomysql://root:Xiaochuan123!@localhost:3306/xiaochuanERP"

async def debug_database_connection():
    """调试数据库连接"""
    print("=== 调试数据库连接 ===")
    
    # 创建引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        poolclass=NullPool,
        pool_pre_ping=True
    )
    
    async with engine.connect() as conn:
        # 检查数据库连接
        result = await conn.execute(text("SELECT DATABASE()"))
        db_name = result.scalar_one()
        print(f"当前连接的数据库: {db_name}")
        
        # 检查数据源表是否存在
        result = await conn.execute(text("SHOW TABLES LIKE 'sys_data_source'"))
        table_exists = result.scalar_one_or_none()
        print(f"sys_data_source表存在: {table_exists is not None}")
        
        if table_exists:
            # 查询数据源记录
            result = await conn.execute(text("SELECT id, name, connection_config FROM sys_data_source"))
            records = result.fetchall()
            print(f"数据源记录数量: {len(records)}")
            
            for record in records:
                print(f"ID: {record[0]}, 名称: {record[1]}")
                print(f"连接配置: {record[2]}")
                
                # 解析JSON配置
                import json
                try:
                    config = json.loads(record[2]) if record[2] else {}
                    print(f"密码字段: {config.get('password', '未找到')}")
                except:
                    print("配置解析失败")

async def test_transaction_isolation():
    """测试事务隔离级别"""
    print("\n=== 测试事务隔离级别 ===")
    
    # 创建引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        poolclass=NullPool,
        pool_pre_ping=True
    )
    
    # 创建会话工厂
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=True,
    )
    
    async with AsyncSessionLocal() as session1:
        # 导入模型
        from app.models.smart_assistant import DataSourceModel
        
        # 查询当前数据
        result = await session1.execute(select(DataSourceModel))
        data_source = result.scalar_one_or_none()
        
        if data_source:
            print(f"会话1 - 当前密码: {data_source.connection_config.get('password')}")
            
            # 更新密码但不提交
            new_password = "TransactionTest123!"
            data_source.connection_config["password"] = new_password
            print(f"会话1 - 设置新密码: {new_password}")
            
            # 在同一个会话中查询
            result2 = await session1.execute(select(DataSourceModel))
            data_source2 = result2.scalar_one_or_none()
            print(f"会话1 - 查询密码: {data_source2.connection_config.get('password')}")
            
            # 使用新会话查询（应该看不到未提交的更改）
            async with AsyncSessionLocal() as session2:
                result3 = await session2.execute(select(DataSourceModel))
                data_source3 = result3.scalar_one_or_none()
                print(f"会话2 - 查询密码: {data_source3.connection_config.get('password')}")
            
            # 现在提交事务
            await session1.commit()
            print("会话1 - 事务已提交")
            
            # 再次使用新会话查询
            async with AsyncSessionLocal() as session3:
                result4 = await session3.execute(select(DataSourceModel))
                data_source4 = result4.scalar_one_or_none()
                print(f"会话3 - 查询密码: {data_source4.connection_config.get('password')}")
                
                if data_source4.connection_config.get('password') == new_password:
                    print("✅ 事务隔离测试通过！")
                    return True
                else:
                    print("❌ 事务隔离测试失败！")
                    return False
        else:
            print("❌ 未找到数据源记录")
            return False

async def test_direct_sql_update():
    """使用原始SQL直接更新"""
    print("\n=== 使用原始SQL直接更新 ===")
    
    # 创建引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        poolclass=NullPool,
        pool_pre_ping=True
    )
    
    async with engine.connect() as conn:
        # 查询当前配置
        result = await conn.execute(text("SELECT id, connection_config FROM sys_data_source"))
        record = result.fetchone()
        
        if record:
            import json
            config = json.loads(record[1]) if record[1] else {}
            print(f"当前密码: {config.get('password')}")
            
            # 更新密码
            new_password = "DirectSQLUpdate123!"
            config["password"] = new_password
            
            # 执行更新
            await conn.execute(
                text("UPDATE sys_data_source SET connection_config = :config WHERE id = :id"),
                {"config": json.dumps(config), "id": record[0]}
            )
            
            # 提交事务
            await conn.commit()
            print("SQL更新已提交")
            
            # 验证更新
            result2 = await conn.execute(text("SELECT connection_config FROM sys_data_source WHERE id = :id"), {"id": record[0]})
            config2 = json.loads(result2.scalar_one())
            print(f"更新后密码: {config2.get('password')}")
            
            if config2.get('password') == new_password:
                print("✅ SQL更新成功！")
                return True
            else:
                print("❌ SQL更新失败！")
                return False
        else:
            print("❌ 未找到数据源记录")
            return False

async def main():
    """主调试函数"""
    print("开始调试数据库连接和事务问题...")
    
    # 调试数据库连接
    await debug_database_connection()
    
    # 测试事务隔离级别
    isolation_result = await test_transaction_isolation()
    
    # 测试直接SQL更新
    sql_result = await test_direct_sql_update()
    
    print("\n=== 调试结果汇总 ===")
    print(f"事务隔离测试: {'✅ 通过' if isolation_result else '❌ 失败'}")
    print(f"SQL直接更新: {'✅ 通过' if sql_result else '❌ 失败'}")

if __name__ == "__main__":
    # 添加项目路径到Python路径
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    
    asyncio.run(main())