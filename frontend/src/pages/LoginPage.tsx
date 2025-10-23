import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, Eye, EyeOff, Package, Sparkles } from 'lucide-react';
import { apiClient } from '../services/api/client';
import { useAuthStore } from '../stores/authStore';

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!formData.username || !formData.password) {
      setError('请输入用户名和密码');
      return;
    }

    try {
      setLoading(true);
      
      console.log('开始登录流程...');
      console.log('用户名:', formData.username);
      
      // 第一步：调用登录API
      const response = await apiClient.login({
        username: formData.username,
        password: formData.password,
      });
      
      console.log('✅ API登录成功');
      console.log('令牌长度:', response.token ? response.token.length : 0);
      console.log('令牌前20位:', response.token ? response.token.substring(0, 20) + '...' : 'null');
      
      if (!response.token) {
        throw new Error('服务器返回的令牌为空');
      }
      
      // 第二步：手动存储令牌到localStorage（双重保险）
      console.log('手动存储令牌到localStorage...');
      localStorage.setItem('auth_token', response.token);
      
      // 验证手动存储
      const manualStoredToken = localStorage.getItem('auth_token');
      console.log('手动存储验证:', manualStoredToken ? '成功' : '失败');
      
      // 第三步：调用authStore的login方法
      console.log('调用authStore.login()...');
      login(response.token, response.user);
      
      // 第四步：最终验证
      const finalToken = localStorage.getItem('auth_token');
      console.log('最终验证 - localStorage中的令牌:', finalToken ? '存在' : '不存在');
      
      if (!finalToken) {
        throw new Error('令牌最终存储失败');
      }
      
      console.log('✅ 登录流程完成，准备跳转到仪表盘');
      
      // 短暂延迟确保状态更新
      setTimeout(() => {
        navigate('/dashboard');
      }, 100);
      
    } catch (error: any) {
      console.error('❌ 登录失败:', error);
      
      // 清理可能的残留数据
      localStorage.removeItem('auth_token');
      
      setError(error.message || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 flex items-center justify-center p-4">
      {/* 动态背景效果 */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-indigo-700/20 animate-pulse"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent animate-gradient-x"></div>
      
      {/* 浮动粒子效果 */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-white/20 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      <div className="max-w-md w-full relative z-10">
        {/* 登录卡片 */}
        <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-3xl">
          {/* Logo和标题 */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Package className="w-8 h-8 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-md">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
              </div>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Nova Quest</h1>
            <p className="text-gray-600 mt-3 text-lg">请登录您的账户</p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-6 p-4 bg-red-100/80 backdrop-blur-sm border border-red-300/50 rounded-xl shadow-sm">
              <p className="text-sm text-red-700 font-medium">{error}</p>
            </div>
          )}

          {/* 登录表单 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-3">
                用户名
              </label>
              <input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-4 py-3 bg-white/80 border border-gray-300/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-200 placeholder:text-gray-400 disabled:opacity-50"
                placeholder="请输入用户名"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-3">
                密码
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 bg-white/80 border border-gray-300/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-200 placeholder:text-gray-400 disabled:opacity-50 pr-12"
                  placeholder="请输入密码"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-blue-600 transition-colors duration-200 disabled:opacity-50"
                  disabled={loading}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium py-3 px-4 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <LogIn className="w-5 h-5" />
              )}
              <span className="text-base">{loading ? '登录中...' : '登录'}</span>
            </button>
          </form>


        </div>

        {/* 页脚信息 */}
        <div className="text-center mt-8 space-y-2">
          <p className="text-sm text-white/80 font-medium">
            © 2025 Nova Quest. 企业级库存管理解决方案
          </p>
          <p className="text-xs text-white/60">
            唐山肖川科技产品
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;