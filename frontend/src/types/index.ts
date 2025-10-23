export interface Product {
  uuid: string;
  productName: string;
  productCode: string;
  unitPrice: number;
  currentQuantity: number;
  minQuantity: number;
  maxQuantity: number;
  supplierUuid?: string;
  supplierName?: string;
  modelUuid?: string;
  modelName?: string;
  specifications?: Record<string, any>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProductRequest {
  productName: string;
  productCode: string;
  unitPrice: number;
  currentQuantity: number;
  minQuantity: number;
  maxQuantity: number;
}

export interface UpdateProductRequest extends Partial<CreateProductRequest> {
  isActive?: boolean;
}

// 产品型号相关类型
export interface ProductModel {
  uuid: string;
  modelName: string;
  modelCode: string;
  categoryUuid?: string;
  categoryName?: string;
  specifications: ProductSpecification[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProductSpecification {
  key: string;
  value: string;
  unit?: string;
}

export interface CreateProductModelRequest {
  modelName: string;
  modelCode: string;
  description?: string;
  categoryUuid: string;
  specifications: ProductSpecification[];
}

export interface UpdateProductModelRequest extends Partial<CreateProductModelRequest> {
  isActive?: boolean;
}

// 产品分类相关类型
export interface ProductCategory {
  uuid: string;
  categoryName: string;
  categoryCode: string;
  description?: string;
  parentUuid?: string;
  parentName?: string;
  sortOrder: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProductCategoryWithChildren extends ProductCategory {
  children?: ProductCategoryWithChildren[];
}

export interface ProductCategoryTreeResponse {
  items: ProductCategoryWithChildren[];
  total: number;
}

export interface CreateProductCategoryRequest {
  categoryName: string;
  categoryCode: string;
  description?: string;
  parentUuid?: string;
  sortOrder?: number;
}

export interface UpdateProductCategoryRequest extends Partial<CreateProductCategoryRequest> {
  isActive?: boolean;
}

export interface Supplier {
  uuid: string;
  supplierName: string;
  supplierCode: string;
  contactPerson: string;
  phone: string;
  email: string;
  address: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateSupplierRequest {
  supplierName: string;
  supplierCode: string;
  contactPerson: string;
  phone: string;
  email: string;
  address: string;
}

export interface UpdateSupplierRequest extends Partial<CreateSupplierRequest> {
  isActive?: boolean;
}

// 客户相关类型
export interface Customer {
  uuid: string;
  customerName: string;
  customerCode: string;
  contactPerson: string;
  phone: string;
  email: string;
  address: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateCustomerRequest {
  customerName: string;
  customerCode: string;
  contactPerson: string;
  phone: string;
  email: string;
  address: string;
}

export interface UpdateCustomerRequest extends Partial<CreateCustomerRequest> {
  isActive?: boolean;
}

export interface InventoryRecord {
  uuid: string;
  productUuid: string;
  productName: string;
  productCode: string;
  changeType: 'IN' | 'OUT' | 'ADJUST';
  quantityChange: number;
  currentQuantity: number;
  remark: string;
  recordDate: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateInventoryRecordRequest {
  productUuid: string;
  changeType: 'IN' | 'OUT' | 'ADJUST';
  quantityChange: number;
  remark?: string;
  recordDate?: string;
}

export interface InventorySummary {
  totalProducts: number;
  totalValue: number;
  lowStockCount: number;
  highStockCount: number;
  todayIn: number;
  todayOut: number;
  lowStockProducts: Array<{
    uuid: string;
    productName: string;
    currentQuantity: number;
    minQuantity: number;
  }>;
  highStockProducts: Array<{
    uuid: string;
    productName: string;
    currentQuantity: number;
    maxQuantity: number;
  }>;
}

export interface InventoryAlert {
  type: 'LOW_STOCK' | 'HIGH_STOCK';
  productUuid: string;
  productName: string;
  currentQuantity: number;
  minQuantity?: number;
  maxQuantity?: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface User {
  uuid: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ErrorResponse {
  success: false;
  error: string;
  message: string;
  details?: any;
}

// 表单验证类型
export interface ValidationRules {
  [key: string]: {
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    custom?: (value: any) => string | null;
  };
}

// 表格列配置
export interface TableColumn<T> {
  key: keyof T | string;
  title: string;
  width?: number;
  sortable?: boolean;
  render?: (value: any, record: T) => React.ReactNode;
}

// 搜索参数
export interface SearchParams {
  page?: number;
  size?: number;
  search?: string;
  [key: string]: any;
}

// 仪表盘相关类型
export interface DashboardStats {
  productCount: number;
  supplierCount: number;
  inventoryValue: number;
  lowStockCount: number;
  todaySalesCount: number;
  todayPurchaseCount: number;
}

export interface LowStockAlert {
  uuid: string;
  productName: string;
  productCode: string;
  currentQuantity: number;
  minQuantity: number;
  unitPrice: number;
}

export interface ProductDistribution {
  name: string;
  value: number;
  count: number;
}

export interface RecentActivity {
  type: 'inventory' | 'purchase' | 'sales';
  action: string;
  description: string;
  user: string;
  time: string;
}

export interface SalesData {
  period: string;
  salesAmount: number;
  salesCount: number;
  averageAmount: number;
}



