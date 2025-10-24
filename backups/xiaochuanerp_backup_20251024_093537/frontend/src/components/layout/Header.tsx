import React, { useState } from 'react';
import { Bell, User, LogOut, Search, Menu, X, Settings, HelpCircle } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

const Header: React.FC = () => {
  const { user, logout } = useAuthStore();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <header className="bg-white border-b border-gray-100 shadow-sm">
      <div className="flex items-center justify-between h-16 px-6">
        {/* 左侧：页面标题和面包屑 */}
        <div className="flex items-center space-x-6">
          <div>
            <h1 className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              进销存管理系统
            </h1>
            <p className="text-xs text-gray-500 mt-1">企业级库存与销售管理平台</p>
          </div>
        </div>
        
        {/* 中间：搜索框 */}
        <div className="flex-1 max-w-md mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索产品、订单、供应商..."
              className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
            />
          </div>
        </div>
        
        {/* 右侧操作区 */}
        <div className="flex items-center space-x-3">
          {/* 快速操作按钮 */}
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200">
              <HelpCircle className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200">
              <Settings className="w-5 h-5" />
            </button>
          </div>
          
          {/* 通知 */}
          <button className="relative p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
          </button>
          
          {/* 用户信息 */}
          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-all duration-200"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="text-left hidden md:block">
                  <div className="font-medium text-gray-900">{user?.username || '管理员'}</div>
                  <div className="text-xs text-gray-500">
                    {user?.role === 'admin' ? '系统管理员' : '普通用户'}
                  </div>
                </div>
              </div>
            </button>
            
            {/* 用户菜单下拉 */}
            {isUserMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
                <div className="px-4 py-2 border-b border-gray-100">
                  <div className="text-sm font-medium text-gray-900">{user?.username || '管理员'}</div>
                  <div className="text-xs text-gray-500">{user?.email || 'admin@example.com'}</div>
                </div>
                <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-200">
                  个人设置
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-200">
                  修改密码
                </button>
                <div className="border-t border-gray-100 mt-2 pt-2">
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors duration-200 flex items-center"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    退出登录
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* 遮罩层 */}
      {isUserMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-10 z-40" 
          onClick={() => setIsUserMenuOpen(false)}
        />
      )}
    </header>
  );
};

export default Header;