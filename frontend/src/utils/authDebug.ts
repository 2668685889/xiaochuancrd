/**
 * 认证调试工具
 * 用于诊断登录和令牌存储问题
 */

export class AuthDebugger {
  /**
   * 检查localStorage中的认证状态
   */
  static checkAuthStatus() {
    console.log('=== 认证状态诊断 ===');
    
    // 检查localStorage中的令牌
    const authToken = localStorage.getItem('auth_token');
    console.log('localStorage.auth_token:', authToken ? '存在 (' + authToken.substring(0, 20) + '...)' : '不存在');
    
    // 检查Zustand存储状态
    const authStorage = localStorage.getItem('auth-storage');
    console.log('Zustand auth-storage:', authStorage ? '存在' : '不存在');
    
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        console.log('Zustand状态:', {
          token: parsed.state.token ? '存在' : '不存在',
          isAuthenticated: parsed.state.isAuthenticated,
          user: parsed.state.user ? '存在' : '不存在'
        });
      } catch (e) {
        console.log('Zustand状态解析失败:', e);
      }
    }
    
    console.log('=== 诊断完成 ===');
  }
  
  /**
   * 清除所有认证相关存储
   */
  static clearAuthStorage() {
    console.log('=== 清除认证存储 ===');
    
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth-storage');
    
    console.log('已清除所有认证相关存储');
    console.log('=== 清除完成 ===');
  }
  
  /**
   * 手动设置令牌（用于测试）
   */
  static setAuthToken(token: string) {
    console.log('=== 手动设置令牌 ===');
    
    localStorage.setItem('auth_token', token);
    
    // 同时更新Zustand存储
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        parsed.state.token = token;
        parsed.state.isAuthenticated = true;
        localStorage.setItem('auth-storage', JSON.stringify(parsed));
      } catch (e) {
        console.log('更新Zustand存储失败:', e);
      }
    }
    
    console.log('令牌设置完成');
    console.log('=== 设置完成 ===');
  }
}

// 导出单例实例
export const authDebugger = new AuthDebugger();