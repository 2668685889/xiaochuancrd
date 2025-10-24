#!/usr/bin/env python3
"""
测试查询语句生成准确性
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_async_db
from app.services.mcp_mysql_service import MCPMySQLService

async def test_query_accuracy():
    """测试查询语句生成准确性"""
    print("=== 测试查询语句生成准确性 ===")
    
    # 定义测试用例
    test_cases = [
        {
            "query": "查询所有商品信息",
            "expected_fields": ["uuid", "product_name", "product_code", "current_quantity", "unit_price"],
            "description": "基本商品查询"
        },
        {
            "query": "查询库存不足的商品",
            "expected_conditions": ["current_quantity <= min_quantity", "is_active = TRUE"],
            "description": "库存不足查询"
        },
        {
            "query": "查询价格大于100元的商品",
            "expected_conditions": ["unit_price > 100", "is_active = TRUE"],
            "description": "价格过滤查询"
        },
        {
            "query": "查询最近创建的商品",
            "expected_order": "created_at DESC",
            "description": "时间排序查询"
        },
        {
            "query": "查询用户列表",
            "expected_table": "users",
            "expected_fields": ["uuid", "username", "email", "full_name"],
            "description": "用户表查询"
        }
    ]
    
    try:
        # 获取数据库会话
        async for db in get_async_db():
            mcp_service = MCPMySQLService(db)
            
            total_tests = len(test_cases)
            passed_tests = 0
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n--- 测试 {i}/{total_tests}: {test_case['description']} ---")
                print(f"查询: {test_case['query']}")
                
                try:
                    # 生成SQL查询
                    result = await mcp_service._generate_sql_with_deepseek(test_case['query'])
                    
                    if result["success"] and result.get("sql"):
                        sql = result["sql"]
                        print(f"✅ SQL生成成功")
                        print(f"生成的SQL: {sql}")
                        
                        # 验证准确性
                        is_valid = True
                        
                        # 检查预期字段
                        if "expected_fields" in test_case:
                            for field in test_case["expected_fields"]:
                                if field not in sql:
                                    print(f"⚠️ 缺少预期字段: {field}")
                                    is_valid = False
                        
                        # 检查预期条件
                        if "expected_conditions" in test_case:
                            for condition in test_case["expected_conditions"]:
                                if condition not in sql:
                                    print(f"⚠️ 缺少预期条件: {condition}")
                                    is_valid = False
                        
                        # 检查预期排序
                        if "expected_order" in test_case:
                            if test_case["expected_order"] not in sql:
                                print(f"⚠️ 缺少预期排序: {test_case['expected_order']}")
                                is_valid = False
                        
                        # 检查预期表
                        if "expected_table" in test_case:
                            if test_case["expected_table"] not in sql:
                                print(f"⚠️ 使用了错误的表，预期: {test_case['expected_table']}")
                                is_valid = False
                        
                        if is_valid:
                            print("✅ 查询准确性验证通过")
                            passed_tests += 1
                        else:
                            print("❌ 查询准确性验证失败")
                        
                        if result.get('explanation'):
                            print(f"解释: {result['explanation']}")
                    else:
                        print(f"❌ SQL生成失败: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    print(f"❌ 测试过程中出现错误: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 输出测试总结
            print(f"\n=== 测试总结 ===")
            print(f"总测试数: {total_tests}")
            print(f"通过数: {passed_tests}")
            print(f"通过率: {passed_tests/total_tests*100:.1f}%")
            
            if passed_tests == total_tests:
                print("🎉 所有测试用例均通过！")
            else:
                print("⚠️ 部分测试用例未通过，需要进一步优化")
            
            break  # 只处理第一个会话
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_query_accuracy())