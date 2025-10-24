import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Eye, Filter, MoreHorizontal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api/client';
import { Customer, CreateCustomerRequest, UpdateCustomerRequest } from '../types';

// 生成客户编码：C + 7位大写英文加数字组合
const generateCustomerCode = (): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const prefix = 'C';
  let randomPart = '';
  for (let i = 0; i < 7; i++) {
    randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return prefix + randomPart;
};

const CustomerPage: React.FC = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);

  // 获取客户列表
  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        size: pageSize,
        search: searchTerm || undefined,
      };
      const response = await apiClient.getCustomers(params);
      setCustomers(response.items);
      setTotal(response.total);
      setError(null);
    } catch (err) {
      setError('获取客户列表失败');
      console.error('Error fetching customers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [currentPage, searchTerm]);

  // 处理搜索
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCustomers();
  };

  // 处理创建/编辑客户
  const handleSubmitCustomer = async (customerData: CreateCustomerRequest | UpdateCustomerRequest) => {
    try {
      if (editingCustomer) {
        // 编辑客户
        await apiClient.updateCustomer(editingCustomer.uuid, customerData as UpdateCustomerRequest);
      } else {
        // 创建客户
        await apiClient.createCustomer(customerData as CreateCustomerRequest);
      }
      
      setShowForm(false);
      setEditingCustomer(null);
      fetchCustomers();
    } catch (err) {
      setError(editingCustomer ? '更新客户失败' : '创建客户失败');
      console.error('Error submitting customer:', err);
    }
  };

  // 处理删除客户
  const handleDelete = async (uuid: string) => {
    if (window.confirm('确定要删除这个客户吗？')) {
      try {
        await apiClient.deleteCustomer(uuid);
        fetchCustomers();
      } catch (err) {
        setError('删除客户失败');
        console.error('Error deleting customer:', err);
      }
    }
  };

  // 处理编辑客户
  const handleEditCustomer = (customer: Customer) => {
    setEditingCustomer(customer);
    setShowForm(true);
  };

  // 处理查看客户详情
  const handleViewCustomer = (uuid: string) => {
    navigate(`/customers/${uuid}`);
  };

  // 状态徽章
  const getStatusBadge = (isActive: boolean) => {
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        isActive 
          ? 'bg-green-100 text-green-800' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        {isActive ? '激活' : '停用'}
      </span>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题区 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl shadow-lg">
            <Plus className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">客户管理</h1>
            <p className="text-gray-600">管理系统客户信息和联系方式</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200"
          >
            <Filter className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-700">筛选</span>
          </button>
          
          <button 
            onClick={() => {
              setEditingCustomer(null);
              setShowForm(true);
            }}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-xl hover:shadow-lg transition-all duration-200"
          >
            <Plus className="w-4 h-4" />
            <span>新增客户</span>
          </button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center">
            <div className="text-red-600 text-sm">{error}</div>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* 搜索和筛选区 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-4 border-b border-gray-100">
          <form onSubmit={handleSearch} className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索客户名称、编码、联系人、电话..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200"
            >
              搜索
            </button>
          </form>
        </div>

        {/* 筛选条件 */}
        {showFilters && (
          <div className="p-4 border-t border-gray-100">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">状态筛选</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option value="">全部状态</option>
                  <option value="active">激活</option>
                  <option value="inactive">停用</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">创建时间</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-end space-x-2">
                <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200">
                  应用筛选
                </button>
                <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200">
                  重置
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 客户列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">客户信息</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">编码</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">联系人</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">联系方式</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                // 加载状态
                Array.from({ length: 5 }).map((_, index) => (
                  <tr key={index}>
                    <td colSpan={7} className="px-6 py-4">
                      <div className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                      </div>
                    </td>
                  </tr>
                ))
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    <div className="flex flex-col items-center space-y-2">
                      <Search className="w-12 h-12 text-gray-300" />
                      <div className="text-lg font-medium">暂无客户数据</div>
                      <div className="text-sm">点击"新增客户"按钮添加第一个客户</div>
                    </div>
                  </td>
                </tr>
              ) : (
                customers.map((customer) => (
                  <tr key={customer.uuid} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{customer.customerName}</div>
                        <div className="text-sm text-gray-500">{customer.address}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {customer.customerCode}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {customer.contactPerson}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{customer.phone}</div>
                      <div>{customer.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(customer.isActive)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(customer.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button 
                          onClick={() => handleViewCustomer(customer.uuid)}
                          className="text-blue-600 hover:text-blue-900"
                          title="查看详情"
                        >
                          <Eye size={16} />
                        </button>
                        <button 
                          onClick={() => handleEditCustomer(customer)}
                          className="text-green-600 hover:text-green-900"
                          title="编辑客户"
                        >
                          <Edit size={16} />
                        </button>
                        <button 
                          onClick={() => handleDelete(customer.uuid)}
                          className="text-red-600 hover:text-red-900"
                          title="删除客户"
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

        {/* 分页 */}
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

      {/* 客户表单 */}
      {showForm && (
        <CustomerForm
          customer={editingCustomer}
          onSubmit={handleSubmitCustomer}
          onCancel={() => {
            setShowForm(false);
            setEditingCustomer(null);
          }}
        />
      )}
    </div>
  );
};

// 客户表单组件
interface CustomerFormProps {
  customer?: Customer | null;
  onSubmit: (data: CreateCustomerRequest | UpdateCustomerRequest) => void;
  onCancel: () => void;
}

const CustomerForm: React.FC<CustomerFormProps> = ({ customer, onSubmit, onCancel }) => {
  // 如果是新增客户，自动生成客户编码；如果是编辑客户，使用原有的客户编码
  const initialCustomerCode = customer ? customer.customerCode : generateCustomerCode();
  
  const [formData, setFormData] = useState<CreateCustomerRequest>({
    customerName: customer?.customerName || '',
    customerCode: initialCustomerCode,
    contactPerson: customer?.contactPerson || '',
    phone: customer?.phone || '',
    email: customer?.email || '',
    address: customer?.address || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (field: keyof CreateCustomerRequest, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {customer ? '编辑客户' : '新增客户'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">客户名称 *</label>
              <input
                type="text"
                required
                value={formData.customerName}
                onChange={(e) => handleChange('customerName', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">客户编码 *</label>
              <input
                type="text"
                required
                value={formData.customerCode}
                onChange={(e) => handleChange('customerCode', e.target.value)}
                readOnly={!customer} // 新增客户时只读，编辑客户时可编辑
                className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  !customer ? 'bg-gray-100 cursor-not-allowed' : ''
                }`}
              />
              {!customer && (
                <p className="text-xs text-gray-500 mt-1">客户编码由系统自动生成</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">联系人</label>
              <input
                type="text"
                value={formData.contactPerson}
                onChange={(e) => handleChange('contactPerson', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">联系电话</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">邮箱地址</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">地址</label>
              <textarea
                value={formData.address}
                onChange={(e) => handleChange('address', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200"
              >
                {customer ? '更新客户' : '创建客户'}
              </button>
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CustomerPage;