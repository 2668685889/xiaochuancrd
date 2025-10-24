import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-cyan-50/20">
      {/* 侧边栏 */}
      <div className={`transition-all duration-300 ease-in-out ${
        sidebarCollapsed ? 'w-20' : 'w-64'
      }`}>
        <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      </div>
      
      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部导航 */}
        <Header />
        
        {/* 页面内容 */}
        <main className="flex-1 overflow-hidden p-4 lg:p-6">
          <div className="w-full max-w-none xl:max-w-7xl mx-auto h-full overflow-auto">
            <Outlet />
          </div>
        </main>
        
        {/* 底部信息栏 */}
        <footer className="bg-white border-t border-gray-100 py-3 px-4 lg:px-6">
          <div className="flex flex-col lg:flex-row items-center justify-between text-xs text-gray-500 space-y-2 lg:space-y-0">
            <div>© 2024 进销存管理系统 - 企业级库存管理解决方案</div>
            <div className="flex flex-wrap items-center justify-center lg:justify-end space-x-2 lg:space-x-4">
              <span>版本 v1.0.0</span>
              <span className="hidden lg:inline">•</span>
              <span>技术支持: support@example.com</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default MainLayout;