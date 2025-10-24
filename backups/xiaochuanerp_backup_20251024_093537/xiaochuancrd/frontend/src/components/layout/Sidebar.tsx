import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  Truck, 
  ShoppingCart, 
  BarChart3, 
  Users, 
  Settings,
  Building2,
  ChevronLeft,
  ChevronRight,
  Cpu,
  FileText,
  User,
  UploadCloud,
  Bot
} from 'lucide-react';

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed = false, onToggle }) => {
  const navigationItems = [
    { path: '/dashboard', label: '仪表盘', icon: LayoutDashboard, color: 'text-blue-600' },
    { path: '/products', label: '产品管理', icon: Package, color: 'text-green-600' },
    { path: '/product-categories', label: '产品分类管理', icon: BarChart3, color: 'text-teal-600' },
    { path: '/product-models', label: '产品型号管理', icon: Cpu, color: 'text-indigo-600' },
    { path: '/inventory', label: '库存管理', icon: Building2, color: 'text-purple-600' },
    { path: '/suppliers', label: '供应商管理', icon: Truck, color: 'text-orange-600' },
    { path: '/customers', label: '客户管理', icon: User, color: 'text-cyan-600' },
    { path: '/sales-orders', label: '销售管理', icon: ShoppingCart, color: 'text-red-600' },
    { path: '/purchase-orders', label: '采购管理', icon: BarChart3, color: 'text-cyan-600' },
    { path: '/reports', label: '报表分析', icon: BarChart3, color: 'text-gray-600' },
    { path: '/smart-assistant', label: '智能助手', icon: Bot, color: 'text-violet-600' },
    { path: '/markdown-converter-demo', label: 'Markdown转换器', icon: FileText, color: 'text-blue-600' },
    { path: '/users', label: '用户管理', icon: Users, color: 'text-pink-600' },
    { path: '/operation-logs', label: '操作日志', icon: FileText, color: 'text-amber-600' },
    { path: '/coze', label: 'Coze', icon: UploadCloud, color: 'text-indigo-600' },
  ];

  return (
    <aside className="h-full bg-white border-r border-gray-100 shadow-lg relative">
      {/* Logo区域 */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">WY</span>
            </div>
            {!collapsed && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900">进销存系统</h2>
                <p className="text-xs text-gray-500">企业版 v1.0</p>
              </div>
            )}
          </div>
          
          {/* 折叠按钮 */}
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors duration-200"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4 text-gray-600" />
            ) : (
              <ChevronLeft className="w-4 h-4 text-gray-600" />
            )}
          </button>
        </div>
      </div>

      {/* 导航菜单 - 可滚动区域 */}
      <div className="flex-1 overflow-hidden">
        <nav 
          className="p-4 space-y-2 h-full overflow-y-auto sidebar-scroll"
          style={{ maxHeight: 'calc(100vh - 200px)' }}
          onWheel={(e) => {
            // 允许鼠标滚轮滚动
            e.currentTarget.scrollTop += e.deltaY;
          }}
        >
          {navigationItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-xl transition-all duration-200 group relative ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-200/50 text-blue-700 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  } ${collapsed ? 'justify-center' : 'justify-between'}`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center">
                      <IconComponent className={`w-5 h-5 ${item.color} ${collapsed ? '' : 'mr-3'}`} />
                      {!collapsed && (
                        <span className="font-medium">{item.label}</span>
                      )}
                    </div>
                    
                    {/* 活动状态指示器 */}
                    {isActive && (
                      <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-6 bg-blue-500 rounded-r-full"></div>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* 设置菜单 */}
      {!collapsed && (
        <div className="absolute bottom-20 left-4 right-4">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-200 text-gray-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Settings className="w-5 h-5 text-gray-500 mr-3" />
                <span className="font-medium">系统设置</span>
              </>
            )}
          </NavLink>
        </div>
      )}

      {/* 底部系统状态 */}
      <div className={`absolute bottom-4 left-4 right-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-100 ${
        collapsed ? 'hidden' : ''
      }`}>
        <div className="flex items-center space-x-3">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <div className="flex-1">
            <p className="text-sm font-medium text-green-800">系统运行正常</p>
            <p className="text-xs text-green-600">在线用户: 3人</p>
          </div>
        </div>
      </div>
      
      {/* 折叠状态下的系统状态 */}
      {collapsed && (
        <div className="absolute bottom-4 left-2 right-2 p-2 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-100">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mx-auto"></div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;