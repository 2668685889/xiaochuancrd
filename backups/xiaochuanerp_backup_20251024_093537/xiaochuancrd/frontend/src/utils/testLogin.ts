/**
 * 登录流程测试工具
 * 用于验证登录流程中的令牌存储机制
 */

import { apiClient } from '../services/api/client';
import { cozeApi } from '../services/api/coze';
import { useAuthStore } from '../stores/authStore';

/**
 * 测试登录流程
 */
export async function testLoginProcess(username: string, password: string) {
  console.log('🔍 开始测试登录流程...');
  console.log('测试账号:', username);
  
  try {
    // 1. 清理之前的认证数据
    console.log('1. 清理之前的认证数据...');
    localStorage.removeItem('auth_token');
    
    // 2. 调用登录API
    console.log('2. 调用登录API...');
    const response = await apiClient.login({ username, password });
    
    console.log('✅ API调用成功');
    console.log('令牌长度:', response.token.length);
    console.log('令牌前20位:', response.token.substring(0, 20) + '...');
    
    // 3. 手动存储令牌
    console.log('3. 手动存储令牌到localStorage...');
    localStorage.setItem('auth_token', response.token);
    
    // 验证手动存储
    const manualToken = localStorage.getItem('auth_token');
    console.log('手动存储验证:', manualToken ? '✅ 成功' : '❌ 失败');
    
    // 4. 使用authStore存储
    console.log('4. 使用authStore存储...');
    const authStore = useAuthStore.getState();
    authStore.login(response.token, response.user);
    
    // 5. 最终验证
    console.log('5. 最终验证...');
    const finalToken = localStorage.getItem('auth_token');
    const authState = useAuthStore.getState();
    
    console.log('localStorage令牌:', finalToken ? '✅ 存在' : '❌ 不存在');
    console.log('authStore状态:', authState.isAuthenticated ? '✅ 已认证' : '❌ 未认证');
    
    if (finalToken && authState.isAuthenticated) {
      console.log('🎉 登录流程测试通过！');
      return {
        success: true,
        token: finalToken,
        user: authState.user
      };
    } else {
      console.log('❌ 登录流程测试失败');
      return {
        success: false,
        error: '令牌存储或状态更新失败'
      };
    }
    
  } catch (error: any) {
    console.error('❌ 登录流程测试失败:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 测试API调用
 */
export async function testApiCall() {
  console.log('🔍 测试API调用...');
  
  try {
    const token = localStorage.getItem('auth_token');
    console.log('当前令牌:', token ? token.substring(0, 20) + '...' : 'null');
    
    // 测试Coze API
    const response = await cozeApi.getTables();
    console.log('✅ API调用成功');
    console.log('返回数据条数:', response.data ? response.data.length : 0);
    
    return {
      success: response.success,
      data: response.data
    };
    
  } catch (error: any) {
    console.error('❌ API调用失败:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 完整测试流程
 */
export async function runFullTest() {
  console.log('🚀 开始完整测试流程...\n');
  
  // 测试登录
  const loginResult = await testLoginProcess('admin', 'admin123');
  
  if (loginResult.success) {
    console.log('\n--- API调用测试 ---');
    // 测试API调用
    const apiResult = await testApiCall();
    
    if (apiResult.success) {
      console.log('\n🎉 完整测试通过！系统工作正常。');
    } else {
      console.log('\n❌ API调用测试失败');
    }
  } else {
    console.log('\n❌ 登录测试失败');
  }
}

// 导出测试函数
if (typeof window !== 'undefined') {
  // 在浏览器环境中暴露到全局对象
  (window as any).testLoginProcess = testLoginProcess;
  (window as any).testApiCall = testApiCall;
  (window as any).runFullTest = runFullTest;
}