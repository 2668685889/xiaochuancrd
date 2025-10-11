import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Eye, Filter, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api/client';
import { PurchaseOrder, CreatePurchaseOrderRequest, UpdatePurchaseOrderRequest } from '../types/purchaseOrder';
import PurchaseOrderForm from '../components/PurchaseOrderForm';

const PurchaseOrderPage: React.FC = () => {
  const navigate = useNavigate();
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editingOrder, setEditingOrder] = useState<PurchaseOrder | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [filters, setFilters] = useState({
    supplierUuid: '',
    productUuid: '',
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: ''
  });

  const fetchPurchaseOrders = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getPurchaseOrders({ 
        page: currentPage, 
        size: pageSize, 
        search: searchTerm || undefined,
        supplierUuid: filters.supplierUuid || undefined,
        productUuid: filters.productUuid || undefined,
        startDate: filters.startDate || undefined,
        endDate: filters.endDate || undefined,
        minAmount: filters.minAmount ? parseFloat(filters.minAmount) : undefined,
        maxAmount: filters.maxAmount ? parseFloat(filters.maxAmount) : undefined
      });
      // 确保response存在且有items字段
      if (response && response.items) {
        setPurchaseOrders(response.items);
        setTotal(response.total);
      } else {
        console.error('API返回数据格式错误:', response);
        setPurchaseOrders([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('获取采购订单列表失败:', error);
      setPurchaseOrders([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  // 加载供应商列表
  const loadSuppliers = async () => {
    try {
      const response = await apiClient.getSuppliers({ page: 1, pageSize: 1000 });
      setSuppliers(response.items || []);
    } catch (error) {
      console.error('加载供应商列表失败:', error);
    }
  };

  // 加载商品列表
  const loadProducts = async () => {
    try {
      const response = await apiClient.getProducts({ page: 1, pageSize: 1000 });
      setProducts(response.items || []);
    } catch (error) {
      console.error('加载商品列表失败:', error);
    }
  };

  useEffect(() => {
    fetchPurchaseOrders();
    loadSuppliers();
    loadProducts();
  }, [currentPage]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchPurchaseOrders();
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleApplyFilters = () => {
    setCurrentPage(1);
    fetchPurchaseOrders();
    setShowFilters(false);
  };

  const handleResetFilters = () => {
    setFilters({
      supplierUuid: '',
      productUuid: '',
      startDate: '',
      endDate: '',
      minAmount: '',
      maxAmount: ''
    });
    setCurrentPage(1);
    fetchPurchaseOrders();
  };

  const getStatusOptions = () => [
    { value: '', label: '全部状态' },
    { value: 'PENDING', label: '待审核' },
    { value: 'CONFIRMED', label: '已确认' },
    { value: 'RECEIVED', label: '已收货' },
    { value: 'CANCELLED', label: '已取消' }
  ];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const hasActiveFilters = () => {
    return Object.values(filters).some(value => value !== '');
  };

  const handleDelete = async (uuid: string) => {
    if (window.confirm('确定要删除这个采购订单吗？')) {
      try {
        await apiClient.deletePurchaseOrder(uuid);
        fetchPurchaseOrders();
      } catch (error) {
        console.error('删除采购订单失败:', error);
      }
    }
  };

  // 编辑采购订单
  const handleEditOrder = async (order: PurchaseOrder) => {
    try {
      // 从API获取最新的订单数据
      const latestOrder = await apiClient.getPurchaseOrder(order.uuid);
      setEditingOrder(latestOrder);
      setShowForm(true);
    } catch (error) {
      console.error('获取采购订单详情失败:', error);
      // 如果获取失败，使用当前页面数据作为备选方案
      setEditingOrder(order);
      setShowForm(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题和操作按钮 */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">采购订单管理</h1>
          <button
            onClick={() => {
              setEditingOrder(null);
              setShowForm(true);
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus size={16} />
            新建采购订单
          </button>
        </div>

        {/* 搜索和筛选栏 */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* 搜索框 */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="搜索订单编号、供应商名称..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </form>

            {/* 筛选按钮 */}
            <div className="flex gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 border rounded-lg flex items-center gap-2 ${
                  hasActiveFilters() 
                    ? 'border-blue-500 text-blue-600 bg-blue-50' 
                    : 'border-gray-300 text-gray-700'
                }`}
              >
                <Filter size={16} />
                筛选
                {hasActiveFilters() && (
                  <span className="bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    !
                  </span>
                )}
              </button>
              
              {hasActiveFilters() && (
                <button
                  onClick={handleResetFilters}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg flex items-center gap-2"
                >
                  <X size={16} />
                  重置
                </button>
              )}
            </div>
          </div>

          {/* 筛选面板 */}
          {showFilters && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* 供应商筛选 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">供应商</label>
                  <select
                    value={filters.supplierUuid}
                    onChange={(e) => handleFilterChange('supplierUuid', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">全部供应商</option>
                    {suppliers.map(supplier => (
                      <option key={supplier.uuid} value={supplier.uuid}>{supplier.supplierName}</option>
                    ))}
                  </select>
                </div>

                {/* 商品筛选 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">商品</label>
                  <select
                    value={filters.productUuid}
                    onChange={(e) => handleFilterChange('productUuid', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">全部商品</option>
                    {products.map(product => (
                      <option key={product.uuid} value={product.uuid}>{product.productName}</option>
                    ))}
                  </select>
                </div>

                {/* 日期范围筛选 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
                  <input
                    type="date"
                    value={filters.startDate}
                    onChange={(e) => handleFilterChange('startDate', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">结束日期</label>
                  <input
                    type="date"
                    value={filters.endDate}
                    onChange={(e) => handleFilterChange('endDate', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* 金额范围筛选 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">最小金额</label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.minAmount}
                    onChange={(e) => handleFilterChange('minAmount', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">最大金额</label>
                  <input
                    type="number"
                    placeholder="不限"
                    value={filters.maxAmount}
                    onChange={(e) => handleFilterChange('maxAmount', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* 筛选操作按钮 */}
              <div className="flex justify-end gap-2 mt-4">
                <button
                  onClick={() => setShowFilters(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  onClick={handleApplyFilters}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  应用筛选
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 筛选状态显示 */}
        {hasActiveFilters() && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-blue-800">
                <span>当前筛选条件：</span>
                {filters.supplierUuid && (
                  <span className="bg-blue-100 px-2 py-1 rounded">
                    供应商：{suppliers.find(s => s.uuid === filters.supplierUuid)?.supplierName}
                  </span>
                )}
                {filters.productUuid && (
                  <span className="bg-blue-100 px-2 py-1 rounded">
                    商品：{products.find(p => p.uuid === filters.productUuid)?.productName}
                  </span>
                )}
                {filters.startDate && (
                  <span className="bg-blue-100 px-2 py-1 rounded">
                    开始日期：{filters.startDate}
                  </span>
                )}
                {filters.endDate && (
                  <span className="bg-blue-100 px-2 py-1 rounded">
                    结束日期：{filters.endDate}
                  </span>
                )}
                {filters.minAmount && (
                  <span className="bg-blue-100 px-2 py-1 rounded">
                    最小金额：¥{filters.minAmount}
                  </span>
                )}
                {filters.maxAmount && (
                  <span className="bg-blue-100 px-2 py-1 rounded">
                    最大金额：¥{filters.maxAmount}
                  </span>
                )}
              </div>
              <button
                onClick={handleResetFilters}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                清除所有筛选
              </button>
            </div>
          </div>
        )}

        {/* 采购订单表格 */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">加载中...</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">订单编号</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">供应商</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">商品名称</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">规格参数</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数量</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">单价</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">小计</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">订单日期</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {purchaseOrders.length > 0 ? (
                      purchaseOrders.flatMap((order) => 
                        order.items && order.items.length > 0 
                          ? order.items.map((item, index) => (
                              <tr key={`${order.uuid}-${item.uuid}`} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {order.orderNumber}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {order.supplierName || '未知供应商'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {item.productName || '未知商品'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {item.selectedSpecification || item.modelName || '无规格参数'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {item.quantity}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  ¥{item.unitPrice?.toFixed(2)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  ¥{item.totalPrice?.toFixed(2)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {formatDate(order.orderDate)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                  <div className="flex items-center gap-2">
                                    <button
                                      onClick={() => navigate(`/purchase-orders/${order.uuid}`)}
                                      className="text-blue-600 hover:text-blue-900"
                                    >
                                      <Eye size={16} />
                                    </button>
                                    <button
                                      onClick={() => handleEditOrder(order)}
                                      className="text-green-600 hover:text-green-900"
                                    >
                                      <Edit size={16} />
                                    </button>
                                    <button
                                      onClick={() => handleDelete(order.uuid)}
                                      className="text-red-600 hover:text-red-900"
                                    >
                                      <Trash2 size={16} />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))
                          : [
                              <tr key={order.uuid} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {order.orderNumber}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {order.supplierName || '未知供应商'}
                                </td>
                                <td colSpan={5} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                                  暂无订单明细
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {formatDate(order.orderDate)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                  <div className="flex items-center gap-2">
                                    <button
                                      onClick={() => navigate(`/purchase-orders/${order.uuid}`)}
                                      className="text-blue-600 hover:text-blue-900"
                                    >
                                      <Eye size={16} />
                                    </button>
                                    <button
                                      onClick={() => handleEditOrder(order)}
                                      className="text-green-600 hover:text-green-900"
                                    >
                                      <Edit size={16} />
                                    </button>
                                    <button
                                      onClick={() => handleDelete(order.uuid)}
                                      className="text-red-600 hover:text-red-900"
                                    >
                                      <Trash2 size={16} />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ]
                      )
                    ) : (
                      <tr>
                        <td colSpan={9} className="px-6 py-8 text-center text-gray-500">
                          暂无采购订单数据
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* 分页 */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    显示第 {((currentPage - 1) * pageSize) + 1} 到 {Math.min(currentPage * pageSize, total)} 条，共 {total} 条记录
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      上一页
                    </button>
                    <span className="px-3 py-1 text-sm">第 {currentPage} 页</span>
                    <button
                      onClick={() => setCurrentPage(prev => prev + 1)}
                      disabled={currentPage * pageSize >= total}
                      className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      下一页
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* 采购订单表单 */}
        {showForm && (
          <PurchaseOrderForm
            purchaseOrder={editingOrder}
            onClose={() => {
              setShowForm(false);
              setEditingOrder(null);
            }}
            onSubmit={async (data) => {
              try {
                if (editingOrder) {
                  // 编辑模式
                  await apiClient.updatePurchaseOrder(editingOrder.uuid, data);
                } else {
                  // 创建模式
                  await apiClient.createPurchaseOrder(data);
                }
                setShowForm(false);
                setEditingOrder(null);
                fetchPurchaseOrders();
              } catch (error) {
                console.error('保存采购订单失败:', error);
                alert('保存失败，请重试');
              }
            }}
            mode={editingOrder ? 'edit' : 'create'}
          />
        )}
      </div>
    </div>
  );
};

export default PurchaseOrderPage;