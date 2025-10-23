import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: any | null;
  isAuthenticated: boolean;
  login: (token: string, user: any) => void;
  logout: () => void;
  setUser: (user: any) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token: string, user: any) => {
    console.log('authStore.login() 被调用，令牌:', token ? token.substring(0, 20) + '...' : 'null');
    
    // 确保令牌不为空
    if (!token) {
      console.error('authStore.login() 错误: 令牌为空');
      throw new Error('登录令牌为空');
    }
    
    // 存储令牌到localStorage
    localStorage.setItem('auth_token', token);
    
    // 验证存储是否成功
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken !== token) {
      console.error('authStore.login() 错误: 令牌存储失败');
      throw new Error('令牌存储失败');
    }
    
    console.log('authStore.login() 成功: 令牌已存储到localStorage');
    
    // 更新状态
    set({ token, user, isAuthenticated: true });
  },
      logout: () => {
        localStorage.removeItem('auth_token');
        set({ token: null, user: null, isAuthenticated: false });
      },
      setUser: (user: any) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);