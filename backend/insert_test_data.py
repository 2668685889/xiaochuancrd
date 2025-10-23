#!/usr/bin/env python3
"""
为进销存系统插入测试数据
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta
from app.core.database import engine
from app.core.database import get_db
from sqlalchemy import text


async def insert_test_data():
    """插入测试数据"""
    async with engine.begin() as conn:
        # 检查用户数据
        result = await conn.execute(text('SELECT COUNT(*) FROM users;'))
        user_count = result.scalar()
        
        # 定义users_data变量，确保在后续代码中可访问
        users_data = []
        
        if user_count > 0:
            print(f"数据库中已有 {user_count} 条用户数据，跳过插入用户数据")
            # 如果用户表已有数据，需要获取一个用户UUID用于created_by字段
            result = await conn.execute(text('SELECT uuid FROM users LIMIT 1;'))
            user_row = result.fetchone()
            if user_row:
                users_data.append({'uuid': user_row[0]})
        else:
            print("开始插入测试数据...")
            
            # 1. 插入用户数据
            print("插入用户数据...")
            users_data = [
                {
                    'uuid': str(uuid.uuid4()),
                    'username': 'admin',
                    'email': 'admin@xiaochuan.com',
                    'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # admin123
                    'full_name': '系统管理员',
                    'role': 'admin',
                    'is_superuser': 1,
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'username': 'manager1',
                    'email': 'manager1@xiaochuan.com',
                    'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # admin123
                    'full_name': '销售经理张三',
                    'role': 'manager',
                    'is_superuser': 0,
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'username': 'user1',
                    'email': 'user1@xiaochuan.com',
                    'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # admin123
                    'full_name': '普通用户李四',
                    'role': 'user',
                    'is_superuser': 0,
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'username': 'user2',
                    'email': 'user2@xiaochuan.com',
                    'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # admin123
                    'full_name': '普通用户王五',
                    'role': 'user',
                    'is_superuser': 0,
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'username': 'user3',
                    'email': 'user3@xiaochuan.com',
                    'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # admin123
                    'full_name': '普通用户赵六',
                    'role': 'user',
                    'is_superuser': 0,
                    'is_active': 1
                }
            ]
            
            for user in users_data:
                await conn.execute(text("""
                    INSERT INTO users (uuid, username, email, password_hash, full_name, role, is_superuser, is_active, created_at, updated_at)
                    VALUES (:uuid, :username, :email, :password_hash, :full_name, :role, :is_superuser, :is_active, NOW(), NOW())
                """), user)

        
        # 2. 检查供应商数据
        print("检查供应商数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM suppliers;'))
        supplier_count = result.scalar()
        
        if supplier_count > 0:
            print(f"供应商表中已有 {supplier_count} 条数据，跳过插入")
        else:
            print("插入供应商数据...")
            suppliers_data = [
            {
                'uuid': str(uuid.uuid4()),
                'supplier_name': '联想集团',
                'supplier_code': 'LX001',
                'contact_person': '张经理',
                'phone': '13800138001',
                'email': 'lx@lenovo.com',
                'address': '北京市海淀区上地信息产业基地',
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'supplier_name': '华为技术有限公司',
                'supplier_code': 'HW002',
                'contact_person': '李总监',
                'phone': '13800138002',
                'email': 'hw@huawei.com',
                'address': '深圳市龙岗区坂田华为基地',
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'supplier_name': '小米科技',
                'supplier_code': 'XM003',
                'contact_person': '王经理',
                'phone': '13800138003',
                'email': 'xm@xiaomi.com',
                'address': '北京市海淀区清河中街68号',
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'supplier_name': '戴尔电脑',
                'supplier_code': 'DE004',
                'contact_person': '陈主管',
                'phone': '13800138004',
                'email': 'de@dell.com',
                'address': '上海市浦东新区张江高科技园区',
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'supplier_name': '苹果公司',
                'supplier_code': 'PG005',
                'contact_person': '刘专员',
                'phone': '13800138005',
                'email': 'pg@apple.com',
                'address': '上海市浦东新区陆家嘴金融贸易区',
                'is_active': 1
            }
            ]
            
            for supplier in suppliers_data:
                await conn.execute(text("""
                    INSERT INTO suppliers (uuid, supplier_name, supplier_code, contact_person, phone, email, address, is_active, created_at, updated_at)
                    VALUES (:uuid, :supplier_name, :supplier_code, :contact_person, :phone, :email, :address, :is_active, NOW(), NOW())
                """), supplier)
        
        # 3. 检查客户数据
        print("检查客户数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM customers;'))
        customer_count = result.scalar()
        
        customers_data = []
        
        if customer_count > 0:
            print(f"客户表中已有 {customer_count} 条数据，跳过插入")
            # 从数据库查询客户数据用于后续关联
            result = await conn.execute(text('SELECT uuid, customer_name, phone, address FROM customers LIMIT 5;'))
            customers = result.fetchall()
            for customer in customers:
                customers_data.append({
                    'uuid': customer[0],
                    'customer_name': customer[1],
                    'phone': customer[2],
                    'address': customer[3]
                })
            
            # 如果数据库中的客户数据少于5条，补充默认数据
            while len(customers_data) < 5:
                customers_data.append({
                    'uuid': str(uuid.uuid4()),
                    'customer_name': f'默认客户{len(customers_data) + 1}',
                    'phone': '13800000000',
                    'address': '默认地址'
                })
        else:
            print("插入客户数据...")
            customers_data = [
                {
                    'uuid': str(uuid.uuid4()),
                    'customer_name': '北京科技有限公司',
                    'customer_code': 'BJ001',
                    'contact_person': '张总',
                    'phone': '13800138101',
                    'email': 'bj@tech.com',
                    'address': '北京市朝阳区建国门外大街',
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'customer_name': '上海贸易有限公司',
                    'customer_code': 'SH002',
                    'contact_person': '李经理',
                    'phone': '13800138102',
                    'email': 'sh@trade.com',
                    'address': '上海市黄浦区南京东路',
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'customer_name': '广州电子有限公司',
                    'customer_code': 'GZ003',
                    'contact_person': '王总监',
                    'phone': '13800138103',
                    'email': 'gz@elec.com',
                    'address': '广州市天河区珠江新城',
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'customer_name': '深圳创新科技有限公司',
                    'customer_code': 'SZ004',
                    'contact_person': '陈主管',
                    'phone': '13800138104',
                    'email': 'sz@innovate.com',
                    'address': '深圳市南山区科技园',
                    'is_active': 1
                },
                {
                    'uuid': str(uuid.uuid4()),
                    'customer_name': '杭州互联网有限公司',
                    'customer_code': 'HZ005',
                    'contact_person': '赵专员',
                    'phone': '13800138105',
                    'email': 'hz@internet.com',
                    'address': '杭州市西湖区文三路',
                    'is_active': 1
                }
            ]
            
            for customer in customers_data:
                await conn.execute(text("""
                    INSERT INTO customers (uuid, customer_name, customer_code, contact_person, phone, email, address, is_active, created_at, updated_at)
                    VALUES (:uuid, :customer_name, :customer_code, :contact_person, :phone, :email, :address, :is_active, NOW(), NOW())
                """), customer)
        
        # 4. 检查产品数据
        print("检查产品数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM products;'))
        product_count = result.scalar()
        
        if product_count > 0:
            print(f"产品表中已有 {product_count} 条数据，跳过插入")
        else:
            print("插入产品数据...")
            products_data = [
            {
                'uuid': str(uuid.uuid4()),
                'product_name': '联想ThinkPad X1 Carbon',
                'product_code': 'NB001',
                'description': '14英寸轻薄商务笔记本电脑',
                'unit_price': 8999.00,
                'current_quantity': 50,
                'min_quantity': 5,
                'max_quantity': 200,
                'supplier_uuid': suppliers_data[0]['uuid'],
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'product_name': '华为MateBook 14',
                'product_code': 'NB002',
                'description': '14英寸全面屏轻薄本',
                'unit_price': 5999.00,
                'current_quantity': 80,
                'min_quantity': 10,
                'max_quantity': 300,
                'supplier_uuid': suppliers_data[1]['uuid'],
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'product_name': '小米RedmiBook Pro 15',
                'product_code': 'NB003',
                'description': '15.6英寸高性能轻薄本',
                'unit_price': 4999.00,
                'current_quantity': 100,
                'min_quantity': 15,
                'max_quantity': 400,
                'supplier_uuid': suppliers_data[2]['uuid'],
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'product_name': '戴尔XPS 13',
                'product_code': 'NB004',
                'description': '13.4英寸超极本',
                'unit_price': 7999.00,
                'current_quantity': 30,
                'min_quantity': 3,
                'max_quantity': 150,
                'supplier_uuid': suppliers_data[3]['uuid'],
                'is_active': 1
            },
            {
                'uuid': str(uuid.uuid4()),
                'product_name': 'MacBook Air M2',
                'product_code': 'NB005',
                'description': '13.6英寸苹果笔记本电脑',
                'unit_price': 9999.00,
                'current_quantity': 20,
                'min_quantity': 2,
                'max_quantity': 100,
                'supplier_uuid': suppliers_data[4]['uuid'],
                'is_active': 1
            }
            ]
            
            for product in products_data:
                await conn.execute(text("""
                    INSERT INTO products (uuid, product_name, product_code, description, unit_price, current_quantity, min_quantity, max_quantity, supplier_uuid, is_active, created_at, updated_at)
                    VALUES (:uuid, :product_name, :product_code, :description, :unit_price, :current_quantity, :min_quantity, :max_quantity, :supplier_uuid, :is_active, NOW(), NOW())
                """), product)
        
        # 5. 检查库存记录数据
        print("检查库存记录数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM inventory_records;'))
        inventory_count = result.scalar()
        
        if inventory_count > 0:
            print(f"库存记录表中已有 {inventory_count} 条数据，跳过插入")
        else:
            print("插入库存记录数据...")
            inventory_records_data = []
            for i, product in enumerate(products_data):
                for j in range(5):
                    record_date = date.today() - timedelta(days=j*10)
                    quantity_change = 10 + j * 5
                    current_quantity = product['current_quantity'] + (quantity_change if j % 2 == 0 else -quantity_change)
                    
                    inventory_records_data.append({
                        'uuid': str(uuid.uuid4()),
                        'product_uuid': product['uuid'],
                        'change_type': 'IN' if j % 2 == 0 else 'OUT',
                        'quantity_change': quantity_change,
                        'current_quantity': current_quantity,
                        'remark': f'第{j+1}次库存{"入库" if j % 2 == 0 else "出库"}记录',
                        'record_date': record_date,
                        'created_by': users_data[0]['uuid']
                    })
            
            for record in inventory_records_data:
                await conn.execute(text("""
                    INSERT INTO inventory_records (uuid, product_uuid, change_type, quantity_change, current_quantity, remark, record_date, created_by, created_at)
                    VALUES (:uuid, :product_uuid, :change_type, :quantity_change, :current_quantity, :remark, :record_date, :created_by, NOW())
                """), record)
        
        # 6. 检查采购订单数据
        print("检查采购订单数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM purchase_orders;'))
        purchase_order_count = result.scalar()
        
        if purchase_order_count > 0:
            print(f"采购订单表中已有 {purchase_order_count} 条数据，跳过插入")
        else:
            print("插入采购订单数据...")
            purchase_orders_data = []
            for i in range(5):
                order_date = date.today() - timedelta(days=(4-i)*30)
                expected_delivery_date = order_date + timedelta(days=7)
                purchase_orders_data.append({
                    'uuid': str(uuid.uuid4()),
                    'order_number': f'PO202400{i+1}',
                    'supplier_uuid': suppliers_data[i]['uuid'],
                    'total_amount': (i+1) * 50000.00,
                    'status': 'RECEIVED' if i < 3 else 'CONFIRMED',
                    'order_date': order_date,
                    'expected_delivery_date': expected_delivery_date,
                    'actual_delivery_date': expected_delivery_date if i < 3 else None,
                    'remark': f'第{i+1}批采购订单',
                    'created_by': users_data[0]['uuid']
                })
            
            for order in purchase_orders_data:
                await conn.execute(text("""
                    INSERT INTO purchase_orders (uuid, order_number, supplier_uuid, total_amount, status, order_date, expected_delivery_date, actual_delivery_date, remark, created_by, created_at, updated_at)
                    VALUES (:uuid, :order_number, :supplier_uuid, :total_amount, :status, :order_date, :expected_delivery_date, :actual_delivery_date, :remark, :created_by, NOW(), NOW())
                """), order)
        
        # 7. 检查销售订单数据
        print("检查销售订单数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM sales_orders;'))
        sales_order_count = result.scalar()
        
        if sales_order_count > 0:
            print(f"销售订单表中已有 {sales_order_count} 条数据，跳过插入")
        else:
            print("插入销售订单数据...")
            sales_orders_data = []
            for i in range(5):
                order_date = date.today() - timedelta(days=(4-i)*15)
                expected_delivery_date = order_date + timedelta(days=5)
                sales_orders_data.append({
                    'uuid': str(uuid.uuid4()),
                    'order_number': f'SO202400{i+1}',
                    'customer_uuid': customers_data[i]['uuid'],
                    'total_amount': (i+1) * 30000.00,
                    'status': 'DELIVERED' if i < 3 else 'CONFIRMED',
                    'order_date': order_date,
                    'expected_delivery_date': expected_delivery_date,
                    'actual_delivery_date': expected_delivery_date if i < 3 else None,
                    'remark': f'第{i+1}批销售订单',
                    'created_by': users_data[0]['uuid']
                })
            
            for order in sales_orders_data:
                # 获取对应的客户信息
                customer = customers_data[sales_orders_data.index(order)]
                order_data = order.copy()
                order_data['customer_name'] = customer['customer_name']
                order_data['customer_phone'] = customer.get('phone', '13800000000')
                order_data['customer_address'] = customer.get('address', '默认地址')
                
                await conn.execute(text("""
                    INSERT INTO sales_orders (uuid, order_number, customer_uuid, customer_name, customer_phone, customer_address, total_amount, status, order_date, expected_delivery_date, actual_delivery_date, remark, created_by, created_at, updated_at)
                    VALUES (:uuid, :order_number, :customer_uuid, :customer_name, :customer_phone, :customer_address, :total_amount, :status, :order_date, :expected_delivery_date, :actual_delivery_date, :remark, :created_by, NOW(), NOW())
                """), order_data)
        
        # 8. 检查采购订单项数据
        print("检查采购订单项数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM purchase_order_items;'))
        purchase_order_item_count = result.scalar()
        
        if purchase_order_item_count > 0:
            print(f"采购订单项表中已有 {purchase_order_item_count} 条数据，跳过插入")
        else:
            print("插入采购订单项数据...")
            purchase_order_items_data = []
            for i, order in enumerate(purchase_orders_data):
                for j in range(min(3, len(products_data))):
                    product = products_data[j]
                    purchase_order_items_data.append({
                        'uuid': str(uuid.uuid4()),
                        'purchase_order_uuid': order['uuid'],
                        'product_uuid': product['uuid'],
                        'product_name': product['product_name'],
                        'product_code': product['product_code'],
                        'quantity': (i+1) * 10,
                        'unit_price': product['unit_price'] * 0.9,
                        'total_price': (i+1) * 10 * product['unit_price'] * 0.9,
                        'shipped_quantity': (i+1) * 10 if i < 3 else 0,
                        'remark': f'采购订单项{i+1}-{j+1}'
                    })
            
            for item in purchase_order_items_data:
                await conn.execute(text("""
                    INSERT INTO purchase_order_items (uuid, purchase_order_uuid, product_uuid, quantity, unit_price, total_price, received_quantity, remark, created_at)
                    VALUES (:uuid, :purchase_order_uuid, :product_uuid, :quantity, :unit_price, :total_price, :shipped_quantity, :remark, NOW())
                """), item)
        
        # 9. 检查销售订单项数据
        print("检查销售订单项数据...")
        result = await conn.execute(text('SELECT COUNT(*) FROM sales_order_items;'))
        sales_order_item_count = result.scalar()
        
        if sales_order_item_count > 0:
            print(f"销售订单项表中已有 {sales_order_item_count} 条数据，跳过插入")
        else:
            print("插入销售订单项数据...")
            sales_order_items_data = []
            for i, order in enumerate(sales_orders_data):
                for j in range(min(3, len(products_data))):
                    product = products_data[j]
                    sales_order_items_data.append({
                        'uuid': str(uuid.uuid4()),
                        'sales_order_uuid': order['uuid'],
                        'product_uuid': product['uuid'],
                        'product_name': product['product_name'],
                        'product_code': product['product_code'],
                        'quantity': (i+1) * 5,
                        'unit_price': product['unit_price'] * 1.1,
                        'total_price': (i+1) * 5 * product['unit_price'] * 1.1,
                        'shipped_quantity': (i+1) * 5 if i < 3 else 0,
                        'remark': f'销售订单项{i+1}-{j+1}'
                    })
            
            for item in sales_order_items_data:
                await conn.execute(text("""
                    INSERT INTO sales_order_items (uuid, sales_order_uuid, product_uuid, quantity, unit_price, total_price, shipped_quantity, remark, created_at)
                    VALUES (:uuid, :sales_order_uuid, :product_uuid, :quantity, :unit_price, :total_price, :shipped_quantity, :remark, NOW())
                """), item)
        
        print("测试数据插入完成！")
        
        # 显示插入的数据统计
        tables_to_check = ['users', 'suppliers', 'customers', 'products', 'inventory_records', 'purchase_orders', 'sales_orders', 'purchase_order_items', 'sales_order_items']
        
        print("\n数据统计:")
        for table in tables_to_check:
            result = await conn.execute(text(f'SELECT COUNT(*) FROM {table};'))
            count = result.scalar()
            print(f"{table}: {count} 条记录")


if __name__ == "__main__":
    asyncio.run(insert_test_data())