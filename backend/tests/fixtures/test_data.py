"""
测试数据夹具
"""

import uuid
from datetime import datetime, date


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_product_data(**kwargs):
        """创建产品测试数据"""
        default_data = {
            "productName": "测试产品",
            "productCode": "TEST001",
            "description": "这是一个测试产品",
            "category": "电子产品",
            "unitPrice": 99.99,
            "costPrice": 50.00,
            "stockQuantity": 100,
            "minStockLevel": 10,
            "maxStockLevel": 500,
            "unitOfMeasure": "个",
            "brand": "测试品牌",
            "model": "测试型号",
            "specifications": "测试规格",
            "weight": 1.5,
            "dimensions": "10x10x5cm",
            "isActive": True
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_customer_data(**kwargs):
        """创建客户测试数据"""
        default_data = {
            "customerName": "测试客户公司",
            "customerCode": "CUST001",
            "contactPerson": "张经理",
            "phone": "13800138000",
            "email": "test@example.com",
            "address": "测试地址",
            "city": "测试城市",
            "province": "测试省份",
            "postalCode": "100000",
            "customerType": "企业客户",
            "creditLimit": 10000.00,
            "paymentTerms": "30天",
            "taxId": "123456789012345",
            "notes": "测试备注",
            "isActive": True
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_supplier_data(**kwargs):
        """创建供应商测试数据"""
        default_data = {
            "supplierName": "测试供应商",
            "supplierCode": "SUP001",
            "contactPerson": "王经理",
            "phone": "13700137000",
            "email": "supplier@example.com",
            "address": "供应商地址",
            "city": "供应商城市",
            "province": "供应商省份",
            "postalCode": "200000",
            "supplierType": "生产商",
            "paymentTerms": "60天",
            "taxId": "987654321098765",
            "bankAccount": "12345678901234567890",
            "bankName": "测试银行",
            "notes": "供应商备注",
            "isActive": True
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_sales_order_data(customer_uuid=None, **kwargs):
        """创建销售订单测试数据"""
        default_data = {
            "orderNumber": "SO2024001",
            "customerUuid": customer_uuid or str(uuid.uuid4()),
            "orderDate": date.today().isoformat(),
            "expectedDeliveryDate": date.today().replace(day=date.today().day + 7).isoformat(),
            "orderStatus": "pending",
            "paymentStatus": "pending",
            "totalAmount": 2000.00,
            "taxAmount": 200.00,
            "discountAmount": 0.00,
            "shippingAddress": "测试配送地址",
            "billingAddress": "测试账单地址",
            "notes": "测试订单备注",
            "orderItems": [
                {
                    "productUuid": str(uuid.uuid4()),
                    "quantity": 10,
                    "unitPrice": 200.00,
                    "totalPrice": 2000.00
                }
            ]
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_purchase_order_data(supplier_uuid=None, **kwargs):
        """创建采购订单测试数据"""
        default_data = {
            "orderNumber": "PO2024001",
            "supplierUuid": supplier_uuid or str(uuid.uuid4()),
            "orderDate": date.today().isoformat(),
            "expectedDeliveryDate": date.today().replace(day=date.today().day + 15).isoformat(),
            "orderStatus": "pending",
            "paymentStatus": "pending",
            "totalAmount": 4000.00,
            "taxAmount": 400.00,
            "discountAmount": 0.00,
            "shippingAddress": "公司仓库",
            "billingAddress": "公司财务部",
            "notes": "采购订单备注",
            "orderItems": [
                {
                    "productUuid": str(uuid.uuid4()),
                    "quantity": 50,
                    "unitPrice": 80.00,
                    "totalPrice": 4000.00
                }
            ]
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_inventory_record_data(product_uuid=None, **kwargs):
        """创建库存记录测试数据"""
        default_data = {
            "productUuid": product_uuid or str(uuid.uuid4()),
            "transactionType": "purchase",
            "quantity": 100,
            "unitPrice": 50.00,
            "totalPrice": 5000.00,
            "transactionDate": datetime.now().isoformat(),
            "referenceNumber": "INV001",
            "notes": "库存记录备注"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_operation_log_data(**kwargs):
        """创建操作日志测试数据"""
        default_data = {
            "userId": str(uuid.uuid4()),
            "userName": "测试用户",
            "action": "create",
            "resource": "product",
            "resourceId": str(uuid.uuid4()),
            "details": "创建测试产品",
            "ipAddress": "192.168.1.1",
            "userAgent": "Mozilla/5.0 (测试浏览器)",
            "timestamp": datetime.now().isoformat()
        }
        default_data.update(kwargs)
        return default_data


class SampleDataSets:
    """样本数据集"""
    
    @staticmethod
    def get_sample_products():
        """获取样本产品数据"""
        return [
            TestDataFactory.create_product_data(
                productName="笔记本电脑",
                productCode="LAPTOP001",
                category="电子产品",
                unitPrice=5999.00,
                stockQuantity=50
            ),
            TestDataFactory.create_product_data(
                productName="智能手机",
                productCode="PHONE001",
                category="电子产品",
                unitPrice=2999.00,
                stockQuantity=100
            ),
            TestDataFactory.create_product_data(
                productName="办公桌",
                productCode="DESK001",
                category="办公家具",
                unitPrice=899.00,
                stockQuantity=30
            ),
            TestDataFactory.create_product_data(
                productName="打印机",
                productCode="PRINTER001",
                category="办公设备",
                unitPrice=1299.00,
                stockQuantity=20
            ),
            TestDataFactory.create_product_data(
                productName="路由器",
                productCode="ROUTER001",
                category="网络设备",
                unitPrice=299.00,
                stockQuantity=80
            )
        ]
    
    @staticmethod
    def get_sample_customers():
        """获取样本客户数据"""
        return [
            TestDataFactory.create_customer_data(
                customerName="科技有限公司",
                customerCode="TECH001",
                contactPerson="李总",
                creditLimit=50000.00
            ),
            TestDataFactory.create_customer_data(
                customerName="贸易有限公司",
                customerCode="TRADE001",
                contactPerson="王经理",
                creditLimit=30000.00
            ),
            TestDataFactory.create_customer_data(
                customerName="制造企业",
                customerCode="MANU001",
                contactPerson="张厂长",
                creditLimit=80000.00
            ),
            TestDataFactory.create_customer_data(
                customerName="零售商店",
                customerCode="RETAIL001",
                contactPerson="陈店长",
                creditLimit=20000.00
            ),
            TestDataFactory.create_customer_data(
                customerName="服务公司",
                customerCode="SERVICE001",
                contactPerson="刘总监",
                creditLimit=25000.00
            )
        ]
    
    @staticmethod
    def get_sample_suppliers():
        """获取样本供应商数据"""
        return [
            TestDataFactory.create_supplier_data(
                supplierName="电子制造厂",
                supplierCode="EMF001",
                contactPerson="赵厂长",
                paymentTerms="45天"
            ),
            TestDataFactory.create_supplier_data(
                supplierName="原材料供应商",
                supplierCode="RAW001",
                contactPerson="钱经理",
                paymentTerms="30天"
            ),
            TestDataFactory.create_supplier_data(
                supplierName="配件生产商",
                supplierCode="PART001",
                contactPerson="孙总监",
                paymentTerms="60天"
            ),
            TestDataFactory.create_supplier_data(
                supplierName="包装材料厂",
                supplierCode="PACK001",
                contactPerson="周主管",
                paymentTerms="30天"
            ),
            TestDataFactory.create_supplier_data(
                supplierName="物流服务商",
                supplierCode="LOGIS001",
                contactPerson="吴经理",
                paymentTerms="15天"
            )
        ]
    
    @staticmethod
    def get_sample_sales_orders(customer_uuids=None):
        """获取样本销售订单数据"""
        if customer_uuids is None:
            customer_uuids = [str(uuid.uuid4()) for _ in range(5)]
        
        return [
            TestDataFactory.create_sales_order_data(
                customerUuid=customer_uuids[0],
                orderNumber="SO2024001",
                totalAmount=12000.00
            ),
            TestDataFactory.create_sales_order_data(
                customerUuid=customer_uuids[1],
                orderNumber="SO2024002",
                totalAmount=8000.00
            ),
            TestDataFactory.create_sales_order_data(
                customerUuid=customer_uuids[2],
                orderNumber="SO2024003",
                totalAmount=15000.00
            ),
            TestDataFactory.create_sales_order_data(
                customerUuid=customer_uuids[3],
                orderNumber="SO2024004",
                totalAmount=6000.00
            ),
            TestDataFactory.create_sales_order_data(
                customerUuid=customer_uuids[4],
                orderNumber="SO2024005",
                totalAmount=10000.00
            )
        ]
    
    @staticmethod
    def get_sample_purchase_orders(supplier_uuids=None):
        """获取样本采购订单数据"""
        if supplier_uuids is None:
            supplier_uuids = [str(uuid.uuid4()) for _ in range(5)]
        
        return [
            TestDataFactory.create_purchase_order_data(
                supplierUuid=supplier_uuids[0],
                orderNumber="PO2024001",
                totalAmount=25000.00
            ),
            TestDataFactory.create_purchase_order_data(
                supplierUuid=supplier_uuids[1],
                orderNumber="PO2024002",
                totalAmount=18000.00
            ),
            TestDataFactory.create_purchase_order_data(
                supplierUuid=supplier_uuids[2],
                orderNumber="PO2024003",
                totalAmount=32000.00
            ),
            TestDataFactory.create_purchase_order_data(
                supplierUuid=supplier_uuids[3],
                orderNumber="PO2024004",
                totalAmount=15000.00
            ),
            TestDataFactory.create_purchase_order_data(
                supplierUuid=supplier_uuids[4],
                orderNumber="PO2024005",
                totalAmount=22000.00
            )
        ]


class EdgeCaseData:
    """边界情况测试数据"""
    
    @staticmethod
    def get_edge_case_products():
        """获取边界情况产品数据"""
        return [
            # 空字符串测试
            TestDataFactory.create_product_data(
                productName="",
                productCode="EDGE001",
                description=""
            ),
            # 极值测试
            TestDataFactory.create_product_data(
                productName="极值测试产品",
                productCode="EDGE002",
                unitPrice=999999.99,
                stockQuantity=999999
            ),
            # 负值测试
            TestDataFactory.create_product_data(
                productName="负值测试产品",
                productCode="EDGE003",
                unitPrice=-100.00,
                stockQuantity=-50
            ),
            # 特殊字符测试
            TestDataFactory.create_product_data(
                productName="特殊@字符#测试$",
                productCode="EDGE@004",
                description="包含特殊字符的描述！@#$"
            ),
            # 超长字符串测试
            TestDataFactory.create_product_data(
                productName="超长产品名称" * 10,
                productCode="EDGE005",
                description="超长描述" * 50
            )
        ]
    
    @staticmethod
    def get_invalid_data_sets():
        """获取无效数据集合"""
        return [
            # 缺失必填字段
            {
                "productName": "测试产品"
                # 缺少productCode等必填字段
            },
            # 错误数据类型
            {
                "productName": 123,  # 应该是字符串
                "productCode": "TEST001",
                "unitPrice": "invalid",  # 应该是数字
                "stockQuantity": "not_a_number"
            },
            # 无效的枚举值
            {
                "productName": "测试产品",
                "productCode": "TEST001",
                "orderStatus": "invalid_status",  # 无效的状态值
                "paymentStatus": "wrong_status"
            },
            # 无效的日期格式
            {
                "productName": "测试产品",
                "productCode": "TEST001",
                "orderDate": "2024/01/01",  # 无效的日期格式
                "expectedDeliveryDate": "01-01-2024"
            }
        ]


class PerformanceTestData:
    """性能测试数据"""
    
    @staticmethod
    def generate_large_product_dataset(count=1000):
        """生成大量产品测试数据"""
        products = []
        for i in range(count):
            product = TestDataFactory.create_product_data(
                productName=f"性能测试产品{i:04d}",
                productCode=f"PERF{i:04d}",
                unitPrice=100 + (i % 100),
                stockQuantity=50 + (i % 200)
            )
            products.append(product)
        return products
    
    @staticmethod
    def generate_large_customer_dataset(count=500):
        """生成大量客户测试数据"""
        customers = []
        for i in range(count):
            customer = TestDataFactory.create_customer_data(
                customerName=f"性能测试客户{i:04d}",
                customerCode=f"CUST{i:04d}",
                creditLimit=10000 + (i % 5000)
            )
            customers.append(customer)
        return customers
    
    @staticmethod
    def generate_large_order_dataset(count=2000, customer_uuids=None):
        """生成大量订单测试数据"""
        if customer_uuids is None:
            customer_uuids = [str(uuid.uuid4()) for _ in range(100)]
        
        orders = []
        for i in range(count):
            customer_uuid = customer_uuids[i % len(customer_uuids)]
            order = TestDataFactory.create_sales_order_data(
                customerUuid=customer_uuid,
                orderNumber=f"SO{i:06d}",
                totalAmount=1000 + (i % 5000)
            )
            orders.append(order)
        return orders


# 导出常用数据生成器
create_product = TestDataFactory.create_product_data
create_customer = TestDataFactory.create_customer_data
create_supplier = TestDataFactory.create_supplier_data
create_sales_order = TestDataFactory.create_sales_order_data
create_purchase_order = TestDataFactory.create_purchase_order_data
create_inventory_record = TestDataFactory.create_inventory_record_data
create_operation_log = TestDataFactory.create_operation_log_data

# 导出样本数据集
sample_products = SampleDataSets.get_sample_products
sample_customers = SampleDataSets.get_sample_customers
sample_suppliers = SampleDataSets.get_sample_suppliers
sample_sales_orders = SampleDataSets.get_sample_sales_orders
sample_purchase_orders = SampleDataSets.get_sample_purchase_orders

# 导出边界情况数据
edge_case_products = EdgeCaseData.get_edge_case_products
invalid_data_sets = EdgeCaseData.get_invalid_data_sets

# 导出性能测试数据
generate_large_product_dataset = PerformanceTestData.generate_large_product_dataset
generate_large_customer_dataset = PerformanceTestData.generate_large_customer_dataset
generate_large_order_dataset = PerformanceTestData.generate_large_order_dataset