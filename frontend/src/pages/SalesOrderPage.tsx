import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Eye, ChevronDown } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { apiClient } from '../services/api/client';
import { SalesOrder } from '../types/salesOrder';
import SalesOrderForm from '../components/SalesOrderForm';

const SalesOrderPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [salesOrders, setSalesOrders] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingOrder, setEditingOrder] = useState<SalesOrder | null>(null);
  const [expandedOrders, setExpandedOrders] = useState<Set<string>>(new Set());
  const pageSize = 20;

  const fetchSalesOrders = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getSalesOrders({ 
        page: currentPage, 
        size: pageSize, 
        search: searchTerm || undefined 
      });
      // 确保response存在且有items字段
      if (response && response.items) {
        setSalesOrders(response.items);
        setTotal(response.total);
      } else {
        console.error('API返回数据格式错误:', response);
        setSalesOrders([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('获取销售订单列表失败:', error);
      setSalesOrders([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSalesOrders();
    
    // 检查是否有从详情页面传递过来的编辑订单
    if (location.state?.editOrder) {
      setEditingOrder(location.state.editOrder);
      setShowForm(true);
      // 清除状态，避免重复触发
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [currentPage, searchTerm, location.state]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchSalesOrders();
  };

  const handleDelete = async (uuid: string) => {
    if (window.confirm('确定要删除这个销售订单吗？')) {
      try {
        await apiClient.deleteSalesOrder(uuid);
        fetchSalesOrders();
      } catch (error) {
        console.error('删除销售订单失败:', error);
      }
    }
  };

  const handleViewOrder = (uuid: string) => {
    navigate(`/sales-orders/${uuid}`);
  };

  const handleEditOrder = async (order: SalesOrder) => {
    try {
      // 从API获取最新的订单数据，包括商品明细和时间信息
      const latestOrder = await apiClient.getSalesOrder(order.uuid);
      setEditingOrder(latestOrder);
      setShowForm(true);
    } catch (error) {
      console.error('获取销售订单详情失败:', error);
      // 如果获取失败，使用当前页面数据作为备选方案
      setEditingOrder(order);
      setShowForm(true);
    }
  };

  const handleCreateOrder = () => {
    setEditingOrder(null);
    setShowForm(true);
  };

  const toggleOrderExpansion = (orderUuid: string) => {
    setExpandedOrders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(orderUuid)) {
        newSet.delete(orderUuid);
      } else {
        newSet.add(orderUuid);
      }
      return newSet;
    });
  };

  // 计算订单总金额
  const calculateOrderTotal = (order: SalesOrder) => {
    if (!order.items || order.items.length === 0) {
      return 0;
    }
    
    // 根据商品明细计算总金额
    return order.items.reduce((total, item) => {
      return total + (item.unitPrice * item.quantity);
    }, 0);
  };

  const handleSubmitOrder = async (data: any) => {
    try {
      if (editingOrder) {
        // 编辑模式
        await apiClient.updateSalesOrder(editingOrder.uuid, data);
      } else {
        // 创建模式
        await apiClient.createSalesOrder(data);
      }
      setShowForm(false);
      setEditingOrder(null);
      fetchSalesOrders();
    } catch (error) {
      console.error('保存销售订单失败:', error);
      alert('保存失败，请重试');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'pending': { color: 'bg-yellow-100 text-yellow-800', label: '待审核' },
      'approved': { color: 'bg-green-100 text-green-800', label: '已审核' },
      'shipped': { color: 'bg-blue-100 text-blue-800', label: '已发货' },
      'completed': { color: 'bg-purple-100 text-purple-800', label: '已完成' },
      'cancelled': { color: 'bg-red-100 text-red-800', label: '已取消' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || { color: 'bg-gray-100 text-gray-800', label: status };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>{config.label}</span>;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">销售订单管理</h1>
        <p className="text-gray-600">管理销售订单信息</p>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <form onSubmit={handleSearch} className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="搜索销售订单..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                搜索
              </button>
            </form>
            <button 
              onClick={handleCreateOrder}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>新建销售订单</span>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">订单编号</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">客户</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-48">商品名称</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">数量</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">单价</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">商品总价</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">订单金额</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">创建时间</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-28">操作</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={10} className="px-6 py-4 text-center">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                    </div>
                  </td>
                </tr>
              ) : salesOrders.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-6 py-4 text-center text-gray-500">
                    暂无销售订单数据
                  </td>
                </tr>
              ) : (
                salesOrders.flatMap((order) => {
                  // 如果订单没有商品，显示一行空商品信息
                  if (!order.items || order.items.length === 0) {
                    return (
                    <tr key={order.uuid} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 w-32">
                        {order.orderNumber}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-40">
                        {order.customerName}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-48">-</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-20">-</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-24">-</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-24">-</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 w-24">
                        ¥{calculateOrderTotal(order).toFixed(2)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-32">
                        {new Date(order.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-28">
                        <div className="flex space-x-2">
                          <button 
                            onClick={() => handleViewOrder(order.uuid)}
                            className="text-blue-600 hover:text-blue-900"
                            title="查看详情"
                          >
                            <Eye size={16} />
                          </button>
                          <button 
                            onClick={() => handleEditOrder(order)}
                            className="text-green-600 hover:text-green-900"
                            title="编辑订单"
                          >
                            <Edit size={16} />
                          </button>
                          <button 
                            onClick={() => handleDelete(order.uuid)}
                            className="text-red-600 hover:text-red-900"
                            title="删除订单"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                  }
                  
                  // 为每个商品创建一行
                  return order.items.map((item, index) => (
                    <tr key={`${order.uuid}-${index}`} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 w-32">
                        {index === 0 ? order.orderNumber : ''}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-40">
                        {index === 0 ? order.customerName : ''}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 w-48">
                        {item.productName}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-20">
                        {item.quantity}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 w-24">
                        ¥{item.unitPrice?.toFixed(2)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 w-24">
                        ¥{item.totalPrice?.toFixed(2)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 w-24">
                        {index === 0 ? `¥${calculateOrderTotal(order).toFixed(2)}` : ''}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-32">
                        {index === 0 ? new Date(order.createdAt).toLocaleDateString() : ''}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 w-28">
                        {index === 0 ? (
                          <div className="flex space-x-2">
                            <button 
                              onClick={() => handleViewOrder(order.uuid)}
                              className="text-blue-600 hover:text-blue-900"
                              title="查看详情"
                            >
                              <Eye size={16} />
                            </button>
                            <button 
                              onClick={() => handleEditOrder(order)}
                              className="text-green-600 hover:text-green-900"
                              title="编辑订单"
                            >
                              <Edit size={16} />
                            </button>
                            <button 
                              onClick={() => handleDelete(order.uuid)}
                              className="text-red-600 hover:text-red-900"
                              title="删除订单"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        ) : ''}
                      </td>
                    </tr>
                  ));
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="px-6 py-4 border-t bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-700">
              显示第 {((currentPage - 1) * pageSize) + 1} 到 {Math.min(currentPage * pageSize, total)} 条，共 {total} 条记录
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
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
      </div>

      {/* 销售订单表单 */}
      {showForm && (
        <SalesOrderForm
          order={editingOrder}
          onSubmit={handleSubmitOrder}
          onCancel={() => {
            setShowForm(false);
            setEditingOrder(null);
          }}
        />
      )}
    </div>
  );
};

export default SalesOrderPage;