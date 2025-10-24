import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, Download, Edit } from 'lucide-react';
import { apiClient } from '../services/api/client';
import { SalesOrder } from '../types/salesOrder';

const SalesOrderDetailPage: React.FC = () => {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const [salesOrder, setSalesOrder] = useState<SalesOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (uuid) {
      fetchSalesOrder(uuid);
    }
  }, [uuid]);

  const fetchSalesOrder = async (orderUuid: string) => {
    try {
      setLoading(true);
      const order = await apiClient.getSalesOrder(orderUuid);
      setSalesOrder(order);
    } catch (err) {
      console.error('获取销售订单详情失败:', err);
      setError('获取订单详情失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    // 导出功能实现
    alert('导出功能开发中');
  };

  const handleEdit = () => {
    if (salesOrder) {
      navigate('/sales-orders', { state: { editOrder: salesOrder } });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">加载失败</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/sales-orders')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回销售订单列表
          </button>
        </div>
      </div>
    );
  }

  if (!salesOrder) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">销售订单不存在</h2>
          <button
            onClick={() => navigate('/sales-orders')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回销售订单列表
          </button>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'pending': { color: 'bg-yellow-100 text-yellow-800', label: '待审核' },
      'approved': { color: 'bg-green-100 text-green-800', label: '已审核' },
      'shipped': { color: 'bg-blue-100 text-blue-800', label: '已发货' },
      'completed': { color: 'bg-purple-100 text-purple-800', label: '已完成' },
      'cancelled': { color: 'bg-red-100 text-red-800', label: '已取消' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || { color: 'bg-gray-100 text-gray-800', label: status };
    return <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>{config.label}</span>;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* 页面头部 */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/sales-orders')}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            返回销售订单列表
          </button>
          
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">销售订单详情</h1>
              <p className="text-gray-600">订单编号: {salesOrder.orderNumber}</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handleEdit}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Edit className="w-4 h-4 mr-2" />
                编辑订单
              </button>
              <button
                onClick={handlePrint}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Printer className="w-4 h-4 mr-2" />
                打印
              </button>
              <button
                onClick={handleExport}
                className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                <Download className="w-4 h-4 mr-2" />
                导出
              </button>
            </div>
          </div>
        </div>

        {/* 订单基本信息 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">订单信息</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">订单编号:</span>
                    <p className="text-gray-900">{salesOrder.orderNumber}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">订单状态:</span>
                    <div className="mt-1">{getStatusBadge(salesOrder.status)}</div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">订单日期:</span>
                    <p className="text-gray-900">{new Date(salesOrder.orderDate).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">订单金额:</span>
                    <p className="text-gray-900 font-semibold">¥{salesOrder.totalAmount?.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">客户信息</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">客户名称:</span>
                    <p className="text-gray-900">{salesOrder.customerName}</p>
                  </div>
                  {salesOrder.shippingAddress && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">收货地址:</span>
                      <p className="text-gray-900">{salesOrder.shippingAddress}</p>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">时间信息</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">创建时间:</span>
                    <p className="text-gray-900">{new Date(salesOrder.createdAt).toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">更新时间:</span>
                    <p className="text-gray-900">{new Date(salesOrder.updatedAt).toLocaleString()}</p>
                  </div>
                  {salesOrder.deliveryDate && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">预计交货日期:</span>
                      <p className="text-gray-900">{new Date(salesOrder.deliveryDate).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {salesOrder.notes && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <span className="text-sm font-medium text-gray-500">订单备注:</span>
                <p className="text-gray-900 mt-1">{salesOrder.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* 订单明细 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">订单明细</h3>
            
            {/* 这里需要显示订单明细，暂时使用占位符 */}
            <div className="text-center py-8 text-gray-500">
              <p>订单明细功能开发中</p>
              <p className="text-sm mt-2">这里将显示销售订单的产品明细信息</p>
            </div>
          </div>
        </div>

        {/* 操作历史（可选） */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">操作历史</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2">
                <div>
                  <p className="text-sm font-medium text-gray-900">订单创建</p>
                  <p className="text-xs text-gray-500">
                    {new Date(salesOrder.createdAt).toLocaleString()}
                  </p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  创建
                </span>
              </div>
              
              {salesOrder.updatedAt !== salesOrder.createdAt && (
                <div className="flex justify-between items-center py-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900">订单更新</p>
                    <p className="text-xs text-gray-500">
                      {new Date(salesOrder.updatedAt).toLocaleString()}
                    </p>
                  </div>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    更新
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesOrderDetailPage;