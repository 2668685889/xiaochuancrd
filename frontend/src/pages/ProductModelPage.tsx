import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Cpu, Filter } from 'lucide-react';
import { apiClient } from '../services/api/client';
import type { ProductModel, CreateProductModelRequest, ProductCategory } from '../types';

// 生成产品型号编码：PM + 6位大写英文加数字组合
const generateModelCode = (): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const prefix = 'PM';
  let randomPart = '';
  for (let i = 0; i < 6; i++) {
    randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return prefix + randomPart;
};

const ProductModelPage: React.FC = () => {
  const [productModels, setProductModels] = useState<ProductModel[]>([]);
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingModel, setEditingModel] = useState<ProductModel | null>(null);

  // 加载产品型号列表
  useEffect(() => {
    loadProductModels();
    loadCategories();
  }, []);

  const loadProductModels = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (searchTerm) params.search = searchTerm;
      if (categoryFilter) params.category = categoryFilter;
      
      console.log('开始加载产品型号数据...');
      const response = await apiClient.getProductModels(params);
      console.log('API响应数据:', response);
      
      // 确保response存在且有items字段
      if (response && response.items) {
        console.log('成功获取产品型号数据，数量:', response.items.length);
        setProductModels(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setProductModels([]);
      }
    } catch (error) {
      console.error('加载产品型号失败:', error);
      setProductModels([]);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await apiClient.getProductCategories();
      // 确保response存在且有items字段
      if (response && response.items) {
        setCategories(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setCategories([]);
      }
    } catch (error) {
      console.error('加载产品分类列表失败:', error);
      setCategories([]);
    }
  };

  const handleCreateModel = async (modelData: CreateProductModelRequest) => {
    try {
      await apiClient.createProductModel(modelData);
      setShowCreateModal(false);
      loadProductModels();
    } catch (error) {
      console.error('创建产品型号失败:', error);
    }
  };

  const handleUpdateModel = async (modelData: CreateProductModelRequest) => {
    if (!editingModel) return;
    
    try {
      await apiClient.updateProductModel(editingModel.uuid, modelData);
      setEditingModel(null);
      loadProductModels();
    } catch (error) {
      console.error('更新产品型号失败:', error);
    }
  };

  // 修复的删除产品型号函数 - 添加更严格的确认逻辑
  const handleDeleteModel = async (uuid: string) => {
    console.log('开始删除确认流程，型号UUID:', uuid);
    
    // 使用更明确的确认逻辑，添加超时保护
    const confirmed = window.confirm('确定要删除这个产品型号吗？删除后将无法恢复。');
    
    console.log('确认对话框结果:', confirmed);
    
    if (!confirmed) {
      console.log('用户取消了删除操作');
      return;
    }
    
    try {
      console.log('开始删除产品型号:', uuid);
      await apiClient.deleteProductModel(uuid);
      console.log('产品型号删除成功');
      loadProductModels();
    } catch (error) {
      console.error('删除产品型号失败:', error);
    }
  };

  // 修复的删除按钮点击处理函数
  const handleDeleteClick = (e: React.MouseEvent, uuid: string) => {
    console.log('删除按钮被点击，阻止默认行为和冒泡');
    
    // 立即阻止所有可能的事件传播
    e.preventDefault();
    e.stopPropagation();
    
    // 阻止事件冒泡到父元素
    e.nativeEvent.stopImmediatePropagation();
    
    // 使用setTimeout确保在事件循环中执行
    setTimeout(() => {
      handleDeleteModel(uuid);
    }, 0);
  };

  const filteredModels = productModels.filter(model =>
    model.modelName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    model.modelCode.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 页面标题和操作栏 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">产品型号管理</h1>
          <p className="text-gray-600 mt-1">管理您的产品型号和规格参数</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>新增型号</span>
        </button>
      </div>

      {/* 搜索和筛选栏 */}
      <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="搜索型号名称或编码..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="input-field min-w-[150px]"
            >
              <option value="">全部分类</option>
              {categories.map(category => (
                <option key={category.uuid} value={category.uuid}>
                  {category.categoryName}
                </option>
              ))}
            </select>
          </div>
          
          <button onClick={loadProductModels} className="btn-secondary">
            刷新
          </button>
        </div>
      </div>

      {/* 产品型号列表 */}
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
                  <th className="table-cell text-left">型号信息</th>
                  <th className="table-cell text-left">型号编码</th>
                  <th className="table-cell text-left">产品分类</th>
                  <th className="table-cell text-left">规格参数</th>
                  <th className="table-cell text-left">状态</th>
                  <th className="table-cell text-left">创建时间</th>
                  <th className="table-cell text-left">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredModels.map((model) => (
                  <tr key={model.uuid} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Cpu className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{model.modelName}</div>
                          <div className="text-sm text-gray-500 line-clamp-1">{model.description || '暂无描述'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="table-cell">
                      <code className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">
                        {model.modelCode}
                      </code>
                    </td>
                    <td className="table-cell">
                      {model.categoryName || '未分类'}
                    </td>
                    <td className="table-cell">
                      <div className="text-sm text-gray-600 max-w-[200px]">
                        {Array.isArray(model.specifications) && model.specifications.length > 0 ? (
                          <div className="space-y-1">
                            {model.specifications.slice(0, 3).map((spec, index) => (
                              <div key={index} className="flex items-center space-x-1">
                                <span className="font-medium text-gray-800">{spec.key}:</span>
                                <span className="text-gray-600">{spec.value}</span>
                                {spec.unit && <span className="text-gray-500 text-xs">{spec.unit}</span>}
                              </div>
                            ))}
                            {model.specifications.length > 3 && (
                              <div className="text-xs text-gray-500">
                                +{model.specifications.length - 3} 个参数
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-gray-400">无规格参数</span>
                        )}
                      </div>
                    </td>
                    <td className="table-cell">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        model.isActive 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {model.isActive ? '启用' : '禁用'}
                      </span>
                    </td>
                    <td className="table-cell">
                      <div className="text-sm text-gray-500">
                        {new Date(model.createdAt).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setEditingModel(model)}
                          className="btn-secondary btn-sm"
                        >
                          <Edit className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => handleDeleteClick(e, model.uuid)}
                          className="btn-danger btn-sm"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredModels.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                暂无产品型号数据
              </div>
            )}
          </div>
        )}
      </div>

      {/* 创建/编辑模态框 */}
      {showCreateModal && (
        <ProductModelFormModal
          categories={categories}
          onSubmit={handleCreateModel}
          onClose={() => setShowCreateModal(false)}
        />
      )}
      
      {editingModel && (
        <ProductModelFormModal
          model={editingModel}
          categories={categories}
          onSubmit={handleUpdateModel}
          onClose={() => setEditingModel(null)}
        />
      )}
    </div>
  );
};

// 产品型号表单模态框组件
interface ProductModelFormModalProps {
  model?: ProductModel;
  categories: ProductCategory[];
  onSubmit: (data: CreateProductModelRequest) => void;
  onClose: () => void;
}

const ProductModelFormModal: React.FC<ProductModelFormModalProps> = ({ 
  model, 
  categories, 
  onSubmit, 
  onClose 
}) => {
  // 将规格参数转换为数组格式（后端现在直接返回数组格式）
  const convertSpecificationsToArray = (specs: any) => {
    if (Array.isArray(specs)) {
      return specs;
    }
    if (typeof specs === 'object' && specs !== null) {
      // 如果是字典格式，转换为数组格式（兼容旧数据）
      return Object.entries(specs).map(([key, value]) => ({
        key,
        value: String(value),
        unit: ''
      }));
    }
    return [];
  };

  const [formData, setFormData] = useState<CreateProductModelRequest>({
    modelName: model?.modelName || '',
    modelCode: model?.modelCode || generateModelCode(),
    description: model?.description || '',
    categoryUuid: model?.categoryUuid || '',
    specifications: convertSpecificationsToArray(model?.specifications),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // 过滤掉空的规格参数
      const filteredSpecifications = formData.specifications.filter(spec => 
        spec.key.trim() !== '' && spec.value.trim() !== ''
      );
      
      // 直接传递数组格式给API客户端，由API客户端进行格式转换
      const submitData = {
        ...formData,
        specifications: filteredSpecifications
      };
      
      onSubmit(submitData);
    } catch (error) {
      console.error('操作失败:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {model ? '编辑产品型号' : '新增产品型号'}
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ×
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                型号名称 *
              </label>
              <input
                type="text"
                required
                value={formData.modelName}
                onChange={(e) => setFormData({...formData, modelName: e.target.value})}
                className="input-field"
                placeholder="请输入型号名称"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                型号编码 *
              </label>
              <input
                type="text"
                required
                value={formData.modelCode}
                onChange={(e) => setFormData({...formData, modelCode: e.target.value})}
                readOnly={!model}
                className={`input-field ${!model ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                placeholder="请输入型号编码"
              />
              {!model && (
                <p className="text-xs text-gray-500 mt-1">系统自动生成的唯一编码</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                型号描述
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="input-field min-h-[80px] resize-vertical"
                placeholder="请输入型号描述（可选）"
                rows={3}
              />
              <p className="text-xs text-gray-500 mt-1">
                型号的详细描述信息，如用途、特点等
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                产品分类
              </label>
              <select
                value={formData.categoryUuid}
                onChange={(e) => setFormData({...formData, categoryUuid: e.target.value})}
                className="input-field"
              >
                <option value="">选择分类</option>
                {categories.map(category => (
                  <option key={category.uuid} value={category.uuid}>
                    {category.categoryName}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                规格参数
              </label>
              <div className="space-y-2">
                {formData.specifications.map((spec, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={spec.key}
                      onChange={(e) => {
                        const newSpecs = [...formData.specifications];
                        newSpecs[index] = { ...spec, key: e.target.value };
                        setFormData({...formData, specifications: newSpecs});
                      }}
                      className="input-field flex-1"
                      placeholder="参数名称"
                    />
                    <input
                      type="text"
                      value={spec.value}
                      onChange={(e) => {
                        const newSpecs = [...formData.specifications];
                        newSpecs[index] = { ...spec, value: e.target.value };
                        setFormData({...formData, specifications: newSpecs});
                      }}
                      className="input-field flex-1"
                      placeholder="参数值"
                    />
                    <input
                      type="text"
                      value={spec.unit || ''}
                      onChange={(e) => {
                        const newSpecs = [...formData.specifications];
                        newSpecs[index] = { ...spec, unit: e.target.value };
                        setFormData({...formData, specifications: newSpecs});
                      }}
                      className="input-field flex-1"
                      placeholder="单位"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const newSpecs = formData.specifications.filter((_, i) => i !== index);
                        setFormData({...formData, specifications: newSpecs});
                      }}
                      className="btn-danger btn-sm"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => setFormData({
                    ...formData, 
                    specifications: [...formData.specifications, { key: '', value: '', unit: '' }]
                  })}
                  className="btn-secondary btn-sm"
                >
                  + 添加参数
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                规格参数用于描述产品的技术规格，如尺寸、重量、颜色等
              </p>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={onClose} className="btn-secondary">
                取消
              </button>
              <button type="submit" className="btn-primary">
                {model ? '更新' : '创建'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductModelPage;