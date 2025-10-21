// MCP API 服务类
export class MCPApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = '/api/v1';
  }

  // 检查MCP服务状态
  async checkMCPStatus(): Promise<{ ready: boolean; message?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/smart-assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'ping',
          session_id: 'status-check'
        })
      });

      return {
        ready: response.ok,
        message: response.ok ? 'MCP服务正常运行' : 'MCP服务不可用'
      };
    } catch (error) {
      return {
        ready: false,
        message: 'MCP服务连接失败'
      };
    }
  }
}

// 创建全局实例
export const mcpApiService = new MCPApiService();