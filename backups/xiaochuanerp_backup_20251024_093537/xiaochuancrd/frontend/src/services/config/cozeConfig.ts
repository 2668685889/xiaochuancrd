/**
 * Coze配置服务
 * 用于管理Coze API地址和密钥的持久化存储
 */

interface CozeConfig {
  apiUrl: string;
  apiKey: string;
}

const CONFIG_KEY = 'coze_config';

/**
 * 获取Coze配置
 */
export const getCozeConfig = (): CozeConfig => {
  try {
    const configStr = localStorage.getItem(CONFIG_KEY);
    if (configStr) {
      return JSON.parse(configStr);
    }
  } catch (error) {
    console.error('获取Coze配置失败:', error);
  }
  
  // 返回默认配置
  return {
    apiUrl: 'https://api.coze.cn',
    apiKey: ''
  };
};

/**
 * 保存Coze配置
 */
export const saveCozeConfig = (config: CozeConfig): boolean => {
  try {
    localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
    return true;
  } catch (error) {
    console.error('保存Coze配置失败:', error);
    return false;
  }
};

/**
 * 清除Coze配置
 */
export const clearCozeConfig = (): boolean => {
  try {
    localStorage.removeItem(CONFIG_KEY);
    return true;
  } catch (error) {
    console.error('清除Coze配置失败:', error);
    return false;
  }
};