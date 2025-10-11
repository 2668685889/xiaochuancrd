import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, CheckCircle, XCircle, Key, Database } from 'lucide-react';
import { AuthDebugger } from '../utils/authDebug';

const AuthDebugPage: React.FC = () => {
  const navigate = useNavigate();
  const [authStatus, setAuthStatus] = useState<any>(null);
  const [testToken, setTestToken] = useState('');

  const checkAuthStatus = () => {
    console.log('=== 开始检查认证状态 ===');
    
    const status = {
      localStorageAuthToken: localStorage.getItem('auth_token'),
      authStorage: localStorage.getItem('auth-storage'),
      timestamp: new Date().toISOString()
    };
    
    setAuthStatus(status);
    
    console.log('认证状态:', status);
    console.log('=== 检查完成 ===');
  };

  const clearAuthStorage = () => {
    AuthDebugger.clearAuthStorage();
    setAuthStatus(null);
    alert('认证存储已清除，请重新登录');
  };

  const setManualToken = () => {
    if (!testToken.trim()) {
      alert('请输入有效的JWT令牌');
      return;
    }
    
    AuthDebugger.setAuthToken(testToken);
    setTestToken('');
    checkAuthStatus();
    alert('令牌已手动设置，请测试API调用');
  };

  const testApiCall = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        alert('没有找到有效的令牌，请先设置令牌');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/coze/tables', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        alert(`API调用成功！返回数据表数量: ${data.length}`);
        console.log('API调用成功:', data);
      } else {
        alert(`API调用失败: ${response.status} ${response.statusText}`);
        console.error('API调用失败:', response);
      }
    } catch (error) {
      alert('API调用异常: ' + error);
      console.error('API调用异常:', error);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Key className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">认证调试工具</h1>
          </div>

          {/* 当前状态 */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-3">当前认证状态</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              {authStatus ? (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    {authStatus.localStorageAuthToken ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-600" />
                    )}
                    <span>localStorage.auth_token: {authStatus.localStorageAuthToken ? '存在' : '不存在'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {authStatus.authStorage ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-600" />
                    )}
                    <span>Zustand auth-storage: {authStatus.authStorage ? '存在' : '不存在'}</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    检查时间: {authStatus.timestamp}
                  </div>
                </div>
              ) : (
                <div className="text-gray-500">点击刷新按钮检查状态</div>
              )}
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <button
              onClick={checkAuthStatus}
              className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>刷新状态</span>
            </button>
            
            <button
              onClick={clearAuthStorage}
              className="flex items-center justify-center space-x-2 bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 transition-colors"
            >
              <Database className="w-4 h-4" />
              <span>清除存储</span>
            </button>
          </div>

          {/* 手动设置令牌 */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-3">手动设置令牌</h2>
            <div className="space-y-3">
              <textarea
                value={testToken}
                onChange={(e) => setTestToken(e.target.value)}
                placeholder="粘贴JWT令牌到这里..."
                className="w-full h-20 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={setManualToken}
                className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors"
              >
                设置令牌
              </button>
            </div>
          </div>

          {/* API测试 */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-3">API调用测试</h2>
            <button
              onClick={testApiCall}
              className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors"
            >
              测试Coze API调用
            </button>
          </div>

          {/* 说明 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 mb-2">使用说明</h3>
            <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
              <li>首先尝试正常登录流程</li>
              <li>如果登录后localStorage为空，使用"手动设置令牌"功能</li>
              <li>使用"测试API调用"验证令牌是否有效</li>
              <li>如果问题持续存在，使用"清除存储"后重新登录</li>
            </ol>
          </div>
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate('/login')}
            className="text-blue-600 hover:text-blue-800 underline"
          >
            返回登录页面
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthDebugPage;