import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Calendar, Phone, Mail, MapPin, User } from 'lucide-react';
import { apiClient } from '../services/api/client';
import { Customer } from '../types';

const CustomerDetailPage: React.FC = () => {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 获取客户详情
  const fetchCustomerDetail = async () => {
    if (!uuid) return;
    
    try {
      setLoading(true);
      const customerData = await apiClient.getCustomer(uuid);
      setCustomer(customerData);
      setError(null);
    } catch (err) {
      setError('获取客户详情失败');
      console.error('Error fetching customer detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomerDetail();
  }, [uuid]);

  // 状态徽章
  const getStatusBadge = (isActive: boolean) => {
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
        isActive 
          ? 'bg-green-100 text-green-800' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        {isActive ? '激活' : '停用'}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !customer) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <div className="text-red-600 text-lg font-medium">{error || '客户不存在'}</div>
          <button 
            onClick={() => navigate('/customers')}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-200"
          >
            返回客户列表
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题和操作区 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => navigate('/customers')}
            className="p-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl shadow-lg">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{customer.customerName}</h1>
              <div className="flex items-center space-x-4 mt-1">
                <span className="text-gray-600">{customer.customerCode}</span>
                {getStatusBadge(customer.isActive)}
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button 
            onClick={() => navigate(`/customers/edit/${customer.uuid}`)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-all duration-200"
          >
            <Edit className="w-4 h-4" />
            <span>编辑客户</span>
          </button>
        </div>
      </div>

      {/* 客户信息卡片 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 基本信息 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <User className="w-5 h-5 text-gray-400" />
              <div>
                <div className="text-sm text-gray-500">联系人</div>
                <div className="font-medium text-gray-900">{customer.contactPerson || '未设置'}</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Phone className="w-5 h-5 text-gray-400" />
              <div>
                <div className="text-sm text-gray-500">联系电话</div>
                <div className="font-medium text-gray-900">{customer.phone || '未设置'}</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Mail className="w-5 h-5 text-gray-400" />
              <div>
                <div className="text-sm text-gray-500">邮箱地址</div>
                <div className="font-medium text-gray-900">{customer.email || '未设置'}</div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm text-gray-500">地址</div>
                <div className="font-medium text-gray-900">{customer.address || '未设置'}</div>
              </div>
            </div>
          </div>
        </div>

        {/* 系统信息 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">系统信息</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <div className="text-sm text-gray-500">创建时间</div>
                <div className="font-medium text-gray-900">
                  {new Date(customer.createdAt).toLocaleString()}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <div className="text-sm text-gray-500">更新时间</div>
                <div className="font-medium text-gray-900">
                  {new Date(customer.updatedAt).toLocaleString()}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 flex items-center justify-center">
                <div className={`w-3 h-3 rounded-full ${customer.isActive ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              </div>
              <div>
                <div className="text-sm text-gray-500">状态</div>
                <div className="font-medium text-gray-900">
                  {customer.isActive ? '激活' : '停用'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">业务统计</h3>
          <div className="space-y-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">0</div>
              <div className="text-sm text-blue-500">销售订单</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">¥0.00</div>
              <div className="text-sm text-green-500">交易金额</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">0</div>
              <div className="text-sm text-purple-500">最近交易</div>
            </div>
          </div>
        </div>
      </div>

      {/* 销售订单记录 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">销售订单记录</h3>
        </div>
        
        <div className="p-6">
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">暂无销售订单记录</div>
            <div className="text-gray-500 text-sm mt-2">该客户尚未产生销售订单</div>
          </div>
        </div>
      </div>

      {/* 操作记录 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">操作记录</h3>
        </div>
        
        <div className="p-6">
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">暂无操作记录</div>
            <div className="text-gray-500 text-sm mt-2">该客户暂无操作记录</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerDetailPage;