import React from 'react';
import { Users, Plus, Search, Filter, MoreHorizontal } from 'lucide-react';

interface User {
  uuid: string;
  username: string;
  email: string;
  role: string;
  status: 'active' | 'inactive';
  lastLogin: string;
  createdAt: string;
}

const UserPage: React.FC = () => {
  // 模拟用户数据
  const mockUsers: User[] = [
    {
      uuid: '1',
      username: 'admin',
      email: 'admin@company.com',
      role: '管理员',
      status: 'active',
      lastLogin: '2024-01-15 10:30:00',
      createdAt: '2024-01-01 09:00:00'
    },
    {
      uuid: '2',
      username: 'manager',
      email: 'manager@company.com',
      role: '经理',
      status: 'active',
      lastLogin: '2024-01-15 09:15:00',
      createdAt: '2024-01-02 14:20:00'
    },
    {
      uuid: '3',
      username: 'operator',
      email: 'operator@company.com',
      role: '操作员',
      status: 'inactive',
      lastLogin: '2024-01-10 16:45:00',
      createdAt: '2024-01-03 11:30:00'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题区 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-pink-500 to-rose-500 rounded-2xl shadow-lg">
            <Users className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
            <p className="text-gray-600">管理系统用户账号和权限</p>
          </div>
        </div>
        
        <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl hover:shadow-lg transition-all duration-200">
          <Plus className="w-4 h-4" />
          <span>新增用户</span>
        </button>
      </div>

      {/* 搜索和筛选区 */}
      <div className="flex items-center space-x-4 p-4 bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索用户名、邮箱..."
            className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>
        
        <select className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
          <option value="">所有角色</option>
          <option value="admin">管理员</option>
          <option value="manager">经理</option>
          <option value="operator">操作员</option>
        </select>
        
        <select className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
          <option value="">所有状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
        </select>
        
        <button className="p-2 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors duration-200">
          <Filter className="w-4 h-4 text-gray-600" />
        </button>
      </div>

      {/* 用户列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户信息</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后登录</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {mockUsers.map((user) => (
                <tr key={user.uuid} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-rose-400 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold text-sm">
                          {user.username.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{user.username}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {user.status === 'active' ? '活跃' : '非活跃'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{user.lastLogin}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{user.createdAt}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200">
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 分页 */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 rounded-b-xl">
        <div className="text-sm text-gray-700">
          显示 <span className="font-medium">1-3</span> 条，共 <span className="font-medium">3</span> 条记录
        </div>
        <div className="flex items-center space-x-2">
          <button className="px-3 py-1 text-sm bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors duration-200">
            上一页
          </button>
          <button className="px-3 py-1 text-sm bg-blue-500 text-white border border-blue-500 rounded-md hover:bg-blue-600 transition-colors duration-200">
            1
          </button>
          <button className="px-3 py-1 text-sm bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors duration-200">
            下一页
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserPage;