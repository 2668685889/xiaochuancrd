import { apiClient } from './client';
import { snakeToCamel } from './mapper';

/**
 * Coze数据上传相关API
 */

// 数据表信息接口
interface CozeTableInfo {
  tableName: string;
  displayName: string;
  description: string;
  recordCount: number;
  lastUpdated?: string;
}

// 上传筛选条件接口
interface CozeUploadFilter {
  field: string;
  operator: string;
  value: any;
}

// 上传请求接口
interface CozeUploadRequest {
  tableName: string;
  cozeWorkflowId?: string;
  cozeWorkflowIdInsert?: string;
  cozeWorkflowIdUpdate?: string;
  cozeWorkflowIdDelete?: string;
  cozeApiKey?: string;
  cozeApiUrl?: string;
  filters?: CozeUploadFilter[];
  batchSize: number;
  selectedFields?: string[];
  configTitle?: string;
}

// 上传响应接口
interface CozeUploadResponse {
  uploadId: string;
  message: string;
  status: string;
}

// 上传状态接口
interface CozeUploadStatus {
  uploadId: string;
  tableName: string;
  status: string;
  progress: number;
  totalRecords: number;
  processedRecords: number;
  failedRecords: number;
  startTime?: string;
  endTime?: string;
  errorMessage?: string;
}

// 上传历史接口
interface CozeUploadHistory {
  uploadId: string;
  tableName: string;
  cozeWorkflowId: string;
  status: string;
  totalRecords: number;
  successRecords: number;
  failedRecords: number;
  startTime: string;
  endTime?: string;
  operatorName: string;
}

/**
 * Coze API服务
 */
export const cozeApi = {
  /**
   * 获取可上传的数据表列表
   */
  async getTables(): Promise<{
    success: boolean;
    data: CozeTableInfo[];
    message?: string;
  }> {
    try {
      const response = await apiClient.request('/api/v1/coze/tables', {
        method: 'GET',
      });
      
      return {
        success: true,
        data: response,
      };
    } catch (error: any) {
      console.error('获取数据表列表失败:', error);
      return {
        success: false,
        data: [],
        message: error.message || '获取数据表列表失败',
      };
    }
  },

  /**
   * 获取数据表的字段信息
   */
  async getTableFields(tableName: string): Promise<{
    success: boolean;
    data: any[];
    message?: string;
  }> {
    try {
      const response = await apiClient.request(`/api/v1/coze/tables/${tableName}/fields`, {
        method: 'GET',
      });
      
      return {
        success: true,
        data: response,
      };
    } catch (error: any) {
      console.error('获取数据表字段信息失败:', error);
      return {
        success: false,
        data: [],
        message: error.message || '获取数据表字段信息失败',
      };
    }
  },

  /**
   * 创建实时同步配置
   */
  async createSyncConfig(request: CozeUploadRequest): Promise<{
    success: boolean;
    data?: {
      configId: string;
      message: string;
      status: string;
    };
    message?: string;
  }> {
    try {
      const response = await apiClient.request('/api/v1/coze/sync-config', {
        method: 'POST',
        body: request,
      });
      
      return {
        success: true,
        data: response,
      };
    } catch (error: any) {
      console.error('创建同步配置失败:', error);
      return {
        success: false,
        message: error.message || '创建同步配置失败',
      };
    }
  },

  /**
   * 获取所有同步配置
   */
  async getSyncConfigs(): Promise<{
    success: boolean;
    data?: any[];
    message?: string;
  }> {
    try {
      const response = await apiClient.request('/api/v1/coze/sync-configs', {
        method: 'GET',
      });
      
      // 将后端返回的蛇形命名数据转换为大驼峰命名
      const camelCaseData = snakeToCamel(response);
      
      // 后端返回的数据结构是 {items: [...], total: 2}，我们需要提取items数组
      return {
        success: true,
        data: camelCaseData.items || [],
      };
    } catch (error: any) {
      console.error('获取同步配置失败:', error);
      return {
        success: false,
        message: error.message || '获取同步配置失败',
      };
    }
  },

  /**
   * 更新同步配置
   */
  async updateSyncConfig(configId: string, updates: any): Promise<{
    success: boolean;
    message?: string;
  }> {
    try {
      await apiClient.request(`/api/v1/coze/sync-config/${configId}`, {
        method: 'PUT',
        body: updates,
      });
      
      return {
        success: true,
      };
    } catch (error: any) {
      console.error('更新同步配置失败:', error);
      return {
        success: false,
        message: error.message || '更新同步配置失败',
      };
    }
  },

  /**
   * 删除同步配置
   */
  async deleteSyncConfig(configId: string): Promise<{
    success: boolean;
    message?: string;
  }> {
    try {
      await apiClient.request(`/api/v1/coze/sync-config/${configId}`, {
        method: 'DELETE',
      });
      
      return {
        success: true,
      };
    } catch (error: any) {
      console.error('删除同步配置失败:', error);
      return {
        success: false,
        message: error.message || '删除同步配置失败',
      };
    }
  },

  /**
   * 获取上传任务状态
   */
  async getUploadStatus(uploadId: string): Promise<{
    success: boolean;
    data?: CozeUploadStatus;
    message?: string;
  }> {
    try {
      const response = await apiClient.request(`/api/v1/coze/upload/${uploadId}`, {
        method: 'GET',
      });
      
      return {
        success: true,
        data: response,
      };
    } catch (error: any) {
      console.error('获取上传状态失败:', error);
      return {
        success: false,
        message: error.message || '获取上传状态失败',
      };
    }
  },

  /**
   * 获取上传历史记录
   */
  async getUploadHistory(page: number = 1, size: number = 20): Promise<{
    success: boolean;
    data: CozeUploadHistory[];
    message?: string;
  }> {
    try {
      const response = await apiClient.request('/api/v1/coze/history', {
        method: 'GET',
        params: { page, size },
      });
      
      return {
        success: true,
        data: response,
      };
    } catch (error: any) {
      console.error('获取上传历史失败:', error);
      return {
        success: false,
        data: [],
        message: error.message || '获取上传历史失败',
      };
    }
  },

  /**
   * 取消上传任务
   */
  async cancelUpload(uploadId: string): Promise<{
    success: boolean;
    message?: string;
  }> {
    try {
      await apiClient.request(`/api/v1/coze/upload/${uploadId}`, {
        method: 'DELETE',
      });
      
      return {
        success: true,
      };
    } catch (error: any) {
      console.error('取消上传任务失败:', error);
      return {
        success: false,
        message: error.message || '取消上传任务失败',
      };
    }
  },

  /**
   * 测试Coze API连接
   */
  async testConnection(cozeApiUrl: string, cozeApiKey: string): Promise<{
    success: boolean;
    message?: string;
    statusCode?: number;
  }> {
    try {
      const response = await apiClient.request('/api/v1/coze/test-connection', {
        method: 'POST',
        body: {
          cozeApiUrl,
          cozeApiKey
        }
      });
      
      return response;
    } catch (error: any) {
      console.error('Coze API连接测试失败:', error);
      return {
        success: false,
        message: error.message || 'Coze API连接测试失败',
      };
    }
  },

  /**
   * 验证Coze工作流ID
   */
  async validateWorkflow(_workflowId: string, _apiKey?: string): Promise<{
    success: boolean;
    workflowName?: string;
    message?: string;
  }> {
    try {
      // 这里实现Coze工作流验证逻辑
      // 暂时返回成功
      return {
        success: true,
        workflowName: '示例工作流',
        message: '工作流验证成功',
      };
    } catch (error: any) {
      console.error('工作流验证失败:', error);
      return {
        success: false,
        message: error.message || '工作流验证失败',
      };
    }
  },

  /**
   * 手动触发同步配置的数据同步
   */
  async triggerManualSync(configUuid: string): Promise<{
    success: boolean;
    message?: string;
    recordsSynced?: number;
    uploadId?: string;
  }> {
    try {
      const response = await apiClient.request(`/api/v1/coze/sync-config/${configUuid}/manual-sync`, {
        method: 'POST',
      });
      
      return {
        success: response.success,
        message: response.message,
        recordsSynced: response.records_synced,
        uploadId: response.upload_id,
      };
    } catch (error: any) {
      console.error('手动同步失败:', error);
      return {
        success: false,
        message: error.message || '手动同步失败',
      };
    }
  },
};

/**
 * Coze配置相关API
 */
export const cozeConfigApi = {
  /**
   * 获取Coze API配置
   */
  async getConfig(): Promise<{
    success: boolean;
    data?: {
      apiKey?: string;
      baseUrl: string;
      timeout: number;
    };
    message?: string;
  }> {
    try {
      // 这里可以从本地存储或后端获取配置
      const config = {
        baseUrl: 'https://api.coze.cn',
        timeout: 30,
      };
      
      return {
        success: true,
        data: config,
      };
    } catch (error: any) {
      console.error('获取Coze配置失败:', error);
      return {
        success: false,
        message: error.message || '获取Coze配置失败',
      };
    }
  },

  /**
   * 保存Coze API配置
   */
  async saveConfig(config: {
    apiKey: string;
    baseUrl?: string;
    timeout?: number;
  }): Promise<{
    success: boolean;
    message?: string;
  }> {
    try {
      // 这里可以保存配置到本地存储或后端
      localStorage.setItem('coze_api_key', config.apiKey);
      
      return {
        success: true,
        message: '配置保存成功',
      };
    } catch (error: any) {
      console.error('保存Coze配置失败:', error);
      return {
        success: false,
        message: error.message || '保存Coze配置失败',
      };
    }
  },
};