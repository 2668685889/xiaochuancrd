import React, { useState, useEffect } from 'react';
import { X, Plus, Minus } from 'lucide-react';
import { apiClient } from '../services/api/client';
import { SalesOrder, CreateSalesOrderRequest, UpdateSalesOrderRequest, SalesOrderItem } from '../types/salesOrder';
import { Customer } from '../types';
import { Product } from '../types';

interface SalesOrderFormProps {
  order?: SalesOrder | null;
  onCancel: () => void;
  onSubmit: (data: CreateSalesOrderRequest | UpdateSalesOrderRequest) => void;
}

interface FormItem {
  productUuid: string;
  productName: string;
  productCode: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

const SalesOrderForm: React.FC<SalesOrderFormProps> = ({
  order,
  onSubmit,
  onCancel
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    customerUuid: order?.customerUuid || '',
    orderDate: order?.orderDate ? new Date(order.orderDate).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
    deliveryDate: order?.deliveryDate ? new Date(order.deliveryDate).toISOString().split('T')[0] : '',
    shippingAddress: order?.shippingAddress || '',
    notes: order?.notes || '',
  });

  const [items, setItems] = useState<FormItem[]>([]);

  useEffect(() => {
    fetchCustomers();
    fetchProducts();
    if (order) {
      fetchSalesOrderItems();
    }
  }, [order]);

  const fetchCustomers = async () => {
    try {
      const response = await apiClient.getCustomers(); // 使用正确的客户API
      setCustomers(response.items || []);
    } catch (error) {
      console.error('获取客户列表失败:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await apiClient.getProducts();
      setProducts(response.items || []);
    } catch (error) {
      console.error('获取产品列表失败:', error);
    }
  };

  const fetchSalesOrderItems = async () => {
    if (!order) return;
    
    try {
      // 从API获取销售订单的完整数据，包括订单明细
      const salesOrderData = await apiClient.getSalesOrder(order.uuid);
      
      if (salesOrderData) {
        // 更新表单数据，包括收货地址等信息
        setFormData({
          customerUuid: salesOrderData.customerUuid || order.customerUuid || '',
          orderDate: salesOrderData.orderDate ? new Date(salesOrderData.orderDate).toISOString().split('T')[0] : (order.orderDate ? new Date(order.orderDate).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]),
          deliveryDate: salesOrderData.deliveryDate ? new Date(salesOrderData.deliveryDate).toISOString().split('T')[0] : (order.deliveryDate ? new Date(order.deliveryDate).toISOString().split('T')[0] : ''),
          shippingAddress: salesOrderData.shippingAddress || order.shippingAddress || '',
          notes: salesOrderData.notes || order.notes || ''
        });
        
        if (salesOrderData.items) {
          // 将订单明细转换为表单需要的格式
          const orderItems: FormItem[] = salesOrderData.items.map(item => ({
            productUuid: item.productUuid,
            productName: item.productName || '',
            productCode: item.productCode || '',
            quantity: item.quantity,
            unitPrice: item.unitPrice,
            totalPrice: item.quantity * item.unitPrice
          }));
          setItems(orderItems);
        } else {
          // 如果没有订单明细，设置为空数组
          setItems([]);
        }
      }
    } catch (error) {
      console.error('获取销售订单明细失败:', error);
      // 如果API调用失败，使用当前订单的数据
      setFormData({
        customerUuid: order.customerUuid || '',
        orderDate: order.orderDate ? new Date(order.orderDate).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
        deliveryDate: order.deliveryDate ? new Date(order.deliveryDate).toISOString().split('T')[0] : '',
        shippingAddress: order.shippingAddress || '',
        notes: order.notes || ''
      });
      
      // 如果API调用失败，使用当前订单的items数据（如果有）
      if (order.items && order.items.length > 0) {
        const orderItems: FormItem[] = order.items.map(item => ({
          productUuid: item.productUuid,
          productName: item.productName || '',
          productCode: item.productCode || '',
          quantity: item.quantity,
          unitPrice: item.unitPrice,
          totalPrice: item.quantity * item.unitPrice
        }));
        setItems(orderItems);
      } else {
        setItems([]);
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddItem = () => {
    setItems(prev => [
      ...prev,
      {
        productUuid: '',
        productName: '',
        productCode: '',
        quantity: 1,
        unitPrice: 0,
        totalPrice: 0
      }
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setItems(prev => prev.filter((_, i) => i !== index));
  };

  const handleItemChange = (index: number, field: keyof FormItem, value: any) => {
    setItems(prev => {
      const newItems = [...prev];
      const item = { ...newItems[index] };
      
      if (field === 'productUuid') {
        const selectedProduct = products.find(p => p.uuid === value);
        if (selectedProduct) {
          item.productUuid = value;
          item.productName = selectedProduct.productName;
          item.productCode = selectedProduct.productCode;
          item.unitPrice = selectedProduct.unitPrice || 0;
        }
      } else if (field === 'quantity' || field === 'unitPrice') {
        item[field] = Number(value);
      } else if (field === 'productName' || field === 'productCode') {
        item[field] = value;
      }
      
      // 计算小计
      item.totalPrice = item.quantity * item.unitPrice;
      
      newItems[index] = item;
      return newItems;
    });
  };

  const calculateTotalAmount = () => {
    return items.reduce((total, item) => total + item.totalPrice, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.customerUuid) {
      alert('请选择客户');
      return;
    }

    if (items.length === 0) {
      alert('请至少添加一个产品');
      return;
    }

    setLoading(true);
    
    try {
      const submitData = {
        ...formData,
        items: items.map(item => ({
          productUuid: item.productUuid,
          quantity: item.quantity,
          unitPrice: item.unitPrice
        }))
      };
      
      onSubmit(submitData);
    } catch (error) {
      console.error('提交销售订单失败:', error);
      alert('提交失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {order ? '编辑销售订单' : '新建销售订单'}
          </h2>
          <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                客户 <span className="text-red-500">*</span>
              </label>
              <select
                name="customerUuid"
                value={formData.customerUuid}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">请选择客户</option>
                {customers.map(customer => (
                  <option key={customer.uuid} value={customer.uuid}>
                    {customer.customerName}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                订单日期 <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="orderDate"
                value={formData.orderDate}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                预计交货日期
              </label>
              <input
                type="date"
                name="deliveryDate"
                value={formData.deliveryDate}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                收货地址
              </label>
              <input
                type="text"
                name="shippingAddress"
                value={formData.shippingAddress}
                onChange={handleInputChange}
                placeholder="请输入收货地址"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              备注
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              placeholder="请输入订单备注"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* 订单明细 */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">订单明细</h3>
              <button
                type="button"
                onClick={handleAddItem}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>添加产品</span>
              </button>
            </div>

            {items.length === 0 ? (
              <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
                暂无订单明细，请点击"添加产品"按钮添加
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">产品</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数量</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">单价</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">小计</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {items.map((item, index) => (
                      <tr key={index}>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <select
                            value={item.productUuid}
                            onChange={(e) => handleItemChange(index, 'productUuid', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            required
                          >
                            <option value="">选择产品</option>
                            {products.map(product => (
                              <option key={product.uuid} value={product.uuid}>
                                {product.productName} ({product.productCode})
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <input
                            type="number"
                            min="1"
                            value={item.quantity}
                            onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                            className="w-20 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            required
                          />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={item.unitPrice}
                            onChange={(e) => handleItemChange(index, 'unitPrice', e.target.value)}
                            className="w-24 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            required
                          />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                          ¥{item.totalPrice.toFixed(2)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <button
                            type="button"
                            onClick={() => handleRemoveItem(index)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Minus className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* 订单总金额 */}
          <div className="flex justify-end mb-6">
            <div className="text-lg font-semibold text-gray-900">
              订单总金额: <span className="text-blue-600">¥{calculateTotalAmount().toFixed(2)}</span>
            </div>
          </div>

          <div className="flex justify-end space-x-4 pt-4 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '保存中...' : order ? '更新订单' : '创建订单'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SalesOrderForm;