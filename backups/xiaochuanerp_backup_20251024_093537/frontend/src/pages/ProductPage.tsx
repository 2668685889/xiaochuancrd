import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Package } from 'lucide-react';
import { apiClient } from '../services/api/client';
import type { Product, CreateProductRequest, Supplier, ProductModel } from '../types';

const ProductPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [productModels, setProductModels] = useState<ProductModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // 加载产品列表
  useEffect(() => {
    loadProducts();
    loadSuppliers();
    loadProductModels();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getProducts({ search: searchTerm || undefined });
      // 确保response存在且有items字段
      if (response && response.items) {
        setProducts(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setProducts([]);
      }
    } catch (error) {
      console.error('加载产品失败:', error);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSuppliers = async () => {
    try {
      const response = await apiClient.getSuppliers();
      // 确保response存在且有items字段
      if (response && response.items) {
        setSuppliers(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setSuppliers([]);
      }
    } catch (error) {
      console.error('加载供应商列表失败:', error);
      setSuppliers([]);
    }
  };

  const loadProductModels = async () => {
    try {
      const response = await apiClient.getProductModels();
      // 确保response存在且有items字段
      if (response && response.items) {
        setProductModels(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setProductModels([]);
      }
    } catch (error) {
      console.error('加载产品型号列表失败:', error);
      setProductModels([]);
    }
  };

  const handleCreateProduct = async (productData: CreateProductRequest) => {
    try {
      await apiClient.createProduct(productData);
      setShowCreateModal(false);
      loadProducts();
    } catch (error: any) {
      console.error('创建产品失败:', error);
      
      // 提取错误信息并显示给用户
      let errorMessage = '创建产品失败，请稍后重试';
      
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(`创建产品失败: ${errorMessage}`);
    }
  };

  const handleDeleteProduct = async (uuid: string) => {
    if (window.confirm('确定要删除这个产品吗？')) {
      try {
        await apiClient.deleteProduct(uuid);
        loadProducts();
      } catch (error: any) {
        console.error('删除产品失败:', error);
        
        // 提取错误信息并显示给用户
        let errorMessage = '删除产品失败，请稍后重试';
        
        if (error.response?.data?.message) {
          errorMessage = error.response.data.message;
        } else if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        alert(`删除产品失败: ${errorMessage}`);
      }
    }
  };

  const filteredProducts = products.filter(product =>
    product.productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.productCode.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 页面标题和操作栏 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">产品管理</h1>
          <p className="text-gray-600 mt-1">管理您的产品目录和库存信息</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>新增产品</span>
        </button>
      </div>

      {/* 搜索栏 */}
      <div className="flex items-center space-x-4">
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
        <button onClick={loadProducts} className="btn-secondary">
          刷新
        </button>
      </div>

      {/* 产品列表 */}
      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="table-header">
                  <th className="table-cell text-left">产品信息</th>
                  <th className="table-cell text-left">编码</th>
                  <th className="table-cell text-left">单价</th>
                  <th className="table-cell text-left">库存数量</th>
                  <th className="table-cell text-left">库存范围</th>
                  <th className="table-cell text-left">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.uuid} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                          <Package className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{product.productName}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(product.createdAt).toLocaleDateString('zh-CN')}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="table-cell">
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm">{product.productCode}</code>
                    </td>
                    <td className="table-cell font-medium text-gray-900">
                      ¥{product.unitPrice.toFixed(2)}
                    </td>
                    <td className="table-cell">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        product.currentQuantity <= product.minQuantity 
                          ? 'bg-red-100 text-red-800'
                          : product.currentQuantity >= product.maxQuantity
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {product.currentQuantity}
                      </span>
                    </td>
                    <td className="table-cell text-sm text-gray-600">
                      {product.minQuantity} - {product.maxQuantity}
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setEditingProduct(product)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="编辑"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteProduct(product.uuid)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="删除"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredProducts.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>暂无产品数据</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 创建/编辑产品模态框 */}
      {showCreateModal && (
        <ProductFormModal
          onSubmit={handleCreateProduct}
          onClose={() => setShowCreateModal(false)}
        />
      )}
      
      {editingProduct && (
        <ProductFormModal
          product={editingProduct}
          onSubmit={handleCreateProduct}
          onClose={() => setEditingProduct(null)}
        />
      )}
    </div>
  );
};

// 产品表单模态框组件
interface ProductFormModalProps {
  product?: Product;
  onSubmit: (data: CreateProductRequest) => void;
  onClose: () => void;
}

// 生成产品编码：P + 9位大写英文加数字组合
const generateProductCode = (): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const prefix = 'P';
  let randomPart = '';
  for (let i = 0; i < 9; i++) {
    randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return prefix + randomPart;
};

const ProductFormModal: React.FC<ProductFormModalProps> = ({ product, onSubmit, onClose }) => {
  const [formData, setFormData] = useState<CreateProductRequest>({
    productName: product?.productName || '',
    productCode: product?.productCode || (product ? '' : generateProductCode()),
    unitPrice: product?.unitPrice || 0,
    currentQuantity: product?.currentQuantity || 0,
    minQuantity: product?.minQuantity || 0,
    maxQuantity: product?.maxQuantity || 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {product ? '编辑产品' : '新增产品'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                产品名称
              </label>
              <input
                type="text"
                required
                value={formData.productName}
                onChange={(e) => setFormData({ ...formData, productName: e.target.value })}
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                产品编码
              </label>
              <input
                type="text"
                required
                value={formData.productCode}
                onChange={(e) => setFormData({ ...formData, productCode: e.target.value })}
                readOnly={!product} // 添加商品时只读，编辑商品时可编辑
                className={`input-field ${!product ? 'bg-gray-100 cursor-not-allowed' : ''}`}
              />
              {!product && (
                <p className="text-xs text-gray-500 mt-1">系统自动生成的唯一编码</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                单价 (¥)
              </label>
              <input
                type="number"
                step="0.01"
                required
                value={formData.unitPrice}
                onChange={(e) => setFormData({ ...formData, unitPrice: parseFloat(e.target.value) })}
                className="input-field"
              />
            </div>
            

            

            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  当前库存
                </label>
                <input
                  type="number"
                  required
                  value={formData.currentQuantity}
                  onChange={(e) => setFormData({ ...formData, currentQuantity: parseInt(e.target.value) })}
                  readOnly={true} // 当前库存不可编辑
                  className="input-field bg-gray-100 cursor-not-allowed"
                />
                <p className="text-xs text-gray-500 mt-1">通过入库/出库操作自动更新</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最低库存
                </label>
                <input
                  type="number"
                  required
                  value={formData.minQuantity}
                  onChange={(e) => setFormData({ ...formData, minQuantity: parseInt(e.target.value) })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最高库存
                </label>
                <input
                  type="number"
                  required
                  value={formData.maxQuantity}
                  onChange={(e) => setFormData({ ...formData, maxQuantity: parseInt(e.target.value) })}
                  className="input-field"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={onClose} className="btn-secondary">
                取消
              </button>
              <button type="submit" className="btn-primary">
                {product ? '更新' : '创建'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;