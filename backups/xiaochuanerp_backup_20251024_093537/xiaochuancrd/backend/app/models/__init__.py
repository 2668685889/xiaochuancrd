"""
模型模块初始化
集中导入所有模型以解决循环导入问题
"""

# 导入所有模型
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.inventory import InventoryRecord
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.customer import Customer
from app.models.user import User
from app.models.product_model import ProductModel
from app.models.product_category import ProductCategory
from app.models.operation_log import OperationLog

# 导出所有模型
__all__ = [
    "Product",
    "Supplier", 
    "InventoryRecord",
    "PurchaseOrder",
    "SalesOrder",
    "Customer",
    "User",
    "ProductModel",
    "ProductCategory",
    "OperationLog"
]