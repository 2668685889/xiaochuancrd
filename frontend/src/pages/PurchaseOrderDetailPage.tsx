import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, Download } from 'lucide-react';
import { apiClient } from '../services/api/client';
import type { PurchaseOrder } from '../types/purchaseOrder';

const PurchaseOrderDetailPage: React.FC = () => {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const [purchaseOrder, setPurchaseOrder] = useState<PurchaseOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (uuid) {
      fetchPurchaseOrder(uuid);
    }
  }, [uuid]);

  const fetchPurchaseOrder = async (orderUuid: string) => {
    try {
      setLoading(true);
      const data = await apiClient.getPurchaseOrder(orderUuid);
      setPurchaseOrder(data);
    } catch (err) {
      setError('获取采购订单详情失败');
      console.error('Error fetching purchase order:', err);
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
            onClick={() => navigate('/purchase-orders')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回采购订单列表
          </button>
        </div>
      </div>
    );
  }

  if (!purchaseOrder) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">采购订单不存在</h2>
          <button
            onClick={() => navigate('/purchase-orders')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回采购订单列表
          </button>
        </div>
      </div>
    );
  }

  const calculateTotalAmount = () => {
    return purchaseOrder.items?.reduce((total: number, item: PurchaseOrderItem) => total + (item.quantity * item.unitPrice), 0) || 0;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/purchase-orders')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">采购订单详情</h1>
              <p className="text-gray-600">订单编号: {purchaseOrder.orderNumber}</p>
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handlePrint}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
            >
              <Printer className="w-4 h-4" />
              <span>打印</span>
            </button>
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>导出</span>
            </button>
          </div>
        </div>

        {/* 订单信息卡片 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">供应商信息</h3>
                <p className="text-lg font-semibold text-gray-900">{purchaseOrder.supplierName}</p>
                <p className="text-gray-600">{purchaseOrder.supplierCode || 'N/A'}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">订单信息</h3>
                <div className="space-y-1">
                  <p className="text-gray-900">订单日期: {new Date(purchaseOrder.orderDate).toLocaleDateString()}</p>
                  <p className="text-gray-900">
                    预计到货: {purchaseOrder.expectedDate ? 
                      new Date(purchaseOrder.expectedDate).toLocaleDateString() : '未设置'
                    }
                  </p>
                  <p className="text-gray-900">
                    状态: <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      purchaseOrder.status === 'completed' ? 'bg-green-100 text-green-800' :
                      purchaseOrder.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {purchaseOrder.status === 'pending' ? '待处理' :
                       purchaseOrder.status === 'completed' ? '已完成' :
                       purchaseOrder.status === 'cancelled' ? '已取消' : '处理中'}
                    </span>
                  </p>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">金额信息</h3>
                <p className="text-2xl font-bold text-blue-600">¥{calculateTotalAmount().toFixed(2)}</p>
                <p className="text-gray-600">共 {purchaseOrder.items?.length || 0} 个产品</p>
              </div>
            </div>
            
            {(purchaseOrder.remark || purchaseOrder.notes) && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 mb-2">备注</h3>
                <p className="text-gray-900">{purchaseOrder.remark || purchaseOrder.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* 订单明细 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">订单明细</h3>
            
            {purchaseOrder.items && purchaseOrder.items.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">产品名称</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">产品编码</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">规格参数</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">数量</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">单价</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">小计</th>
                    </tr>
                  </thead>
                  <tbody>
                    {purchaseOrder.items.map((item, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm text-gray-900">{item.productName}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">{item.productCode}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{item.selectedSpecification || "无规格参数"}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 text-right">{item.quantity}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 text-right">¥{item.unitPrice.toFixed(2)}</td>
                        <td className="py-3 px-4 text-sm text-blue-600 font-medium text-right">
                          ¥{(item.quantity * item.unitPrice).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colSpan={5} className="py-3 px-4 text-sm font-medium text-gray-900 text-right">
                        总计:
                      </td>
                      <td className="py-3 px-4 text-lg font-bold text-blue-600 text-right">
                        ¥{calculateTotalAmount().toFixed(2)}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                暂无订单明细
              </div>
            )}
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
                    {new Date(purchaseOrder.createdAt).toLocaleString()}
                  </p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  创建
                </span>
              </div>
              
              {purchaseOrder.updatedAt !== purchaseOrder.createdAt && (
                <div className="flex justify-between items-center py-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900">订单更新</p>
                    <p className="text-xs text-gray-500">
                      {new Date(purchaseOrder.updatedAt).toLocaleString()}
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

export default PurchaseOrderDetailPage;