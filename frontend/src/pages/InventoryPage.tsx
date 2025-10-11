import React, { useState, useEffect } from 'react';
import { Search, Filter, TrendingUp, TrendingDown, AlertTriangle, Package } from 'lucide-react';
import { apiClient } from '../services/api/client';
import type { Product } from '../types';

const InventoryPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'low' | 'high'>('all');

  // 加载产品列表（包含库存信息）
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const productsResponse = await apiClient.getProducts({ page: 1, pageSize: 1000 });
      setProducts(productsResponse.items);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 计算库存预警状态
  const getInventoryStatus = (product: Product) => {
    if (product.currentQuantity <= product.minQuantity) return 'low';
    if (product.currentQuantity >= product.maxQuantity) return 'high';
    return 'normal';
  };

  // 过滤产品列表
  const filteredProducts = products.filter(product => {
    // 搜索过滤
    const matchesSearch = product.productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.productCode.toLowerCase().includes(searchTerm.toLowerCase());
    
    // 状态过滤
    const status = getInventoryStatus(product);
    const matchesFilter = filterType === 'all' || 
                         (filterType === 'low' && status === 'low') ||
                         (filterType === 'high' && status === 'high');
    
    return matchesSearch && matchesFilter;
  });

  // 统计信息
  const stats = {
    totalProducts: products.length,
    lowStock: products.filter(product => product.currentQuantity <= product.minQuantity).length,
    highStock: products.filter(product => product.currentQuantity >= product.maxQuantity).length,
    totalValue: products.reduce((sum, product) => sum + (product.currentQuantity * product.unitPrice), 0)
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">库存管理</h1>
        <p className="text-gray-600 mt-1">实时监控库存状态和预警信息</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">总产品数</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalProducts}</p>
            </div>
            <Package className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">库存预警</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{stats.lowStock}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">库存积压</p>
              <p className="text-2xl font-bold text-orange-600 mt-1">{stats.highStock}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-orange-600" />
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">库存总值</p>
              <p className="text-2xl font-bold text-green-600 mt-1">¥{stats.totalValue.toLocaleString()}</p>
            </div>
            <TrendingDown className="w-8 h-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* 搜索和过滤栏 */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="搜索产品名称或编码..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as any)}
              className="input-field"
            >
              <option value="all">全部库存</option>
              <option value="low">库存预警</option>
              <option value="high">库存积压</option>
            </select>
          </div>
          <button onClick={loadData} className="btn-secondary">
            刷新
          </button>
        </div>
      </div>

      {/* 库存列表 */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  产品信息
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  供货商
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  产品型号
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  售价
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  当前库存
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  库存范围
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  库存价值
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  最后更新
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                  </td>
                </tr>
              ) : filteredProducts.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center text-gray-500">
                    暂无库存数据
                  </td>
                </tr>
              ) : (
                filteredProducts.map((product) => {
                  const status = getInventoryStatus(product);
                  
                  return (
                    <tr key={product.uuid} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {product.productName}
                          </div>
                          <div className="text-sm text-gray-500">
                            {product.productCode}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {product.supplierName || '未设置'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {product.modelName || '未设置'}
                          {product.specifications && typeof product.specifications === 'object' && Object.keys(product.specifications).length > 0 && (
                            <div className="text-xs text-gray-400 mt-1">
                              {Object.entries(product.specifications)
                                .map(([key, value]) => {
                                  // 确保key和value都是字符串，避免React渲染对象错误
                                  const safeKey = String(key);
                                  const safeValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
                                  return `${safeKey}: ${safeValue}`;
                                })
                                .join(' | ')}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          ¥{product.unitPrice.toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-medium">
                          {product.currentQuantity}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {product.minQuantity} - {product.maxQuantity}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          ¥{(product.currentQuantity * product.unitPrice).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          status === 'low' ? 'bg-red-100 text-red-800' :
                          status === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {status === 'low' ? '库存预警' :
                           status === 'high' ? '库存积压' : '正常'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(product.updatedAt).toLocaleDateString('zh-CN')}
                      </td>
                    </tr>
                  );
                })
              )}
              
              {!loading && filteredProducts.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-gray-500">
                    <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p>暂无库存数据</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 库存预警提示 */}
      {stats.lowStock > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">
                库存预警提醒
              </h3>
              <p className="text-sm text-red-700 mt-1">
                有 {stats.lowStock} 个产品库存低于安全水平，请及时补充库存。
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryPage;