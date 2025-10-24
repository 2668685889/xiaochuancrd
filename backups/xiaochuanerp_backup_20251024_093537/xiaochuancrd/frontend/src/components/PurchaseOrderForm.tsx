import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { apiClient } from '../services/api/client';
import type { 
  PurchaseOrder, 
  CreatePurchaseOrderRequest, 
  UpdatePurchaseOrderRequest,
  PurchaseOrderItem,
  CreatePurchaseOrderItemRequest
} from '../types/purchaseOrder';
import type { Supplier, Product, ProductModel, ProductSpecification } from '../types';

interface PurchaseOrderFormProps {
  purchaseOrder?: PurchaseOrder;
  onSubmit: (data: CreatePurchaseOrderRequest | UpdatePurchaseOrderRequest) => void;
  onClose: () => void;
  mode: 'create' | 'edit';
}

const PurchaseOrderForm: React.FC<PurchaseOrderFormProps> = ({
  purchaseOrder,
  onSubmit,
  onClose,
  mode
}) => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [productModels, setProductModels] = useState<ProductModel[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    supplierUuid: purchaseOrder?.supplierUuid || '',
    orderDate: purchaseOrder?.orderDate ? new Date(purchaseOrder.orderDate).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
    expectedDate: purchaseOrder?.expectedDeliveryDate ? new Date(purchaseOrder.expectedDeliveryDate).toISOString().split('T')[0] : '',
    remark: purchaseOrder?.remark || ''
  });

  const [items, setItems] = useState<CreatePurchaseOrderItemRequest[]>(
    purchaseOrder?.items?.map((item: PurchaseOrderItem) => ({
      productUuid: item.productUuid,
      modelUuid: item.modelUuid || '',
      selectedSpecification: item.selectedSpecification || '',
      quantity: item.quantity,
      unitPrice: item.unitPrice
    })) || []
  );

  // 监听purchaseOrder变化，更新表单数据
  useEffect(() => {
    console.log('purchaseOrder变化:', purchaseOrder);
    
    if (purchaseOrder && mode === 'edit') {
      // 更新表单数据
      setFormData({
        supplierUuid: purchaseOrder.supplierUuid || '',
        orderDate: purchaseOrder.orderDate ? new Date(purchaseOrder.orderDate).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
        expectedDate: purchaseOrder.expectedDeliveryDate ? new Date(purchaseOrder.expectedDeliveryDate).toISOString().split('T')[0] : '',
        remark: purchaseOrder.remark || ''
      });
      
      // 更新商品明细
      setItems(
        purchaseOrder.items?.map((item: PurchaseOrderItem) => ({
          productUuid: item.productUuid,
          modelUuid: item.modelUuid || '',
          selectedSpecification: item.selectedSpecification || '',
          quantity: item.quantity,
          unitPrice: item.unitPrice
        })) || []
      );
    }
  }, [purchaseOrder, mode]);

  // 加载供应商、产品和产品型号列表
  useEffect(() => {
    const loadData = async () => {
      try {
        console.log('开始加载数据...');
        const [suppliersResponse, productsResponse, productModelsResponse] = await Promise.all([
          apiClient.getSuppliers(),
          apiClient.getProducts({ pageSize: 1000 }),
          apiClient.getProductModels({ pageSize: 1000 })
        ]);
        
        console.log('供应商数据:', suppliersResponse.items);
        console.log('产品数据:', productsResponse.items);
        console.log('产品型号数据:', productModelsResponse.items);
        
        setSuppliers(suppliersResponse.items || []);
        setProducts(productsResponse.items || []);
        setProductModels(productModelsResponse.items || []);
        
        console.log('数据加载完成');
      } catch (error) {
        console.error('加载数据失败:', error);
      }
    };

    loadData();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.supplierUuid) {
      alert('请选择供应商');
      return;
    }

    if (items.length === 0) {
      alert('请至少添加一个产品');
      return;
    }

    // 处理items中的modelUuid和selectedSpecification字段，将空字符串转换为null
    const processedItems = items.map(item => ({
      ...item,
      modelUuid: item.modelUuid === '' ? null : item.modelUuid,
      selectedSpecification: item.selectedSpecification === '' ? null : item.selectedSpecification
    }));

    // 处理日期格式和字段名映射
    const submitData = {
      supplierUuid: formData.supplierUuid,
      orderDate: formData.orderDate ? `${formData.orderDate}T00:00:00` : null,
      expectedDeliveryDate: formData.expectedDate ? `${formData.expectedDate}T00:00:00` : null,
      remark: formData.remark,
      items: processedItems
    };

    onSubmit(submitData);
  };

  const addItem = () => {
    setItems([...items, { productUuid: '', modelUuid: '', selectedSpecification: '', quantity: 1, unitPrice: 0 }]);
  };

  const removeItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const updateItem = (index: number, field: keyof CreatePurchaseOrderItemRequest, value: any) => {
    console.log('updateItem调用:', { index, field, value });
    
    // 确保索引有效
    if (index < 0 || index >= items.length) {
      console.error('无效的索引:', index, 'items长度:', items.length);
      return;
    }
    
    // 使用函数式更新确保获取最新状态
    setItems(prevItems => {
      const newItems = [...prevItems];
      newItems[index] = { ...newItems[index], [field]: value };
      console.log('更新后的newItems:', newItems);
      return newItems;
    });
  };

  const getProductName = (productUuid: string) => {
    const product = products.find(p => p.uuid === productUuid);
    return product ? `${product.productName} (${product.productCode})` : '选择产品';
  };

  // 获取产品可选的型号列表
  const getAvailableProductModels = (productUuid: string) => {
    if (!productUuid) {
      return [];
    }
    
    // 根据选择的产品筛选对应的型号
    // 产品和型号通过产品分类进行关联
    const selectedProduct = products.find(p => p.uuid === productUuid);
    if (!selectedProduct) {
      return [];
    }
    
    // 如果产品有分类，筛选属于该分类的型号
    if (selectedProduct.categoryUuid) {
      const availableModels = productModels.filter(model => 
        model.isActive && model.categoryUuid === selectedProduct.categoryUuid
      );
      return availableModels;
    }
    
    // 如果没有分类，返回所有活跃型号
    return productModels.filter(model => model.isActive);
  };

  const calculateItemTotal = (item: CreatePurchaseOrderItemRequest) => {
    return (item.quantity || 0) * (item.unitPrice || 0);
  };

  const calculateTotalAmount = () => {
    return items.reduce((total: number, item: CreatePurchaseOrderItemRequest) => total + calculateItemTotal(item), 0);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              {mode === 'create' ? '新建采购订单' : '编辑采购订单'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 基本信息 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  供应商 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.supplierUuid}
                  onChange={(e) => setFormData({ ...formData, supplierUuid: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">选择供应商</option>
                  {suppliers.map(supplier => (
                    <option key={supplier.uuid} value={supplier.uuid}>
                      {supplier.supplierName} ({supplier.supplierCode})
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
                  value={formData.orderDate}
                  onChange={(e) => setFormData({ ...formData, orderDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  预计到货日期
                </label>
                <input
                  type="date"
                  value={formData.expectedDate}
                  onChange={(e) => setFormData({ ...formData, expectedDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  订单总金额
                </label>
                <input
                  type="text"
                  value={`¥${calculateTotalAmount().toFixed(2)}`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  readOnly
                />
              </div>
            </div>

            {/* 订单明细 */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <label className="block text-sm font-medium text-gray-700">
                  订单明细 <span className="text-red-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={addItem}
                  className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                >
                  <Plus className="w-4 h-4" />
                  <span>添加产品</span>
                </button>
              </div>

              {items.length === 0 ? (
                <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
                  暂无产品明细，请点击"添加产品"按钮添加
                </div>
              ) : (
                <div className="space-y-3">
                  {items.map((item, index) => {
                    const product = products.find(p => p.uuid === item.productUuid);
                    const availableModels = getAvailableProductModels(item.productUuid);
                    
                    return (
                      <div key={index} className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg">
                        {/* 产品选择 */}
                        <div className="flex-1 min-w-0">
                          <label className="block text-xs text-gray-500 mb-1">产品选择</label>
                          <select
                            value={item.productUuid}
                            onChange={(e) => updateItem(index, 'productUuid', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                          >
                            <option value="">选择产品</option>
                            {products.map(product => (
                              <option key={product.uuid} value={product.uuid}>
                                {product.productName} ({product.productCode}) - ¥{product.unitPrice}
                              </option>
                            ))}
                          </select>
                        </div>
                        
                        {/* 产品型号选择 */}
                        <div className="flex-1 min-w-0">
                          <label className="block text-xs text-gray-500 mb-1">产品型号</label>
                          <select
                            value={item.modelUuid || ''}
                            onChange={(e) => {
                              console.log('选择型号事件触发:', e.target.value);
                              console.log('当前item:', item);
                              console.log('当前index:', index);
                              
                              // 更新型号UUID
                              updateItem(index, 'modelUuid', e.target.value);
                              
                              // 清空已选择的规格参数
                              updateItem(index, 'selectedSpecification', '');
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">选择型号（可选）</option>
                            {availableModels.map(model => (
                              <option key={model.uuid} value={model.uuid}>
                                {model.modelName}
                              </option>
                            ))}
                          </select>
                        </div>
                        
                        {/* 规格参数选择 */}
                        <div className="flex-1 min-w-0">
                          <label className="block text-xs text-gray-500 mb-1">规格参数</label>
                          {item.modelUuid ? (
                            <select
                              value={item.selectedSpecification || ''}
                              onChange={(e) => updateItem(index, 'selectedSpecification', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="">选择规格参数</option>
                              {(() => {
                                const selectedModel = productModels.find(m => m.uuid === item.modelUuid);
                                
                                if (selectedModel && selectedModel.specifications && selectedModel.specifications.length > 0) {
                                  return selectedModel.specifications.map((spec, idx) => {
                                    // 创建完整的规格参数字符串
                                    const specString = `${spec.key}:${spec.value}${spec.unit ? spec.unit : ''}`;
                                    return (
                                      <option key={idx} value={specString}>
                                        {spec.key}: {spec.value}{spec.unit ? spec.unit : ''}
                                      </option>
                                    );
                                  });
                                }
                                
                                return null;
                              })()}
                            </select>
                          ) : (
                            <div>
                              <input
                                type="text"
                                value={item.selectedSpecification || ''}
                                onChange={(e) => updateItem(index, 'selectedSpecification', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="输入规格参数"
                              />
                              <div className="text-xs text-gray-500 mt-1">
                                💡 提示：请先选择产品型号，规格参数下拉框才会显示
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {/* 数量 */}
                        <div className="w-32">
                          <label className="block text-xs text-gray-500 mb-1">数量</label>
                          <input
                            type="number"
                            min="1"
                            value={item.quantity}
                            onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                          />
                        </div>
                        
                        {/* 单价 */}
                        <div className="w-32">
                          <label className="block text-xs text-gray-500 mb-1">单价</label>
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={item.unitPrice}
                            onChange={(e) => updateItem(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                          />
                        </div>
                        
                        {/* 小计 */}
                        <div className="w-32">
                          <label className="block text-xs text-gray-500 mb-1">小计</label>
                          <input
                            type="text"
                            value={`¥${calculateItemTotal(item).toFixed(2)}`}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                            readOnly
                          />
                        </div>
                        
                        {/* 删除按钮 */}
                        <div className="flex items-end h-9">
                          <button
                            type="button"
                            onClick={() => removeItem(index)}
                            className="p-2 text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 备注 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                备注
              </label>
              <textarea
                value={formData.remark}
                onChange={(e) => setFormData({ ...formData, remark: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入订单备注信息..."
              />
            </div>

            {/* 操作按钮 */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {mode === 'create' ? '创建订单' : '更新订单'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PurchaseOrderForm;