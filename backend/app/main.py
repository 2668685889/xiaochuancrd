"""
进销存管理系统 - 后端主应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.routes import auth, products, suppliers, inventory, purchase_orders, sales_orders, customers, dashboard, product_models, product_categories, operation_logs, coze, coze_sync_template_routes
from app.middleware.operation_log_middleware import OperationLogMiddleware

# 导入所有模型以确保SQLAlchemy正确映射
from app.models import Product, Supplier, InventoryRecord, PurchaseOrder, SalesOrder, Customer, User, ProductModel, ProductCategory, OperationLog


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建默认管理员用户
    from app.core.database import AsyncSessionLocal
    from app.routes.auth import create_default_admin
    
    async with AsyncSessionLocal() as session:
        await create_default_admin(session)
    
    # 启动CDC服务
    from app.services.cdc_service import start_cdc_service
    cdc_task = await start_cdc_service()
    
    yield
    
    # 关闭时清理资源
    if cdc_task:
        cdc_task.cancel()
    await engine.dispose()


# 创建FastAPI应用实例
app = FastAPI(
    title="进销存管理系统",
    description="企业级进销存管理解决方案",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加操作日志中间件
app.add_middleware(OperationLogMiddleware)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(products.router, prefix="/api/v1", tags=["产品管理"])
app.include_router(suppliers.router, prefix="/api/v1", tags=["供应商管理"])
app.include_router(inventory.router, prefix="/api/v1", tags=["库存管理"])
app.include_router(purchase_orders.router, prefix="/api/v1", tags=["采购订单管理"])
app.include_router(sales_orders.router, prefix="/api/v1", tags=["销售订单管理"])
app.include_router(customers.router, prefix="/api/v1", tags=["客户管理"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["仪表盘"])
app.include_router(product_models.router, prefix="/api/v1", tags=["产品型号管理"])
app.include_router(product_categories.router, prefix="/api/v1", tags=["产品分类管理"])
app.include_router(operation_logs.router, prefix="/api/v1", tags=["操作日志管理"])
app.include_router(coze.router, prefix="/api/v1", tags=["Coze数据上传"])
app.include_router(coze_sync_template_routes.router, prefix="/api/v1", tags=["Coze同步模板"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "进销存管理系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )