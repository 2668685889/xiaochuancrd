"""
仪表盘API路由
提供仪表盘所需的统计数据
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Dict, Any

from app.core.database import get_db
from app.models import Product, Supplier, InventoryRecord, PurchaseOrder, SalesOrder

router = APIRouter()


@router.get("/Dashboard/Stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """获取仪表盘统计数据"""
    try:
        # 获取产品总数
        product_count_result = await db.execute(select(func.count(Product.uuid)))
        product_count = product_count_result.scalar() or 0
        
        # 获取供应商数量
        supplier_count_result = await db.execute(select(func.count(Supplier.uuid)))
        supplier_count = supplier_count_result.scalar() or 0
        
        # 获取库存总价值
        inventory_value_result = await db.execute(
            select(func.sum(Product.current_quantity * Product.unit_price))
        )
        inventory_value = inventory_value_result.scalar() or 0
        
        # 获取库存预警数量（库存低于最小库存的产品）
        low_stock_count_result = await db.execute(
            select(func.count(Product.uuid)).where(
                Product.current_quantity <= Product.min_quantity
            )
        )
        low_stock_count = low_stock_count_result.scalar() or 0
        
        # 获取今日销售订单数量
        today_sales_count_result = await db.execute(
            select(func.count(SalesOrder.uuid)).where(
                func.date(SalesOrder.created_at) == func.current_date()
            )
        )
        today_sales_count = today_sales_count_result.scalar() or 0
        
        # 获取今日采购订单数量
        today_purchase_count_result = await db.execute(
            select(func.count(PurchaseOrder.uuid)).where(
                func.date(PurchaseOrder.created_at) == func.current_date()
            )
        )
        today_purchase_count = today_purchase_count_result.scalar() or 0
        
        return {
            "productCount": product_count,
            "supplierCount": supplier_count,
            "inventoryValue": float(inventory_value),
            "lowStockCount": low_stock_count,
            "todaySalesCount": today_sales_count,
            "todayPurchaseCount": today_purchase_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/Dashboard/LowStockAlerts")
async def get_low_stock_alerts(db: AsyncSession = Depends(get_db)):
    """获取低库存预警列表"""
    try:
        low_stock_products_result = await db.execute(
            select(
                Product.uuid,
                Product.product_name,
                Product.product_code,
                Product.current_quantity,
                Product.min_quantity,
                Product.unit_price
            ).where(
                Product.current_quantity <= Product.min_quantity
            ).order_by(Product.current_quantity.asc())
        )
        
        low_stock_products = low_stock_products_result.fetchall()
        
        return {
            "alerts": [
                {
                    "uuid": str(product.uuid),
                    "productName": product.product_name,
                    "productCode": product.product_code,
                    "currentQuantity": product.current_quantity,
                    "minQuantity": product.min_quantity,
                    "unitPrice": float(product.unit_price)
                }
                for product in low_stock_products
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取低库存预警失败: {str(e)}")


@router.get("/Dashboard/ProductDistribution")
async def get_product_distribution(db: AsyncSession = Depends(get_db)):
    """获取产品分类分布数据（用于饼状图）"""
    try:
        # 检查是否有分类数据
        category_distribution_result = await db.execute(
            select(
                Product.category_name,
                func.count(Product.uuid).label("count"),
                func.sum(Product.current_quantity * Product.unit_price).label("value")
            ).group_by(Product.category_name)
        )
        
        category_distribution = category_distribution_result.fetchall()
        
        # 如果有分类数据且不是所有产品都未分类
        if category_distribution and any(category[0] for category in category_distribution):
            return {
                "distribution": [
                    {
                        "name": category if category else "未分类",
                        "value": float(value),
                        "count": count
                    }
                    for category, count, value in category_distribution
                ]
            }
        
        # 如果没有分类数据或所有产品都未分类，返回按库存价值分布
        # 获取库存价值最高的10个产品
        top_products_result = await db.execute(
            select(
                Product.uuid,
                Product.product_name,
                Product.current_quantity,
                Product.unit_price
            ).order_by((Product.current_quantity * Product.unit_price).desc()).limit(10)
        )
        
        top_products = top_products_result.fetchall()
        
        # 计算其他产品的总价值
        other_value_result = await db.execute(
            select(func.sum(Product.current_quantity * Product.unit_price))
        )
        total_value = other_value_result.scalar() or 0
        
        top_products_value = sum(product.current_quantity * product.unit_price for product in top_products)
        other_value = total_value - top_products_value
        
        distribution = [
            {
                "name": product.product_name,
                "value": float(product.current_quantity * product.unit_price),
                "count": product.current_quantity
            }
            for product in top_products
        ]
        
        if other_value > 0:
            distribution.append({
                "name": "其他产品",
                "value": float(other_value),
                "count": 0
            })
        
        return {"distribution": distribution}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取产品分布数据失败: {str(e)}")


@router.get("/Dashboard/RecentActivities")
async def get_recent_activities(db: AsyncSession = Depends(get_db)):
    """获取最近活动记录"""
    try:
        # 获取最近的库存变动记录
        recent_inventory_changes_result = await db.execute(
            select(
                InventoryRecord.uuid,
                InventoryRecord.change_type,
                InventoryRecord.quantity_change,
                InventoryRecord.remark,
                InventoryRecord.created_at,
                Product.product_name
            ).join(Product, InventoryRecord.product_uuid == Product.uuid)
            .order_by(InventoryRecord.created_at.desc())
            .limit(10)
        )
        
        recent_inventory_changes = recent_inventory_changes_result.fetchall()
        
        # 获取最近的订单记录
        recent_purchase_orders_result = await db.execute(
            select(
                PurchaseOrder.uuid,
                PurchaseOrder.order_number,
                PurchaseOrder.status,
                PurchaseOrder.created_at,
                Supplier.supplier_name
            ).join(Supplier, PurchaseOrder.supplier_uuid == Supplier.uuid)
            .order_by(PurchaseOrder.created_at.desc())
            .limit(5)
        )
        
        recent_purchase_orders = recent_purchase_orders_result.fetchall()
        
        # 获取最近的销售订单记录
        recent_sales_orders_result = await db.execute(
            select(
                SalesOrder.uuid,
                SalesOrder.order_number,
                SalesOrder.status,
                SalesOrder.created_at,
                SalesOrder.customer_name
            ).order_by(SalesOrder.created_at.desc())
            .limit(5)
        )
        
        recent_sales_orders = recent_sales_orders_result.fetchall()
        
        activities = []
        
        # 添加库存变动活动
        for change in recent_inventory_changes:
            activity_type = "库存调整"
            if change.change_type == "IN":
                activity_type = "入库"
            elif change.change_type == "OUT":
                activity_type = "出库"
            
            activities.append({
                "type": "inventory",
                "action": activity_type,
                "description": f"{change.product_name} {activity_type} {change.quantity_change}件",
                "user": "系统",  # 这里可以根据实际情况获取用户信息
                "time": change.created_at.isoformat()
            })
        
        # 添加采购订单活动
        for order in recent_purchase_orders:
            activities.append({
                "type": "purchase",
                "action": "创建采购订单",
                "description": f"向 {order.supplier_name} 采购",
                "user": "采购员",  # 这里可以根据实际情况获取用户信息
                "time": order.created_at.isoformat()
            })
        
        # 添加销售订单活动
        for order in recent_sales_orders:
            activities.append({
                "type": "sales",
                "action": "创建销售订单",
                "description": f"向 {order.customer_name} 销售",
                "user": "销售员",  # 这里可以根据实际情况获取用户信息
                "time": order.created_at.isoformat()
            })
        
        # 按时间排序并返回前10个
        activities.sort(key=lambda x: x["time"], reverse=True)
        
        return {"activities": activities[:10]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近活动失败: {str(e)}")