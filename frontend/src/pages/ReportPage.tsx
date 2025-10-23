import React, { useState } from 'react';
import { BarChart3, TrendingUp, Package, Users, Calendar, AlertTriangle, UserPlus, Activity } from 'lucide-react';

const ReportPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sales' | 'inventory' | 'customer'>('sales');
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month' | 'quarter' | 'year'>('month');

  // 模拟销售数据
  const salesData = {
    today: { revenue: 12500, orders: 45, avgOrder: 277.78 },
    week: { revenue: 85600, orders: 312, avgOrder: 274.36 },
    month: { revenue: 385000, orders: 1420, avgOrder: 271.13 },
    quarter: { revenue: 1150000, orders: 4250, avgOrder: 270.59 },
    year: { revenue: 4850000, orders: 17800, avgOrder: 272.47 }
  };

  // 模拟库存数据
  const inventoryData = {
    today: { totalValue: 2850000, lowStock: 12, highStock: 8 },
    week: { totalValue: 2850000, lowStock: 15, highStock: 6 },
    month: { totalValue: 2850000, lowStock: 18, highStock: 4 },
    quarter: { totalValue: 2850000, lowStock: 22, highStock: 3 },
    year: { totalValue: 2850000, lowStock: 25, highStock: 2 }
  };

  // 模拟客户数据
  const customerData = {
    today: { total: 156, new: 8, active: 45 },
    week: { total: 156, new: 35, active: 89 },
    month: { total: 156, new: 142, active: 112 },
    quarter: { total: 156, new: 425, active: 134 },
    year: { total: 156, new: 1780, active: 145 }
  };

  const currentData = activeTab === 'sales' ? salesData[dateRange] : 
                    activeTab === 'inventory' ? inventoryData[dateRange] : 
                    customerData[dateRange];

  // 类型保护函数
  const isSalesData = (data: any): data is { revenue: number; orders: number; avgOrder: number } => {
    return data && typeof data.revenue === 'number' && typeof data.orders === 'number' && typeof data.avgOrder === 'number';
  };

  const isInventoryData = (data: any): data is { totalValue: number; lowStock: number; highStock: number } => {
    return data && typeof data.totalValue === 'number' && typeof data.lowStock === 'number' && typeof data.highStock === 'number';
  };

  const isCustomerData = (data: any): data is { total: number; new: number; active: number } => {
    return data && typeof data.total === 'number' && typeof data.new === 'number' && typeof data.active === 'number';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">报表分析</h1>
        <p className="text-gray-600">查看业务数据统计和分析报告</p>
      </div>

      {/* 时间范围选择器 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <Calendar className="w-5 h-5 text-gray-400" />
          <span className="text-sm font-medium text-gray-700">时间范围:</span>
          <div className="flex space-x-2">
            {['today', 'week', 'month', 'quarter', 'year'].map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range as any)}
                className={`px-3 py-1 rounded-lg text-sm font-medium ${
                  dateRange === range
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {range === 'today' ? '今日' : 
                 range === 'week' ? '本周' : 
                 range === 'month' ? '本月' : 
                 range === 'quarter' ? '本季度' : '本年'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 报表类型标签 */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'sales', label: '销售报表', icon: TrendingUp },
              { id: 'inventory', label: '库存报表', icon: Package },
              { id: 'customer', label: '客户报表', icon: Users }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* 销售报表内容 */}
          {activeTab === 'sales' && isSalesData(currentData) && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-600">销售总额</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">
                        ¥{currentData.revenue.toLocaleString()}
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-green-600">订单数量</p>
                      <p className="text-2xl font-bold text-green-900 mt-1">
                        {currentData.orders}
                      </p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-green-600" />
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-purple-600">平均订单金额</p>
                      <p className="text-2xl font-bold text-purple-900 mt-1">
                        ¥{currentData.avgOrder.toFixed(2)}
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">销售趋势图</h3>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-16 h-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">销售趋势图表区域</span>
                </div>
              </div>
            </div>
          )}

          {/* 库存报表内容 */}
          {activeTab === 'inventory' && isInventoryData(currentData) && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-600">库存总值</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">
                        ¥{currentData.totalValue.toLocaleString()}
                      </p>
                    </div>
                    <Package className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
                
                <div className="bg-orange-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-orange-600">低库存产品</p>
                      <p className="text-2xl font-bold text-orange-900 mt-1">
                        {currentData.lowStock}
                      </p>
                    </div>
                    <AlertTriangle className="w-8 h-8 text-orange-600" />
                  </div>
                </div>
                
                <div className="bg-red-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-red-600">高库存产品</p>
                      <p className="text-2xl font-bold text-red-900 mt-1">
                        {currentData.highStock}
                      </p>
                    </div>
                    <Package className="w-8 h-8 text-red-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">库存分布图</h3>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-16 h-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">库存分布图表区域</span>
                </div>
              </div>
            </div>
          )}

          {/* 客户报表内容 */}
          {activeTab === 'customer' && isCustomerData(currentData) && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-600">客户总数</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">
                        {currentData.total}
                      </p>
                    </div>
                    <Users className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-green-600">新增客户</p>
                      <p className="text-2xl font-bold text-green-900 mt-1">
                        {currentData.new}
                      </p>
                    </div>
                    <UserPlus className="w-8 h-8 text-green-600" />
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-purple-600">活跃客户</p>
                      <p className="text-2xl font-bold text-purple-900 mt-1">
                        {currentData.active}
                      </p>
                    </div>
                    <Activity className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">客户增长趋势</h3>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-16 h-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">客户增长趋势图表区域</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 导出功能 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">导出报表</h3>
            <p className="text-gray-600">导出当前报表数据为Excel或PDF格式</p>
          </div>
          <div className="flex space-x-3">
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
              导出Excel
            </button>
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500">
              导出PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportPage;