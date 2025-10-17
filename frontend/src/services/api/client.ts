import axios from 'axios';
import type { 
  Product, 
  CreateProductRequest, 
  UpdateProductRequest,
  Supplier, 
  CreateSupplierRequest, 
  UpdateSupplierRequest,
  Customer,
  CreateCustomerRequest,
  UpdateCustomerRequest,
  InventoryRecord,
  CreateInventoryRecordRequest,
  InventorySummary,
  InventoryAlert,
  ApiResponse, 
  PaginatedResponse,
  DashboardStats,
  LowStockAlert,
  ProductDistribution,
  RecentActivity,
  ProductModel,
  CreateProductModelRequest,
  UpdateProductModelRequest,
  ProductCategory,
  CreateProductCategoryRequest,
  UpdateProductCategoryRequest,
  ProductCategoryTreeResponse,
  ProductSpecification
} from '../../types';
import type {
  PurchaseOrder,
  CreatePurchaseOrderRequest,
  UpdatePurchaseOrderRequest
} from '../../types/purchaseOrder';
import type {
  SalesOrder,
  CreateSalesOrderRequest,
  UpdateSalesOrderRequest
} from '../../types/salesOrder';

class ApiClient {
  private baseURL = import.meta.env.VITE_API_BASE_URL || ''; // 使用环境变量配置API基础URL
  private client = axios.create({
    baseURL: this.baseURL,
    timeout: 10000,
  });

  constructor() {
    this.setupInterceptors();
  }

  /**
   * 处理规格参数格式转换
   * 后端返回的规格参数已经是数组格式，但需要确保格式正确
   */
  private convertSpecificationsToArray(specifications: any): ProductSpecification[] {
    // 如果已经是数组格式，直接返回
    if (Array.isArray(specifications)) {
      return specifications.map(spec => ({
        key: spec.key || '',
        value: spec.value || '',
        unit: spec.unit || ''
      }));
    }
    
    // 如果是字典格式，转换为数组格式（兼容旧版本）
    if (specifications && typeof specifications === 'object') {
      return Object.entries(specifications).map(([key, value]) => {
        // 如果value是对象，提取unit和value
        if (typeof value === 'object' && value !== null && value !== undefined) {
          const valueObj = value as any;
          return {
            key,
            value: valueObj.value || String(value),
            unit: valueObj.unit || ''
          };
        }
        
        // 如果value是简单值
        return {
          key,
          value: String(value),
          unit: ''
        };
      });
    }
    
    return [];
  }

  /**
   * 将前端规格参数数组转换为后端期望的字典格式
   */
  private convertSpecificationsToObject(specifications: ProductSpecification[]): Record<string, any> {
    if (!Array.isArray(specifications)) {
      return {};
    }
    
    const result: Record<string, any> = {};
    
    specifications.forEach(spec => {
      if (spec.unit) {
        // 如果有单位，存储为对象格式
        result[spec.key] = {
          value: spec.value,
          unit: spec.unit
        };
      } else {
        // 如果没有单位，存储为简单值
        result[spec.key] = spec.value;
      }
    });
    
    return result;
  }

  private setupInterceptors() {
    // 请求拦截器 - 不再转换数据格式，由后端统一处理
    this.client.interceptors.request.use(
      (config) => {
        // 添加认证token
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器 - 不再转换数据格式，由后端统一处理
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * 通用请求方法，用于处理Coze API等特殊接口
   */
  async request(endpoint: string, options: { method?: string; headers?: Record<string, string>; body?: any; params?: Record<string, any> } = {}): Promise<any> {
    // 在开发模式下使用相对路径，让Vite代理处理请求转发
    const isDevelopment = import.meta.env.MODE === 'development';
    const baseURL = isDevelopment ? '' : this.baseURL;
    let url = `${baseURL}${endpoint}`;
    
    // 处理请求配置
    const config: RequestInit = {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // 添加认证token
    const token = localStorage.getItem('auth_token');
    if (token) {
      (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
    }

    // 处理请求体
    if (options.body) {
      config.body = JSON.stringify(options.body);
    }

    // 处理查询参数
    if (options.params) {
      const params = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
      url += `?${params.toString()}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // 产品相关API
  async getProducts(params?: { page?: number; pageSize?: number; search?: string }): Promise<PaginatedResponse<Product>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Product>>>('/api/v1/Products', { params });
    return response.data.data;
  }

  async getProduct(uuid: string): Promise<Product> {
    const response = await this.client.get<ApiResponse<Product>>(`/api/v1/Products/${uuid}`);
    return response.data.data;
  }

  async createProduct(productData: CreateProductRequest): Promise<Product> {
    const response = await this.client.post<ApiResponse<Product>>('/api/v1/Products', productData);
    return response.data.data;
  }

  async updateProduct(uuid: string, productData: UpdateProductRequest): Promise<Product> {
    const response = await this.client.put<ApiResponse<Product>>(`/api/v1/Products/${uuid}`, productData);
    return response.data.data;
  }

  async deleteProduct(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/Products/${uuid}`);
  }

  // 产品型号相关API
  async getProductModels(params?: { page?: number; pageSize?: number; search?: string; category?: string }): Promise<PaginatedResponse<ProductModel>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<any>>>('/api/v1/ProductModels', { params });
    
    // 处理规格参数格式转换
    const data = response.data.data;
    if (data && data.items) {
      data.items = data.items.map((item: any) => ({
        ...item,
        specifications: this.convertSpecificationsToArray(item.specifications)
      }));
    }
    
    return data;
  }

  async getProductModel(uuid: string): Promise<ProductModel> {
    const response = await this.client.get<ApiResponse<any>>(`/api/v1/ProductModels/${uuid}`);
    
    // 处理规格参数格式转换
    const data = response.data.data;
    if (data) {
      data.specifications = this.convertSpecificationsToArray(data.specifications);
    }
    
    return data;
  }

  async createProductModel(modelData: CreateProductModelRequest): Promise<ProductModel> {
    // 转换规格参数格式为后端期望的字典格式
    const requestData = {
      ...modelData,
      specifications: this.convertSpecificationsToObject(modelData.specifications || [])
    };
    
    const response = await this.client.post<ApiResponse<any>>('/api/v1/ProductModels', requestData);
    
    // 处理返回数据的规格参数格式转换
    const data = response.data.data;
    if (data) {
      data.specifications = this.convertSpecificationsToArray(data.specifications);
    }
    
    return data;
  }

  async updateProductModel(uuid: string, modelData: UpdateProductModelRequest): Promise<ProductModel> {
    // 转换规格参数格式为后端期望的字典格式
    const requestData = {
      ...modelData,
      specifications: this.convertSpecificationsToObject(modelData.specifications || [])
    };
    
    const response = await this.client.put<ApiResponse<any>>(`/api/v1/ProductModels/${uuid}`, requestData);
    
    // 处理返回数据的规格参数格式转换
    const data = response.data.data;
    if (data) {
      data.specifications = this.convertSpecificationsToArray(data.specifications);
    }
    
    return data;
  }

  async deleteProductModel(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/ProductModels/${uuid}`);
  }

  // 产品分类相关API
  async getProductCategories(params?: { page?: number; pageSize?: number; search?: string; parentUuid?: string }): Promise<PaginatedResponse<ProductCategory>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<ProductCategory>>>('/api/v1/ProductCategories', { params });
    return response.data.data;
  }

  async getProductCategoryTree(): Promise<ProductCategoryTreeResponse> {
    const response = await this.client.get<ApiResponse<ProductCategoryTreeResponse>>('/api/v1/ProductCategories/tree');
    return response.data.data;
  }

  async getProductCategory(uuid: string): Promise<ProductCategory> {
    const response = await this.client.get<ApiResponse<ProductCategory>>(`/api/v1/ProductCategories/${uuid}`);
    return response.data.data;
  }

  async createProductCategory(categoryData: CreateProductCategoryRequest): Promise<ProductCategory> {
    const response = await this.client.post<ApiResponse<ProductCategory>>('/api/v1/ProductCategories', categoryData);
    return response.data.data;
  }

  async updateProductCategory(uuid: string, categoryData: UpdateProductCategoryRequest): Promise<ProductCategory> {
    const response = await this.client.put<ApiResponse<ProductCategory>>(`/api/v1/ProductCategories/${uuid}`, categoryData);
    return response.data.data;
  }

  async deleteProductCategory(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/ProductCategories/${uuid}`);
  }

  // 供应商相关API
  async getSuppliers(params?: { page?: number; pageSize?: number; search?: string }): Promise<PaginatedResponse<Supplier>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Supplier>>>('/api/v1/Suppliers', { params });
    return response.data.data;
  }

  async createSupplier(supplierData: CreateSupplierRequest): Promise<Supplier> {
    const response = await this.client.post<ApiResponse<Supplier>>('/api/v1/Suppliers', supplierData);
    return response.data.data;
  }

  async updateSupplier(uuid: string, supplierData: UpdateSupplierRequest): Promise<Supplier> {
    const response = await this.client.put<ApiResponse<Supplier>>(`/api/v1/Suppliers/${uuid}`, supplierData);
    return response.data.data;
  }

  async deleteSupplier(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/Suppliers/${uuid}`);
  }

  // 客户相关API
  async getCustomers(params?: { page?: number; size?: number; search?: string; isActive?: boolean }): Promise<PaginatedResponse<Customer>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Customer>>>('/api/v1/Customers', { params });
    return response.data.data;
  }

  async getCustomer(uuid: string): Promise<Customer> {
    const response = await this.client.get<ApiResponse<Customer>>(`/api/v1/Customers/${uuid}`);
    return response.data.data;
  }

  async createCustomer(customerData: CreateCustomerRequest): Promise<Customer> {
    const response = await this.client.post<ApiResponse<Customer>>('/api/v1/Customers', customerData);
    return response.data.data;
  }

  async updateCustomer(uuid: string, customerData: UpdateCustomerRequest): Promise<Customer> {
    const response = await this.client.put<ApiResponse<Customer>>(`/api/v1/Customers/${uuid}`, customerData);
    return response.data.data;
  }

  async deleteCustomer(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/Customers/${uuid}`);
  }

  // 认证相关API
  async login(credentials: { username: string; password: string }): Promise<{ token: string; user: any }> {
    // 后端返回的数据包装在ApiResponse中
    const response = await this.client.post<ApiResponse<{ accessToken: string; tokenType: string; user: any }>>('/api/v1/auth/login', credentials);
    
    // 检查响应数据是否存在
    if (!response.data.data) {
      throw new Error('登录响应数据为空');
    }
    
    // 将accessToken映射为token返回
    return {
      token: response.data.data.accessToken,
      user: response.data.data.user
    };
  }

  async register(userData: { username: string; email: string; password: string }): Promise<void> {
    await this.client.post('/api/v1/auth/register', userData);
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/auth/me');
    return response.data.data;
  }

  // 库存相关API
  async getInventoryRecords(params?: { 
    page?: number; 
    size?: number; 
    productUuid?: string; 
    changeType?: 'IN' | 'OUT' | 'ADJUST'; 
    startDate?: string; 
    endDate?: string; 
    search?: string; 
  }): Promise<PaginatedResponse<InventoryRecord>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<InventoryRecord>>>('/api/v1/Inventory', { params });
    return response.data.data;
  }

  async getInventoryRecord(uuid: string): Promise<InventoryRecord> {
    const response = await this.client.get<ApiResponse<InventoryRecord>>(`/api/v1/Inventory/${uuid}`);
    return response.data.data;
  }

  async createInventoryRecord(recordData: CreateInventoryRecordRequest): Promise<InventoryRecord> {
    const response = await this.client.post<ApiResponse<InventoryRecord>>('/api/v1/Inventory', recordData);
    return response.data.data;
  }

  async getInventorySummary(): Promise<InventorySummary> {
    const response = await this.client.get<ApiResponse<InventorySummary>>('/api/v1/Inventory/Summary');
    return response.data.data;
  }

  async getInventoryAlerts(): Promise<InventoryAlert[]> {
    const response = await this.client.get<ApiResponse<{ alerts: InventoryAlert[] }>>('/api/v1/Inventory/Alerts');
    return response.data.data.alerts;
  }

  // 采购订单相关API
  async getPurchaseOrders(params: {
    page?: number;
    size?: number;
    search?: string;
    statusFilter?: string;
    supplierUuid?: string;
    productUuid?: string;
    startDate?: string;
    endDate?: string;
    minAmount?: number;
    maxAmount?: number;
  } = {}): Promise<PaginatedResponse<PurchaseOrder>> {
    const { page = 1, size = 20, search, statusFilter, supplierUuid, productUuid, startDate, endDate, minAmount, maxAmount } = params;
    
    const backendParams: any = {
      page,
      size,
    };
    
    if (search) backendParams.search = search;
    if (statusFilter) backendParams.status_filter = statusFilter;
    if (supplierUuid) backendParams.supplier_uuid = supplierUuid;
    if (productUuid) backendParams.product_uuid = productUuid;
    if (startDate) backendParams.start_date = startDate;
    if (endDate) backendParams.end_date = endDate;
    if (minAmount !== undefined) backendParams.min_amount = minAmount;
    if (maxAmount !== undefined) backendParams.max_amount = maxAmount;
    
    const response = await this.client.get<ApiResponse<PaginatedResponse<PurchaseOrder>>>('/api/v1/PurchaseOrders', { 
      params: backendParams 
    });
    return response.data.data;
  }

  async getPurchaseOrder(uuid: string): Promise<PurchaseOrder> {
    const response = await this.client.get<ApiResponse<PurchaseOrder>>(`/api/v1/PurchaseOrders/${uuid}`);
    return response.data.data;
  }

  async createPurchaseOrder(orderData: CreatePurchaseOrderRequest): Promise<PurchaseOrder> {
    const response = await this.client.post<ApiResponse<PurchaseOrder>>('/api/v1/PurchaseOrders', orderData);
    return response.data.data;
  }

  async updatePurchaseOrder(uuid: string, orderData: UpdatePurchaseOrderRequest): Promise<PurchaseOrder> {
    const response = await this.client.put<ApiResponse<PurchaseOrder>>(`/api/v1/PurchaseOrders/${uuid}`, orderData);
    return response.data.data;
  }

  async deletePurchaseOrder(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/PurchaseOrders/${uuid}`);
  }

  // 销售订单相关API
  async getSalesOrders(params?: { page?: number; size?: number; search?: string }): Promise<PaginatedResponse<SalesOrder>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<SalesOrder>>>('/api/v1/SalesOrders', { params });
    return response.data.data;
  }

  async getSalesOrder(uuid: string): Promise<SalesOrder> {
    const response = await this.client.get<ApiResponse<SalesOrder>>(`/api/v1/SalesOrders/${uuid}`);
    return response.data.data;
  }

  async createSalesOrder(orderData: CreateSalesOrderRequest): Promise<SalesOrder> {
    const response = await this.client.post<ApiResponse<SalesOrder>>('/api/v1/SalesOrders', orderData);
    return response.data.data;
  }

  async updateSalesOrder(uuid: string, orderData: UpdateSalesOrderRequest): Promise<SalesOrder> {
    const response = await this.client.put<ApiResponse<SalesOrder>>(`/api/v1/SalesOrders/${uuid}`, orderData);
    return response.data.data;
  }

  async deleteSalesOrder(uuid: string): Promise<void> {
    await this.client.delete(`/api/v1/SalesOrders/${uuid}`);
  }

  // 仪表盘相关API
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get<DashboardStats>('/api/v1/Dashboard/Stats');
    return response.data;
  }

  async getLowStockAlerts(): Promise<{ alerts: LowStockAlert[] }> {
    const response = await this.client.get<{ alerts: LowStockAlert[] }>('/api/v1/Dashboard/LowStockAlerts');
    return response.data;
  }

  async getProductDistribution(): Promise<{ distribution: ProductDistribution[] }> {
    const response = await this.client.get<{ distribution: ProductDistribution[] }>('/api/v1/Dashboard/ProductDistribution');
    return response.data;
  }

  async getRecentActivities(): Promise<{ activities: RecentActivity[] }> {
    const response = await this.client.get<{ activities: RecentActivity[] }>('/api/v1/Dashboard/RecentActivities');
    return response.data;
  }
}

export const apiClient = new ApiClient();