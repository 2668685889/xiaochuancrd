import { apiClient } from './client';

interface OperationLog {
  uuid: string;
  operation_type: string;
  operation_module: string;
  operation_description: string;
  target_uuid?: string;
  target_name?: string;
  operator_uuid: string;
  operator_name: string;
  operator_ip?: string;
  operation_status: string;
  error_message?: string;
  operation_time: string;
  created_at: string;
}

interface OperationLogsResponse {
  items: OperationLog[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

interface FilterParams {
  operation_type?: string;
  operation_module?: string;
  operator_name?: string;
  target_name?: string;
  operation_status?: string;
  start_date?: Date;
  end_date?: Date;
  page?: number;
  size?: number;
}

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

/**
 * 操作日志API服务
 */
export const operationLogApi = {
  /**
   * 获取操作日志列表
   */
  async getOperationLogs(params: FilterParams): Promise<ApiResponse<OperationLogsResponse>> {
    const queryParams = new URLSearchParams();
    
    // 添加筛选参数
    if (params.operation_type) queryParams.append('operation_type', params.operation_type);
    if (params.operation_module) queryParams.append('operation_module', params.operation_module);
    if (params.operator_name) queryParams.append('operator_name', params.operator_name);
    if (params.target_name) queryParams.append('target_name', params.target_name);
    if (params.operation_status) queryParams.append('operation_status', params.operation_status);
    if (params.start_date) queryParams.append('start_date', params.start_date.toISOString());
    if (params.end_date) queryParams.append('end_date', params.end_date.toISOString());
    
    // 添加分页参数
    queryParams.append('page', (params.page || 1).toString());
    queryParams.append('size', (params.size || 20).toString());
    
    return apiClient.request(`/api/v1/OperationLogs?${queryParams.toString()}`);
  },

  /**
   * 获取操作日志详情
   */
  async getOperationLog(logUuid: string): Promise<ApiResponse<OperationLog>> {
    return apiClient.request(`/api/v1/OperationLogs/${logUuid}`);
  },

  /**
   * 获取最近的操作日志
   */
  async getRecentOperationLogs(limit: number = 10): Promise<ApiResponse<OperationLog[]>> {
    return apiClient.request(`/api/v1/OperationLogs/Recent?limit=${limit}`);
  },

  /**
   * 获取操作日志统计信息
   */
  async getOperationLogStatistics(days: number = 30): Promise<ApiResponse<any>> {
    return apiClient.request(`/api/v1/OperationLogs/Statistics?days=${days}`);
  }
};