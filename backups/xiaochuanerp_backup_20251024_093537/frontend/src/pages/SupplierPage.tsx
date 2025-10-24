import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Users, Phone, Mail, MapPin } from 'lucide-react';
import { apiClient } from '../services/api/client';
import type { Supplier, CreateSupplierRequest } from '../types';

// 生成供应商编码：S + 7位大写英文加数字组合
const generateSupplierCode = (): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const prefix = 'S';
  let randomPart = '';
  for (let i = 0; i < 7; i++) {
    randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return prefix + randomPart;
};

const SupplierPage: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);

  // 加载供应商列表
  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getSuppliers({ search: searchTerm || undefined });
      // 确保response存在且有items字段
      if (response && response.items) {
        setSuppliers(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setSuppliers([]);
      }
    } catch (error) {
      console.error('加载供应商失败:', error);
      setSuppliers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSupplier = async (supplierData: CreateSupplierRequest) => {
    try {
      await apiClient.createSupplier(supplierData);
      setShowCreateModal(false);
      loadSuppliers();
    } catch (error) {
      console.error('创建供应商失败:', error);
    }
  };

  const handleDeleteSupplier = async (uuid: string) => {
    if (window.confirm('确定要删除这个供应商吗？')) {
      try {
        await apiClient.deleteSupplier(uuid);
        loadSuppliers();
      } catch (error) {
        console.error('删除供应商失败:', error);
      }
    }
  };

  const filteredSuppliers = suppliers.filter(supplier =>
    supplier.supplierName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    supplier.supplierCode.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 页面标题和操作栏 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">供应商管理</h1>
          <p className="text-gray-600 mt-1">管理您的供应商信息和联系方式</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>新增供应商</span>
        </button>
      </div>

      {/* 搜索栏 */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="搜索供应商名称或编码..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <button onClick={loadSuppliers} className="btn-secondary">
          刷新
        </button>
      </div>

      {/* 供应商列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">供应商信息</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">编码</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">联系人</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">联系方式</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                // 加载状态
                Array.from({ length: 5 }).map((_, index) => (
                  <tr key={index}>
                    <td colSpan={6} className="px-6 py-4">
                      <div className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                      </div>
                    </td>
                  </tr>
                ))
              ) : filteredSuppliers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    <div className="flex flex-col items-center space-y-2">
                      <Search className="w-12 h-12 text-gray-300" />
                      <div className="text-lg font-medium">暂无供应商数据</div>
                      <div className="text-sm">点击"新增供应商"按钮添加第一个供应商</div>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredSuppliers.map((supplier) => (
                  <tr key={supplier.uuid} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{supplier.supplierName}</div>
                        <div className="text-sm text-gray-500">{supplier.address}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {supplier.supplierCode}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {supplier.contactPerson}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{supplier.phone}</div>
                      <div>{supplier.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(supplier.createdAt).toLocaleDateString('zh-CN')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button 
                          onClick={() => setEditingSupplier(supplier)}
                          className="text-green-600 hover:text-green-900"
                          title="编辑供应商"
                        >
                          <Edit size={16} />
                        </button>
                        <button 
                          onClick={() => handleDeleteSupplier(supplier.uuid)}
                          className="text-red-600 hover:text-red-900"
                          title="删除供应商"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 创建/编辑供应商模态框 */}
      {showCreateModal && (
        <SupplierFormModal
          onSubmit={handleCreateSupplier}
          onClose={() => setShowCreateModal(false)}
        />
      )}
      
      {editingSupplier && (
        <SupplierFormModal
          supplier={editingSupplier}
          onSubmit={handleCreateSupplier}
          onClose={() => setEditingSupplier(null)}
        />
      )}
    </div>
  );
};

// 供应商表单模态框组件
interface SupplierFormModalProps {
  supplier?: Supplier;
  onSubmit: (data: CreateSupplierRequest) => void;
  onClose: () => void;
}

const SupplierFormModal: React.FC<SupplierFormModalProps> = ({ supplier, onSubmit, onClose }) => {
  // 生成初始编码：编辑时使用原编码，新增时生成新编码
  const initialSupplierCode = supplier ? supplier.supplierCode : generateSupplierCode();
  
  const [formData, setFormData] = useState<CreateSupplierRequest>({
    supplierName: supplier?.supplierName || '',
    supplierCode: initialSupplierCode, // 使用生成的编码
    contactPerson: supplier?.contactPerson || '',
    phone: supplier?.phone || '',
    email: supplier?.email || '',
    address: supplier?.address || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {supplier ? '编辑供应商' : '新增供应商'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                供应商名称
              </label>
              <input
                type="text"
                required
                value={formData.supplierName}
                onChange={(e) => setFormData({ ...formData, supplierName: e.target.value })}
                className="input-field"
              />
            </div>
            
            {supplier ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  供应商编码
                </label>
                <input
                  type="text"
                  required
                  value={formData.supplierCode || ''}
                  onChange={(e) => setFormData({ ...formData, supplierCode: e.target.value })}
                  className="input-field"
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  供应商编码
                </label>
                <input
                  type="text"
                  value={formData.supplierCode}
                  readOnly
                  className="input-field bg-gray-100 cursor-not-allowed"
                />
                <p className="text-xs text-gray-500 mt-1">供应商编码将由系统自动生成（S + 7位大写英文加数字）</p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                联系人
              </label>
              <input
                type="text"
                required
                value={formData.contactPerson}
                onChange={(e) => setFormData({ ...formData, contactPerson: e.target.value })}
                className="input-field"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  电话
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  邮箱
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input-field"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                地址
              </label>
              <textarea
                required
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="input-field min-h-[80px]"
              />
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={onClose} className="btn-secondary">
                取消
              </button>
              <button type="submit" className="btn-primary">
                {supplier ? '更新' : '创建'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SupplierPage;