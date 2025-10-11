#!/usr/bin/env python3
"""
测试所有数据表的功能
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api/v1/coze"

async def test_table_fields(session: aiohttp.ClientSession, table_name: str) -> Dict[str, Any]:
    """测试单个表的字段获取功能"""
    url = f"{BASE_URL}/tables/{table_name}/fields"
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "table_name": table_name,
                    "fields_test": "PASS",
                    "field_count": len(data),
                    "fields": data
                }
            else:
                return {
                    "table_name": table_name,
                    "fields_test": "FAIL",
                    "error": f"HTTP {response.status}: {await response.text()}"
                }
    except Exception as e:
        return {
            "table_name": table_name,
            "fields_test": "FAIL",
            "error": str(e)
        }

async def test_table_sample_data(session: aiohttp.ClientSession, table_name: str) -> Dict[str, Any]:
    """测试单个表的样本数据获取功能"""
    url = f"{BASE_URL}/tables/{table_name}/sample?sample_size=2"
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "table_name": table_name,
                    "sample_test": "PASS",
                    "sample_count": len(data),
                    "sample_data": data
                }
            else:
                return {
                    "table_name": table_name,
                    "sample_test": "FAIL",
                    "error": f"HTTP {response.status}: {await response.text()}"
                }
    except Exception as e:
        return {
            "table_name": table_name,
            "sample_test": "FAIL",
            "error": str(e)
        }

async def test_all_tables():
    """测试所有数据表"""
    
    # 首先获取所有表列表
    async with aiohttp.ClientSession() as session:
        # 获取表列表
        async with session.get(f"{BASE_URL}/tables") as response:
            if response.status != 200:
                print(f"获取表列表失败: HTTP {response.status}")
                return
            
            tables_data = await response.json()
            table_names = [table["tableName"] for table in tables_data]
            
            print(f"发现 {len(table_names)} 个数据表:")
            for table in tables_data:
                print(f"  - {table['tableName']} ({table['displayName']}): {table['recordCount']} 条记录")
            
            print("\n开始测试字段获取功能...")
            
            # 测试所有表的字段获取
            fields_tasks = [test_table_fields(session, table_name) for table_name in table_names]
            fields_results = await asyncio.gather(*fields_tasks)
            
            print("\n字段获取测试结果:")
            for result in fields_results:
                status = "✅ PASS" if result["fields_test"] == "PASS" else "❌ FAIL"
                print(f"  - {result['table_name']}: {status}")
                if result["fields_test"] == "PASS":
                    print(f"    字段数量: {result['field_count']}")
                else:
                    print(f"    错误: {result['error']}")
            
            print("\n开始测试样本数据获取功能...")
            
            # 测试所有表的样本数据获取
            sample_tasks = [test_table_sample_data(session, table_name) for table_name in table_names]
            sample_results = await asyncio.gather(*sample_tasks)
            
            print("\n样本数据测试结果:")
            for result in sample_results:
                status = "✅ PASS" if result["sample_test"] == "PASS" else "❌ FAIL"
                print(f"  - {result['table_name']}: {status}")
                if result["sample_test"] == "PASS":
                    print(f"    样本数量: {result['sample_count']}")
                else:
                    print(f"    错误: {result['error']}")
            
            # 汇总结果
            print("\n" + "="*50)
            print("测试汇总:")
            print("="*50)
            
            fields_pass = sum(1 for r in fields_results if r["fields_test"] == "PASS")
            sample_pass = sum(1 for r in sample_results if r["sample_test"] == "PASS")
            
            print(f"字段获取: {fields_pass}/{len(table_names)} 个表通过")
            print(f"样本数据: {sample_pass}/{len(table_names)} 个表通过")
            
            # 显示有问题的表
            problematic_tables = []
            for i, table_name in enumerate(table_names):
                if fields_results[i]["fields_test"] == "FAIL" or sample_results[i]["sample_test"] == "FAIL":
                    problematic_tables.append({
                        "table_name": table_name,
                        "fields_error": fields_results[i].get("error") if fields_results[i]["fields_test"] == "FAIL" else None,
                        "sample_error": sample_results[i].get("error") if sample_results[i]["sample_test"] == "FAIL" else None
                    })
            
            if problematic_tables:
                print("\n有问题的表:")
                for table in problematic_tables:
                    print(f"\n  - {table['table_name']}:")
                    if table["fields_error"]:
                        print(f"    字段获取错误: {table['fields_error']}")
                    if table["sample_error"]:
                        print(f"    样本数据错误: {table['sample_error']}")
            else:
                print("\n🎉 所有表功能正常！")

if __name__ == "__main__":
    asyncio.run(test_all_tables())