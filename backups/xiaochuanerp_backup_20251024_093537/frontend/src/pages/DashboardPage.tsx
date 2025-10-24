import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Package, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  ShoppingCart, 
  Truck,
  RefreshCw,
  Eye,
  Download,
  Filter,
  Calendar,
  MoreHorizontal,
  Activity
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';
import { apiClient } from '../services/api/client';
import type { 
  DashboardStats, 
  ProductDistribution, 
  RecentActivity,
  SalesData 
} from '../types';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'];

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [productDistribution, setProductDistribution] = useState<ProductDistribution[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [timeScale, setTimeScale] = useState<'day' | 'week' | 'month'>('week');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSalesData = async (scale: 'day' | 'week' | 'month') => {
    try {
      // 模拟销售数据 - 在实际应用中应该从API获取
      if (scale === 'day') {
        const mockDayData: SalesData[] = [
          { period: '00:00', salesAmount: 800, salesCount: 3, averageAmount: 266.67 },
          { period: '04:00', salesAmount: 1200, salesCount: 5, averageAmount: 240.00 },
          { period: '08:00', salesAmount: 4500, salesCount: 15, averageAmount: 300.00 },
          { period: '12:00', salesAmount: 9800, salesCount: 32, averageAmount: 306.25 },
          { period: '16:00', salesAmount: 7600, salesCount: 25, averageAmount: 304.00 },
          { period: '20:00', salesAmount: 5200, salesCount: 17, averageAmount: 305.88 }
        ];
        setSalesData(mockDayData);
      } else if (scale === 'week') {
        const mockWeekData: SalesData[] = [
          { period: '周一', salesAmount: 18500, salesCount: 62, averageAmount: 298.39 },
          { period: '周二', salesAmount: 21000, salesCount: 78, averageAmount: 269.23 },
          { period: '周三', salesAmount: 16500, salesCount: 55, averageAmount: 300.00 },
          { period: '周四', salesAmount: 28000, salesCount: 92, averageAmount: 304.35 },
          { period: '周五', salesAmount: 32000, salesCount: 105, averageAmount: 304.76 },
          { period: '周六', salesAmount: 45000, salesCount: 148, averageAmount: 304.05 },
          { period: '周日', salesAmount: 38000, salesCount: 125, averageAmount: 304.00 }
        ];
        setSalesData(mockWeekData);
      } else {
        const mockMonthData: SalesData[] = [
          { period: '1月', salesAmount: 450000, salesCount: 1480, averageAmount: 304.05 },
          { period: '2月', salesAmount: 520000, salesCount: 1710, averageAmount: 304.09 },
          { period: '3月', salesAmount: 480000, salesCount: 1580, averageAmount: 303.80 },
          { period: '4月', salesAmount: 560000, salesCount: 1840, averageAmount: 304.35 },
          { period: '5月', salesAmount: 610000, salesCount: 2000, averageAmount: 305.00 },
          { period: '6月', salesAmount: 590000, salesCount: 1940, averageAmount: 304.12 }
        ];
        setSalesData(mockMonthData);
      }
    } catch (err) {
      console.error('Error fetching sales data:', err);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行获取所有数据
      const [statsData, productData, activitiesData] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getProductDistribution(),
        apiClient.getRecentActivities()
      ]);

      console.log('Dashboard stats data:', statsData); // 调试信息
      console.log('Inventory value:', statsData?.inventoryValue); // 调试信息
      
      setStats(statsData);
      setProductDistribution(productData.distribution);
      setRecentActivities(activitiesData.activities);
      
      // 获取销售数据
      await fetchSalesData(timeScale);
    } catch (err) {
      setError('获取仪表盘数据失败');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeScaleChange = (scale: 'day' | 'week' | 'month') => {
    setTimeScale(scale);
    fetchSalesData(scale);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
    }).format(value);
  };

  const formatLargeCurrency = (value: number) => {
    if (value >= 100000000) {
      // 大于等于1亿，显示为亿元
      return `¥${(value / 100000000).toFixed(1)}亿`;
    } else if (value >= 10000) {
      // 大于等于1万，显示为万元
      return `¥${(value / 10000).toFixed(1)}万`;
    } else {
      // 小于1万，使用普通货币格式化
      return formatCurrency(value);
    }
  };

  // 专门为库存价值卡片设计的格式化函数，始终以"万"为单位
  const formatInventoryValue = (value: number) => {
    if (value === null || value === undefined || isNaN(value)) {
      return '¥0万';
    }
    
    // 如果值为0，直接返回0万
    if (value === 0) {
      return '¥0万';
    }
    
    // 无论数值大小，都转换为万元显示
    const valueInWan = value / 10000;
    
    // 处理非常小的数值（小于0.01万的情况）
    if (valueInWan < 0.01) {
      return `¥${value.toLocaleString('zh-CN')}`;
    }
    
    if (valueInWan >= 10000) {
      // 如果超过1亿，显示为亿元
      return `¥${(valueInWan / 10000).toFixed(1)}亿`;
    } else if (valueInWan >= 1) {
      // 大于等于1万，显示为万元
      return `¥${valueInWan.toFixed(1)}万`;
    } else {
      // 小于1万，显示为小数万元
      return `¥${valueInWan.toFixed(2)}万`;
    }
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('zh-CN').format(value);
  };

  const formatTime = (timeString: string) => {
    const time = new Date(timeString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return '刚刚';
    if (diffInMinutes < 60) return `${diffInMinutes}分钟前`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}小时前`;
    return `${Math.floor(diffInMinutes / 1440)}天前`;
  };

  if (loading) {
    return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="text-center">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-8 h-8 mx-auto mb-4 text-red-600" />
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  // 处理卡片点击跳转
  const handleCardClick = (route: string) => {
    navigate(route);
  };

  const statCards = [
    {
      title: '产品总数',
      value: stats ? formatNumber(stats.productCount) : '0',
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-gradient-to-br from-blue-50 to-blue-100',
      borderColor: 'border-blue-200',
      trend: '+12%',
      trendColor: 'text-green-600',
      route: '/products',
    },
    {
      title: '供应商数量',
      value: stats ? formatNumber(stats.supplierCount) : '0',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-gradient-to-br from-green-50 to-green-100',
      borderColor: 'border-green-200',
      trend: '+5%',
      trendColor: 'text-green-600',
      route: '/suppliers',
    },
    {
      title: '库存价值',
      value: stats ? formatInventoryValue(stats.inventoryValue) : '¥0万',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-gradient-to-br from-purple-50 to-purple-100',
      borderColor: 'border-purple-200',
      trend: '+8.2%',
      trendColor: 'text-green-600',
      customWidth: 'min-w-[200px]', // 增加最小宽度，确保卡片有足够空间显示各种格式的数值
      route: '/inventory',
    },
    {
      title: '库存预警',
      value: stats ? formatNumber(stats.lowStockCount) : '0',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-gradient-to-br from-red-50 to-red-100',
      borderColor: 'border-red-200',
      trend: '-3%',
      trendColor: 'text-green-600',
      route: '/inventory',
    },
    {
      title: '今日销售',
      value: stats ? formatNumber(stats.todaySalesCount) : '0',
      icon: ShoppingCart,
      color: 'text-orange-600',
      bgColor: 'bg-gradient-to-br from-orange-50 to-orange-100',
      borderColor: 'border-orange-200',
      trend: '+15%',
      trendColor: 'text-green-600',
      route: '/sales-orders',
    },
    {
      title: '今日采购',
      value: stats ? formatNumber(stats.todayPurchaseCount) : '0',
      icon: Truck,
      color: 'text-indigo-600',
      bgColor: 'bg-gradient-to-br from-indigo-50 to-indigo-100',
      borderColor: 'border-indigo-200',
      trend: '+7%',
      trendColor: 'text-green-600',
      route: '/purchase-orders',
    },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题和操作按钮 */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            仪表盘
          </h1>
          <p className="text-gray-500 mt-1 text-sm lg:text-base">实时监控系统关键指标和业务数据</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 lg:gap-3">
          <button className="flex items-center space-x-2 px-3 lg:px-4 py-2 lg:py-2.5 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-sm text-xs lg:text-sm">
            <Filter className="w-3 h-3 lg:w-4 lg:h-4 text-gray-600" />
            <span className="font-medium text-gray-700">筛选</span>
          </button>
          <button className="flex items-center space-x-2 px-3 lg:px-4 py-2 lg:py-2.5 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-sm text-xs lg:text-sm">
            <Download className="w-3 h-3 lg:w-4 lg:h-4 text-gray-600" />
            <span className="font-medium text-gray-700">导出</span>
          </button>
          <button
            onClick={fetchDashboardData}
            className="flex items-center space-x-2 px-3 lg:px-4 py-2 lg:py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 shadow-lg text-xs lg:text-sm"
          >
            <RefreshCw className="w-3 h-3 lg:w-4 lg:h-4" />
            <span className="font-medium">刷新数据</span>
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div 
              key={stat.title} 
              className={`p-4 lg:p-5 rounded-2xl border ${stat.borderColor} shadow-sm hover:shadow-md transition-all duration-300 ${stat.bgColor} ${stat.customWidth || ''} cursor-pointer`}
              onClick={() => handleCardClick(stat.route)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-600 uppercase tracking-wide truncate">{stat.title}</p>
                  <p className="text-xl lg:text-2xl font-bold text-gray-900 mt-1 break-all">{stat.value}</p>
                  <p className={`text-xs font-medium mt-1 ${stat.trendColor} truncate`}>
                    {stat.trend}
                  </p>
                </div>
                <div className={`flex-shrink-0 p-2 lg:p-3 rounded-xl bg-white/50 backdrop-blur-sm border ${stat.borderColor} ml-3`}>
                  <Icon className={`w-5 h-5 lg:w-6 lg:h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 lg:gap-6">
        {/* 产品分布饼状图 */}
        <div className="bg-white rounded-2xl border border-gray-100 p-4 lg:p-6 shadow-sm hover:shadow-md transition-all duration-300">
          <div className="flex items-center justify-between mb-4 lg:mb-6">
            <h2 className="text-base lg:text-lg font-semibold text-gray-900">产品价值分布</h2>
          </div>
          <div className="h-64 lg:h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={productDistribution.map(item => ({
                    name: item.name,
                    value: item.value,
                    count: item.count
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {productDistribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), '价值']}
                  contentStyle={{
                    borderRadius: '12px',
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Legend 
                  wrapperStyle={{
                    paddingTop: '20px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 销售额柱形图 */}
        <div className="bg-white rounded-2xl border border-gray-100 p-4 lg:p-6 shadow-sm hover:shadow-md transition-all duration-300">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-4 lg:mb-6 space-y-3 lg:space-y-0">
            <h2 className="text-base lg:text-lg font-semibold text-gray-900">销售额统计</h2>
            <div className="flex items-center space-x-2">
              <div className="flex bg-gray-100 rounded-xl p-1">
                <button
                  onClick={() => handleTimeScaleChange('day')}
                  className={`px-2 lg:px-3 py-1.5 text-xs lg:text-sm font-medium rounded-lg transition-all duration-200 ${
                    timeScale === 'day' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  日
                </button>
                <button
                  onClick={() => handleTimeScaleChange('week')}
                  className={`px-2 lg:px-3 py-1.5 text-xs lg:text-sm font-medium rounded-lg transition-all duration-200 ${
                    timeScale === 'week' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  周
                </button>
                <button
                  onClick={() => handleTimeScaleChange('month')}
                  className={`px-2 lg:px-3 py-1.5 text-xs lg:text-sm font-medium rounded-lg transition-all duration-200 ${
                    timeScale === 'month' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  月
                </button>
              </div>
            </div>
          </div>
          <div className="h-64 lg:h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis 
                  dataKey="period" 
                  angle={-45}
                  textAnchor="end"
                  height={60}
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  tickFormatter={(value) => formatCurrency(value)}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), '销售额']}
                  labelFormatter={(label) => `时间段: ${label}`}
                  contentStyle={{
                    borderRadius: '12px',
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Legend />
                <Bar 
                  dataKey="salesAmount" 
                  name="销售额" 
                  fill="url(#salesGradient)"
                  radius={[8, 8, 0, 0]}
                />
                <defs>
                  <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.3} />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 最近活动 */}
      <div className="bg-white rounded-2xl border border-gray-100 p-4 lg:p-6 shadow-sm hover:shadow-md transition-all duration-300">
        <div className="flex items-center justify-between mb-4 lg:mb-6">
          <h2 className="text-base lg:text-lg font-semibold text-gray-900">最近活动</h2>
          <button className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200">
            查看全部
          </button>
        </div>
        <div className="space-y-2 lg:space-y-3">
          {recentActivities.length > 0 ? (
            recentActivities.map((activity, index) => (
              <div 
                key={index} 
                className="flex items-center space-x-3 lg:space-x-4 p-3 lg:p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:border-gray-200 transition-all duration-200"
              >
                <div className={`flex-shrink-0 w-8 h-8 lg:w-10 lg:h-10 rounded-xl flex items-center justify-center ${
                  activity.type === '新增' ? 'bg-green-50 border border-green-200' :
                  activity.type === '更新' ? 'bg-blue-50 border border-blue-200' :
                  activity.type === '删除' ? 'bg-red-50 border border-red-200' :
                  'bg-gray-50 border border-gray-200'
                }`}>
                  <Activity className={`w-4 h-4 lg:w-5 lg:h-5 ${
                    activity.type === '新增' ? 'text-green-600' :
                    activity.type === '更新' ? 'text-blue-600' :
                    activity.type === '删除' ? 'text-red-600' :
                    'text-gray-600'
                  }`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs lg:text-sm font-medium text-gray-900 truncate">{activity.description}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <p className="text-xs text-gray-500">{formatTime(activity.time)}</p>
                    <span className="text-xs text-gray-400">•</span>
                    <p className="text-xs text-gray-500">{activity.user}</p>
                  </div>
                </div>
                <div className={`text-xs px-2 lg:px-3 py-1 lg:py-1.5 rounded-full font-medium ${
                  activity.type === '新增' ? 'bg-green-100 text-green-700' :
                  activity.type === '更新' ? 'bg-blue-100 text-blue-700' :
                  activity.type === '删除' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {activity.type}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <Activity className="w-16 h-16 text-gray-200 mx-auto mb-4" />
              <p className="text-gray-500 text-sm">暂无活动记录</p>
              <p className="text-gray-400 text-xs mt-1">系统活动将在这里显示</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;