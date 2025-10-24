import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ChatContainer } from '../components/ui/chat-container';
import SettingsDialog from '../components/smart-assistant/SettingsDialog';
import { Database, Bot, MessageSquare, Settings, Search, Shield, Loader2, Activity } from 'lucide-react';

// API服务 - 使用本地后端服务，无需Docker环境
const API_BASE_URL = '/api/v1';

// MCP智能助手配置状态
const mcpConfig = {
  database: {
    host: 'localhost',
    port: 3306,
    database: 'xiaochuanerp',
    username: 'root',
    password: 'password'
  },
  model: {
    modelId: 'mcp-assistant',
    modelName: 'MCP智能助手'
  },
  rag: {
    tables: [],
    enabled: false
  }
};

// 检查MCP服务状态 - 现在使用本地集成服务
const checkMCPStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/smart-assistant/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: 'test',
        session_id: 'test_session'
      })
    });
    return { ready: response.ok, status: response.status };
  } catch (error) {
    console.log('MCP本地集成服务检查失败:', error);
    return { ready: false, status: 0 };
  }
};



interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'sql' | 'chart' | 'table';
}

interface ChatSession {
  id: string;
  name: string;
  createdAt: Date;
  lastMessage?: string;
  messageCount: number;
}

const SmartAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '您好！我是MCP智能助手，可以帮您查询产品、销售、采购、库存等数据。请告诉我您想了解什么？',
      role: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConfigLoading, setIsConfigLoading] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  // MCP服务状态
  const [mcpReady, setMCPReady] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [initError, setInitError] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [sessionsOpen, setSessionsOpen] = useState(false);
  
  // 生成唯一会话ID - 使用useCallback优化
  const generateSessionId = useCallback(() => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // 创建新会话 - 使用useCallback优化
  const createNewSession = useCallback(() => {
    const newSessionId = generateSessionId();
    const newSession: ChatSession = {
      id: newSessionId,
      name: `新对话 ${new Date().toLocaleTimeString()}`,
      createdAt: new Date(),
      messageCount: 0
    };
    
    setChatSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSessionId);
    setMessages([
      {
        id: '1',
        content: '您好！我是MCP智能助手，可以帮您查询产品、销售、采购、库存等数据。请告诉我您想了解什么？',
        role: 'assistant',
        timestamp: new Date()
      }
    ]);
    setSessionsOpen(false);
    
    // 保存会话到localStorage
    localStorage.setItem('smartAssistant_currentSessionId', newSessionId);
    localStorage.setItem('smartAssistant_chatSessions', JSON.stringify([newSession, ...chatSessions]));
  }, [generateSessionId, chatSessions]);

  // 切换会话 - 使用useCallback优化
  const switchSession = useCallback((sessionId: string) => {
    const session = chatSessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSessionId(sessionId);
      setMessages([
        {
          id: '1',
          content: '您好！我是MCP智能助手，可以帮您查询产品、销售、采购、库存等数据。请告诉我您想了解什么？',
          role: 'assistant',
          timestamp: new Date()
        }
      ]);
      setSessionsOpen(false);
      
      // 保存当前会话到localStorage
      localStorage.setItem('smartAssistant_currentSessionId', sessionId);
    }
  }, [chatSessions]);

  // 删除会话 - 使用useCallback优化
  const deleteSession = useCallback((sessionId: string) => {
    const updatedSessions = chatSessions.filter(s => s.id !== sessionId);
    setChatSessions(updatedSessions);
    
    if (currentSessionId === sessionId) {
      if (updatedSessions.length > 0) {
        switchSession(updatedSessions[0].id);
      } else {
        createNewSession();
      }
    }
    
    // 更新localStorage
    localStorage.setItem('smartAssistant_chatSessions', JSON.stringify(updatedSessions));
  }, [chatSessions, currentSessionId, switchSession, createNewSession]);

  // 初始化会话
  useEffect(() => {
    const savedCurrentSessionId = localStorage.getItem('smartAssistant_currentSessionId');
    const savedChatSessions = localStorage.getItem('smartAssistant_chatSessions');
    
    if (savedChatSessions) {
      try {
        const sessions = JSON.parse(savedChatSessions);
        // 确保createdAt字段被正确转换为Date对象
        const processedSessions = sessions.map((session: any) => ({
          ...session,
          createdAt: new Date(session.createdAt)
        }));
        setChatSessions(processedSessions);
        
        if (savedCurrentSessionId && processedSessions.some((s: ChatSession) => s.id === savedCurrentSessionId)) {
          setCurrentSessionId(savedCurrentSessionId);
        } else if (processedSessions.length > 0) {
          setCurrentSessionId(processedSessions[0].id);
        } else {
          createNewSession();
        }
      } catch (error) {
        console.error('解析保存的会话数据失败:', error);
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, []);
  
  // MCP核心功能配置状态 - 使用真实API数据
  const [databaseConfig, setDatabaseConfig] = useState({
    selectedDatabase: 'xiaochuanERP',
    connectionStatus: 'connected',
    databases: [
      { 
        id: 'xiaochuanERP', 
        name: '小川ERP主数据库', 
        type: 'mysql', 
        host: 'localhost',
        port: 3306,
        database: 'xiaochuanERP',
        username: 'root',
        password: 'Xiaochuan123!', // 设置正确的数据库密码
        status: 'connected' 
      }
    ]
  });
  
  const [modelConfig, setModelConfig] = useState({
    selectedModel: '',
    provider: '',
    models: [
      // 阿里云百炼模型
      { 
        id: 'qwen-max', 
        name: '通义千问 Max', 
        provider: 'aliyun', 
        status: 'available', 
        cost: 'medium', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        apiKey: ''
      },
      { 
        id: 'qwen-plus', 
        name: '通义千问 Plus', 
        provider: 'aliyun', 
        status: 'available', 
        cost: 'medium', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        apiKey: ''
      },
      
      // 千帆大模型
      { 
        id: 'ernie-x1-turbo-32k', 
        name: '文心一言 X1 Turbo', 
        provider: 'baidu', 
        status: 'available', 
        cost: 'medium', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'https://qianfan.baidubce.com/v2/',
        apiKey: ''
      },
      
      // DeepSeek模型
      { 
        id: 'deepseek-chat', 
        name: 'DeepSeek Chat', 
        provider: 'deepseek', 
        status: 'available', 
        cost: 'low', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'api.deepseek.com',
        baseUrl: 'https://api.deepseek.com/v1',
        apiKey: ''
      },
      
      // 腾讯混元模型
      { 
        id: 'hunyuan-standard-256K', 
        name: '腾讯混元 Standard 256K', 
        provider: 'tencent', 
        status: 'available', 
        cost: 'medium', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'https://api.hunyuan.cloud.tencent.com/v1/',
        apiKey: ''
      },
      
      // 讯飞星火模型
      { 
        id: '4.0Ultra', 
        name: '讯飞星火 4.0 Ultra', 
        provider: 'iflytek', 
        status: 'available', 
        cost: 'high', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'https://spark-api-open.xf-yun.com/v1/',
        apiKey: ''
      },
      
      // Kimi模型
      { 
        id: 'kimi-k2-0711-preview', 
        name: 'Kimi K2 0711 Preview', 
        provider: 'kimi', 
        status: 'available', 
        cost: 'medium', 
        capabilities: ['text-to-sql', 'rag', 'data-analysis'],
        apiDomain: 'https://api.moonshot.cn/v1',
        apiKey: ''
      }
    ]
  });
  

  

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部 - 使用useCallback优化
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // 加载保存的设置信息
  const loadSavedSettings = async () => {
    try {
      const response = await fetch('/api/v1/smart-assistant/settings', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        
        if (result.success && result.data.is_configured) {
          const { ai_model_config, database_config } = result.data;
          
          // 更新数据库配置
      setDatabaseConfig(prev => ({
        ...prev,
        databases: [{
          id: 'xiaochuanERP',
          name: '小川ERP主数据库',
          type: 'mysql',
          host: database_config.host,
          port: database_config.port,
          database: database_config.database,
          username: database_config.username,
          password: database_config.password,
          schemaName: database_config.schema_name || '',
          status: 'connected'
        }]
      }));
      
      // 更新模型配置
      setModelConfig(prev => ({
        ...prev,
        selectedModel: ai_model_config.model_id,
        models: prev.models.map(model => 
          model.id === ai_model_config.model_id 
            ? { 
                ...model, 
                apiKey: ai_model_config.api_key,
                apiDomain: ai_model_config.api_domain,
                baseUrl: ai_model_config.base_url || '',
                prompt: ai_model_config.prompt || ''
              }
            : model
        )
      }));
          
          console.log('已加载保存的设置信息');
        } else {
          console.log('未找到保存的设置信息，使用默认配置');
        }
      }
    } catch (error) {
      console.error('加载保存的设置信息失败:', error);
      throw error; // 重新抛出错误以便在初始化中处理
    }
  };

  // 重试初始化 - 使用useCallback优化
  const retryInitialization = useCallback(async () => {
    try {
      setIsInitializing(true);
      setInitError(null);
      
      // 重新检查MCP状态
      const mcpStatusResult = await checkMCPStatus();
      setMCPReady(mcpStatusResult.ready);
      
      if (!mcpStatusResult.ready) {
        setInitError('MCP服务仍未就绪，请检查后端服务是否正常运行');
      }
    } catch (error) {
      console.error('重试初始化失败:', error);
      setInitError('重试初始化失败，请稍后再试');
    } finally {
      setIsInitializing(false);
    }
  }, []);

  // 页面初始化 - 合并所有初始化逻辑到一个useEffect中
  useEffect(() => {
    const initializePage = async () => {
      try {
        setIsInitializing(true);
        setInitError(null);
        
        // 并行执行所有初始化操作
        const [settingsResult, mcpStatusResult] = await Promise.allSettled([
          loadSavedSettings(),
          checkMCPStatus()
        ]);
        
        // 处理设置加载结果
        if (settingsResult.status === 'rejected') {
          console.error('加载设置失败:', settingsResult.reason);
          // 不阻止页面继续加载，使用默认设置
        }
        
        // 处理MCP状态检查结果
        if (mcpStatusResult.status === 'fulfilled') {
          setMCPReady(mcpStatusResult.value.ready);
          if (!mcpStatusResult.value.ready) {
            console.warn('MCP服务未就绪:', mcpStatusResult.value.message);
          }
        } else {
          console.error('MCP状态检查失败:', mcpStatusResult.reason);
          setMCPReady(false);
        }
        
        // 设置默认MCP配置（如果设置加载失败）
        if (settingsResult.status === 'rejected') {
          console.log('使用MCP智能助手默认配置:', mcpConfig);
          
          // 设置数据库配置
          setDatabaseConfig({
            selectedDatabase: 'xiaochuanERP',
            connectionStatus: 'connected',
            databases: [{
              id: 'xiaochuanERP',
              name: '小川ERP主数据库',
              type: 'mysql',
              host: mcpConfig.database.host,
              port: mcpConfig.database.port,
              database: mcpConfig.database.database,
              username: mcpConfig.database.username,
              password: mcpConfig.database.password,
              schemaName: '',
              status: 'connected'
            }]
          });
          
          // 设置模型配置 - 使用DeepSeek作为默认模型
          setModelConfig({
            selectedModel: 'deepseek-chat',
            provider: 'deepseek',
            models: [{
              id: 'deepseek-chat',
              name: 'DeepSeek Chat',
              provider: 'deepseek',
              status: 'available',
              cost: 'low',
              capabilities: ['text-to-sql', 'rag', 'data-analysis'],
              apiDomain: 'api.deepseek.com',
              baseUrl: 'https://api.deepseek.com/v1',
              apiKey: '您的DeepSeek_API密钥' // 需要用户配置
            }]
          });
        }
        
        // 完成配置加载
        setIsConfigLoading(false);
      } catch (error) {
        console.error('页面初始化失败:', error);
        setInitError('页面初始化失败，请刷新页面重试');
        setIsConfigLoading(false);
      } finally {
        setIsInitializing(false);
      }
    };
    
    initializePage();
  }, []);

  // 定期检查MCP状态
  useEffect(() => {
    if (isInitializing) return; // 初始化期间不执行定期检查
    
    const checkStatusInterval = setInterval(async () => {
      try {
        const mcpStatusResult = await checkMCPStatus();
        // 只有当状态发生变化时才更新
        if (mcpStatusResult.ready !== mcpReady) {
          setMCPReady(mcpStatusResult.ready);
          if (mcpStatusResult.ready) {
            console.log('MCP服务已恢复');
          }
        }
      } catch (error) {
        console.error('定期MCP状态检查失败:', error);
      }
    }, 30000); // 每30秒检查一次
    
    return () => clearInterval(checkStatusInterval);
  }, [isInitializing, mcpReady]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 将表格数据转换为纯文本键值对列表格式
  const convertToTextListFormat = (rawContent: string): string => {
    try {
      console.log('开始转换表格数据为纯文本键值对列表格式');
      console.log('原始内容:', rawContent);
      
      // 提取查询结果部分 - 支持多种格式
      let queryResultMatch = rawContent.match(/查询结果\s*\(\d+\s*条记录\):([\s\S]*?)(?=\n\n|\n$|$)/);
      
      // 如果没有找到标准格式，尝试另一种格式
      if (!queryResultMatch) {
        queryResultMatch = rawContent.match(/总记录数：\d+\s*条\n\n([\s\S]*?)(?=\n\n|\n$|$)/);
      }
      
      // 如果还是没有找到，直接查找表格部分
      if (!queryResultMatch) {
        // 查找表格开始位置 - 更灵活的匹配方式
        const tableStartIndex = rawContent.indexOf('|');
        if (tableStartIndex !== -1) {
          // 查找第一个包含|的行作为表头
          const lines = rawContent.split('\n');
          let headerLineIndex = -1;
          
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line.includes('|') && !line.includes('---') && line.split('|').filter(cell => cell.trim()).length > 1) {
              headerLineIndex = i;
              break;
            }
          }
          
          if (headerLineIndex !== -1) {
            // 从表头开始到下一个空行或文件末尾
            let tableEndIndex = lines.length;
            for (let i = headerLineIndex + 1; i < lines.length; i++) {
              if (lines[i].trim() === '') {
                tableEndIndex = i;
                break;
              }
            }
            
            const tableSection = lines.slice(headerLineIndex, tableEndIndex).join('\n');
            queryResultMatch = [null, tableSection];
          }
        }
      }
      
      if (!queryResultMatch) {
        console.log('未找到查询结果部分，返回原始内容');
        return rawContent; // 如果没有找到查询结果，返回原始内容
      }
      
      const tableSection = queryResultMatch[1];
      const lines = tableSection.split('\n').filter(line => line.trim());
      
      // 提取表头和数据行
      const headerLine = lines.find(line => line.includes('|') && !line.includes('---'));
      if (!headerLine) {
        console.log('未找到表头行，返回原始内容');
        return rawContent;
      }
      
      const headers = headerLine.split('|').map(h => h.trim()).filter(h => h);
      console.log('提取的表头:', headers);
      
      // 提取数据行（跳过表头行和分隔线）
      const dataRows = lines.filter(line => 
        line.includes('|') && 
        !line.includes('---') && 
        line !== headerLine
      ).map(line => 
        line.split('|').map(cell => cell.trim()).filter(cell => cell)
      ).filter(row => row.length > 0 && row.length === headers.length);
      
      console.log('提取的数据行:', dataRows);
      
      // 构建纯文本键值对格式
      const currentTime = new Date().toLocaleString('zh-CN');
      let formattedText = `好的，已切换为纯文本模式显示模拟的商品数据库内容。\n\n---\n\n**商品数据库查询结果**\n\n`;
      formattedText += `**查询时间**：${currentTime}\n`;
      formattedText += `**总记录数**：${dataRows.length} 条\n\n---\n`;
      
      // 字段映射（将数据库字段名转换为友好名称）
      const fieldMapping: Record<string, string> = {
        'uuid': '商品ID',
        'product_code': '商品编码',
        '产品编码': '商品编码',
        'product_name': '商品名称',
        '产品名称': '商品名称',
        'current_quantity': '当前库存',
        '当前库存': '库存',
        'min_quantity': '最低库存',
        '最低库存': '最低库存',
        'max_quantity': '最高库存',
        '最高库存': '最高库存',
        'category_name': '分类',
        '产品分类': '分类',
        'product_model': '产品型号',
        '产品型号': '产品型号',
        'supplier_name': '供应商',
        '供应商': '供应商',
        'unit_price': '价格（元）',
        '单价': '价格',
        '价格（元）': '价格',
        'is_active': '库存状态',
        '库存状态': '状态',
        'order_date': '上架时间',
        '上架时间': '上架时间'
      };
      
      // 为每个记录构建纯文本键值对格式
      dataRows.forEach((row, index) => {
        formattedText += `\n**记录 ${index + 1}**\n`;
        
        headers.forEach((header, headerIndex) => {
          if (headerIndex < row.length) {
            const friendlyHeader = fieldMapping[header] || header;
            let cellValue = row[headerIndex];
            
            // 处理特殊值
            if (cellValue === 'None' || cellValue === 'null' || cellValue === '') {
              cellValue = '-';
            }
            
            // 格式化数值
            if (cellValue && !isNaN(Number(cellValue))) {
              if (cellValue.includes('.')) {
                cellValue = Number(cellValue).toLocaleString('zh-CN', { 
                  minimumFractionDigits: 2, 
                  maximumFractionDigits: 2 
                }) + ' 元';
              } else {
                cellValue = Number(cellValue).toLocaleString('zh-CN');
              }
            }
            
            // 处理状态字段
            if (header === '库存状态' || friendlyHeader === '状态') {
              // 保留原始状态显示，如🟢 充足、🔴 不足等
              if (cellValue.includes('🟢') || cellValue.includes('🔴') || cellValue.includes('🟡')) {
                // 保持原始状态显示
              } else if (cellValue === '1' || cellValue === '销售中') {
                cellValue = '🟢 销售中';
              } else if (cellValue === '0' || cellValue === '已下架') {
                cellValue = '🔴 已下架';
              } else if (cellValue === '缺货') {
                cellValue = '🔴 缺货';
              }
            }
            
            // 处理日期字段
            if (header === 'order_date' || header === '上架时间' || friendlyHeader === '上架时间') {
              if (cellValue && cellValue !== '-') {
                // 简化日期格式，只显示年月日
                const date = new Date(cellValue);
                if (!isNaN(date.getTime())) {
                  cellValue = date.toLocaleDateString('zh-CN');
                }
              }
            }
            
            formattedText += `- ${friendlyHeader}：${cellValue}\n`;
          }
        });
      });
      
      formattedText += '\n---\n\n以上为模拟数据。如果您需要按特定条件（如分类、价格、库存等）进行查询，请随时告诉我。';
      console.log('格式化后的文本:', formattedText);
      return formattedText;
      
    } catch (error) {
      console.error('转换表格数据为纯文本键值对列表格式失败:', error);
      return rawContent;
    }
  };

  // 格式化Markdown数据，将MCP返回的数据转换为用户要求的Markdown格式
  const formatMarkdownData = (content: string): string => {
    // 检查内容是否包含表格格式
    if (!content.includes('查询结果') || !content.includes('|') || !content.includes('---')) {
      return content; // 如果不是表格格式，直接返回原内容
    }

    try {
      // 提取表格数据
      const lines = content.split('\n');
      const tableStartIndex = lines.findIndex(line => line.includes('查询结果'));
      if (tableStartIndex === -1) return content;

      // 找到表格开始位置（表头）
      let headerIndex = -1;
      for (let i = tableStartIndex; i < lines.length; i++) {
        if (lines[i].includes('|') && lines[i + 1] && lines[i + 1].includes('---')) {
          headerIndex = i;
          break;
        }
      }

      if (headerIndex === -1) return content;

      // 解析表头
      const headerLine = lines[headerIndex];
      const headers = headerLine.split('|').map(h => h.trim()).filter(h => h);

      // 解析数据行
      const dataRows = [];
      for (let i = headerIndex + 2; i < lines.length; i++) {
        if (lines[i].includes('|')) {
          const row = lines[i].split('|').map(cell => cell.trim()).filter(cell => cell);
          if (row.length === headers.length) {
            dataRows.push(row);
          }
        } else if (lines[i].trim() === '') {
          // 空行可能是表格结束
          break;
        }
      }

      // 字段映射（英文到中文）
      const fieldMapping: { [key: string]: string } = {
        'id': '商品ID',
        'product_id': '商品ID',
        'product_name': '商品名称',
        'name': '商品名称',
        'category': '分类',
        'price': '价格',
        'stock': '库存',
        'created_at': '上架时间',
        'status': '状态',
        'description': '描述'
      };

      // 状态映射
      const statusMapping: { [key: string]: string } = {
        'active': '销售中',
        'inactive': '下架',
        'out_of_stock': '缺货',
        'in_stock': '有货'
      };

      // 构建Markdown格式内容
      let markdownContent = "好的，已切换为纯文本模式显示模拟的商品数据库内容。\n\n---\n\n**商品数据库查询结果**\n\n";
      
      // 添加查询时间
      const now = new Date();
      markdownContent += `**查询时间**：${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}\n`;
      
      // 添加总记录数
      markdownContent += `**总记录数**：${dataRows.length} 条\n\n---\n`;

      // 添加每条记录
      dataRows.forEach((row, index) => {
        markdownContent += `\n**记录 ${index + 1}**\n`;
        
        headers.forEach((header, headerIndex) => {
          const fieldName = fieldMapping[header.toLowerCase()] || header;
          let value = row[headerIndex];
          
          // 处理特殊值
          if (value === 'None' || value === 'null' || value === '') {
            value = '-';
          }
          
          // 处理价格字段
          if (header.toLowerCase().includes('price') && value !== '-') {
            const numValue = parseFloat(value);
            if (!isNaN(numValue)) {
              value = `${numValue.toFixed(2)} 元`;
            }
          }
          
          // 处理状态字段
          if (header.toLowerCase().includes('status') && value !== '-') {
            value = statusMapping[value.toLowerCase()] || value;
          }
          
          // 处理日期字段
          if (header.toLowerCase().includes('created_at') && value !== '-') {
            try {
              const date = new Date(value);
              if (!isNaN(date.getTime())) {
                value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
              }
            } catch (e) {
              // 保留原始值
            }
          }
          
          markdownContent += `- ${fieldName}：${value}\n`;
        });
      });
      
      markdownContent += "\n---\n\n以上为模拟数据。如果您需要按特定条件（如分类、价格、库存等）进行查询，请随时告诉我。";
      
      return markdownContent;
    } catch (error) {
      console.error('格式化Markdown数据时出错:', error);
      return content; // 出错时返回原内容
    }
  };

  // 格式化表格数据为表格显示格式（优化中文显示）
  const formatTableData = (rawContent: string): string => {
    try {
      console.log('原始数据内容:', rawContent); // 调试日志
      
      // 修改检测逻辑：检查是否包含表格格式的关键标识
      if (rawContent.includes('查询结果') && rawContent.includes('|') && rawContent.includes('---')) {
        // 这是MCP服务返回的完整格式，现在转换为纯文本列表格式
        console.log('检测到MCP服务完整格式，转换为纯文本列表格式');
        return convertToTextListFormat(rawContent);
      }
      
      // 检查是否是直接返回的Markdown表格格式
      if (rawContent.includes('|') && rawContent.includes('---')) {
        console.log('检测到Markdown表格格式，转换为纯文本列表格式');
        return convertToTextListFormat(rawContent);
      }
      
      // 对于其他格式，使用原有的解析逻辑
      let tableMatch = rawContent.match(/\*\*查询结果\*\*:\s*\n\n([\s\S]*?)(?=\n\n|\n$|$)/);
      
      if (!tableMatch) {
        tableMatch = rawContent.match(/查询结果\s*\(\d+\s*条记录\):([\s\S]*?)(?=\n\n|\n$|$)/);
      }
      
      if (!tableMatch) {
        tableMatch = rawContent.match(/查询结果\s*\(\d+\s*条记录\):\s*\n([\s\S]*?)(?=\n\n|\n$|$)/);
      }
      
      if (!tableMatch) {
        return formatQueryResult(rawContent); // 如果没有找到表格，使用通用格式化
      }
      
      let tableSection = tableMatch[1];
      tableSection = tableSection.replace(/\.\.\.\s*\(显示前\d+条，共\d+条记录\)/g, '');
      
      const lines = tableSection.split('\n').filter(line => line.trim());
      const dataLines = lines.filter(line => !line.includes('---') && line.trim());
      
      if (dataLines.length === 0) {
        return "未找到查询结果数据";
      }
      
      const headerLine = dataLines[0];
      const headers = headerLine.split('|').map(h => h.trim()).filter(h => h);
      const dataRows = dataLines.slice(1).map(line => {
        return line.split('|').map(cell => cell.trim()).filter(cell => cell);
      }).filter(row => row.length > 0 && row.length === headers.length);
      
      const currentTime = new Date().toLocaleString('zh-CN');
      let formattedTable = `📦 商品数据库查询结果\n`;
      formattedTable += `查询时间：${currentTime}\n`;
      formattedTable += `总记录数：${dataRows.length} 条\n\n`;
      
      const friendlyHeaders = headers.map(header => {
        const headerMap: Record<string, string> = {
          'uuid': '商品ID',
          'product_name': '商品名称',
          'product_code': '商品编码',
          'current_quantity': '库存',
          'unit_price': '价格（元）',
          'supplier_uuid': '供应商',
          'category_name': '分类',
          'customer_name': '客户名称',
          'order_date': '上架时间',
          'total_amount': '总金额',
          'quantity': '数量',
          'status': '状态'
        };
        return headerMap[header] || header;
      });
      
      formattedTable += friendlyHeaders.join('\t\t') + '\n';
      
      dataRows.forEach((row) => {
        const formattedRow = row.map((cell, cellIndex) => {
          if (cell && !isNaN(Number(cell)) && cell.includes('.')) {
            return Number(cell).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
          } else if (cell && !isNaN(Number(cell))) {
            return Number(cell).toLocaleString('zh-CN');
          }
          
          if (cell === 'None' || cell === 'null' || cell === '') {
            return '-';
          }
          
          if (cell && cell.length === 36 && cell.includes('-')) {
            return cell.substring(0, 8) + '...';
          }
          
          return cell;
        });
        
        formattedTable += formattedRow.join('\t\t') + '\n';
      });
      
      return formattedTable;
    } catch (error) {
      console.error('格式化表格数据失败:', error);
      return formatQueryResult(rawContent); // 出错时使用通用格式化
    }
  };
  
  // 将Markdown表格转换为纯文本格式
  const convertTableToText = (tableContent: string): string => {
    try {
      const lines = tableContent.split('\n').filter(line => line.trim());
      if (lines.length < 3) return tableContent; // 不是完整表格
      
      // 提取表头
      const headers = lines[0].split('|').filter(h => h.trim()).map(h => h.trim());
      const separatorLine = lines[1];
      
      // 提取数据行
      const dataRows = lines.slice(2);
      
      let result = '**商品数据库查询结果**\n\n';
      result += `**查询时间**：${new Date().toLocaleString('zh-CN')}\n`;
      result += `**总记录数**：${dataRows.length} 条\n\n`;
      result += '---\n\n';
      
      // 智能字段名称转换函数
      const convertFieldName = (fieldName: string): string => {
        // 常见的数据库字段名模式转换
        const patterns: Record<string, string> = {
          // 商品相关字段
          'product_name': '商品名称',
          'product_code': '商品编码',
          'current_quantity': '当前库存',
          'min_quantity': '最低库存',
          'max_quantity': '最高库存',
          'unit_price': '单价',
          
          // 订单相关字段
          'order_number': '订单编号',
          'customer_name': '客户名称',
          'total_amount': '总金额',
          'status': '状态',
          'order_date': '订单日期',
          'expected_delivery_date': '预计交货日期',
          
          // 通用字段
          'uuid': '唯一标识',
          'id': 'ID',
          'name': '名称',
          'code': '编码',
          'quantity': '数量',
          'price': '价格',
          'amount': '金额',
          'date': '日期',
          'time': '时间',
          'description': '描述',
          'created_at': '创建时间',
          'updated_at': '更新时间',
          'category_name': '分类',
          'model': '产品型号',
          'supplier_name': '供应商',
          'is_active': '是否激活'
        };
        
        // 直接匹配
        if (patterns[fieldName]) {
          return patterns[fieldName];
        }
        
        // 下划线分割转换
        if (fieldName.includes('_')) {
          const parts = fieldName.split('_');
          const convertedParts = parts.map(part => patterns[part] || part);
          return convertedParts.join('');
        }
        
        // 驼峰命名转换
        if (/[a-z][A-Z]/.test(fieldName)) {
          const words = fieldName.replace(/([A-Z])/g, ' $1').toLowerCase().split(' ');
          const convertedWords = words.map(word => patterns[word] || word);
          return convertedWords.join('');
        }
        
        // 默认返回原字段名
        return fieldName;
      };
      
      // 处理每一行数据
      dataRows.forEach((row, index) => {
        const cells = row.split('|').filter(c => c.trim()).map(c => c.trim());
        if (cells.length === headers.length) {
          result += `**记录 ${index + 1}**\n`;
          headers.forEach((header, i) => {
            if (cells[i] && cells[i] !== '-' && cells[i] !== 'NULL' && cells[i] !== 'None') {
              const friendlyName = convertFieldName(header);
              result += `- ${friendlyName}：${cells[i]}\n`;
            }
          });
          result += '\n';
        }
      });
      
      result += '---\n\n';
      result += '以上为查询结果。如果您需要按特定条件（如分类、价格、库存等）进行查询，请随时告诉我。';
      
      return result;
    } catch (error) {
      console.error('转换表格失败:', error);
      return tableContent;
    }
  };

  // 提取查询结果，只保留MCP查询结果部分
  const extractQueryResult = (rawContent: string): string => {
    try {
      // 如果内容已经是纯查询结果（包含表格格式），转换为纯文本
      if (rawContent.includes('|') && rawContent.includes('---')) {
        // 检查是否是完整的查询结果表格
        const lines = rawContent.split('\n');
        const tableStartIndex = lines.findIndex(line => line.includes('|') && line.includes('---'));
        if (tableStartIndex !== -1) {
          // 提取表格部分
          const tableLines = lines.slice(tableStartIndex);
          let tableContent = tableLines.join('\n');
          
          // 检查表格格式是否完整
          const tableParts = tableContent.split('\n');
          if (tableParts.length >= 3) { // 至少包含表头、分隔线、一行数据
            return convertTableToText(tableContent);
          }
        }
      }
      
      // 处理MCP返回的表格格式：|---|---|---|---|---|---|---| 格式
      if (rawContent.includes('|---')) {
        const lines = rawContent.split('\n');
        const tableStartIndex = lines.findIndex(line => line.includes('|---'));
        if (tableStartIndex !== -1 && tableStartIndex > 0) {
          // 提取表头、分隔线和数据行
          const tableLines = lines.slice(tableStartIndex - 1); // 包含表头
          return convertTableToText(tableLines.join('\n'));
        }
      }
      
      // 尝试提取查询结果部分
      const resultPatterns = [
        /查询结果[：:]\s*\n\n([\s\S]*?)(?=\n\n|\n$|$)/,
        /查询结果\s*\(\d+\s*条记录\)[：:]\s*\n([\s\S]*?)(?=\n\n|\n$|$)/,
        /查询结果\s*\(\d+\s*条记录\)[：:]\s*\n\n([\s\S]*?)(?=\n\n|\n$|$)/,
        /查询结果[：:]\s*\n([\s\S]*?)(?=\n\n|\n$|$)/
      ];
      
      for (const pattern of resultPatterns) {
        const match = rawContent.match(pattern);
        if (match && match[1]) {
          return match[1].trim();
        }
      }
      
      // 如果没有找到查询结果部分，返回原始内容
      return rawContent;
    } catch (error) {
      console.error('提取查询结果失败:', error);
      return rawContent;
    }
  };

  // 格式化查询结果，只显示查询结果，隐藏查询说明
  const formatQueryResult = (rawContent: string): string => {
    try {
      // 直接返回原始内容，不进行任何格式化处理
      // 让ReactMarkdown组件自动处理Markdown格式
      return rawContent;
    } catch (error) {
      console.error('格式化查询结果失败:', error);
      return rawContent;
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // 调用智能助手API
      const response = await fetch(`${API_BASE_URL}/smart-assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          session_id: currentSessionId
        })
      });

      if (!response.ok) {
        throw new Error('聊天请求失败');
      }

      const result = await response.json();
      
      if (result.success) {
        let responseContent = '';
        let messageType: Message['type'] = 'text';
        
        // 调试：打印完整的响应结构
        console.log('🔍 MCP服务完整响应结构:', JSON.stringify(result.data, null, 2));
        
        // 提取实际响应内容
        let actualResponseContent = '';
        
        // 优先从raw_response中提取内容
        if (result.data.data && result.data.data.raw_response && result.data.data.raw_response.content && result.data.data.raw_response.content.length > 0) {
          const textContent = result.data.data.raw_response.content.find((item: any) => item.type === 'text');
          if (textContent && textContent.text) {
            actualResponseContent = textContent.text;
            console.log('🔍 使用raw_response中的实际内容:', actualResponseContent);
          }
        } else if (result.data.content) {
          // 备用方案：直接使用content字段
          actualResponseContent = result.data.content;
          console.log('🔍 使用content字段:', actualResponseContent);
        } else if (result.data.response) {
          // 最后使用response字段
          actualResponseContent = result.data.response;
          console.log('🔍 使用response字段:', actualResponseContent);
        }
        
        // 提取并只保留查询结果部分
        if (actualResponseContent) {
          console.log('原始响应内容:', actualResponseContent);
          
          // 使用新的formatMarkdownData函数格式化内容
          responseContent = formatMarkdownData(actualResponseContent);
          
          // 检查内容类型（现在返回的是Markdown格式，所以不需要特殊处理表格）
          if (responseContent.includes('```')) {
            messageType = 'code';
          } else if (responseContent.includes('$$') || responseContent.includes('\\[')) {
            messageType = 'math';
          } else if (responseContent.includes('SELECT') || responseContent.includes('INSERT') || 
              responseContent.includes('UPDATE') || responseContent.includes('DELETE')) {
            messageType = 'sql';
          } else if (responseContent.includes('📊') || responseContent.includes('📈')) {
            messageType = 'chart';
          } else {
            // 默认使用文本类型，让ReactMarkdown渲染Markdown格式
            messageType = 'text';
          }
        }
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: responseContent,
          role: 'assistant',
          timestamp: new Date(),
          type: messageType
        };
        setMessages(prev => [...prev, assistantMessage]);
        
        // 更新会话消息计数
        setChatSessions(prev => prev.map(session => 
          session.id === currentSessionId 
            ? { ...session, messageCount: session.messageCount + 2, lastMessage: inputValue }
            : session
        ));
      } else {
        throw new Error(result.message || '聊天处理失败');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '抱歉，暂时无法处理您的请求。请稍后再试。',
        role: 'assistant',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickActions = [
    { label: '今日销售统计', query: '请显示今日的销售统计' },
    { label: '库存预警', query: '哪些产品库存需要预警？' },
    { label: '热门产品', query: '最近一周哪些产品最受欢迎？' },
    { label: '供应商分析', query: '分析各供应商的供货情况' }
  ];

  const handleSaveSettings = async () => {
    try {
      setIsLoading(true);
      
      const errors: string[] = [];
      
      // 验证数据库配置
      if (databaseConfig.databases.length > 0) {
        const dbConfig = databaseConfig.databases[0];
        
        // 检查必填字段
        if (!dbConfig.host?.trim()) errors.push('数据库主机地址不能为空');
        if (!dbConfig.port) errors.push('数据库端口不能为空');
        if (!dbConfig.database?.trim()) errors.push('数据库名称不能为空');
        if (!dbConfig.username?.trim()) errors.push('数据库用户名不能为空');
        if (!dbConfig.password?.trim()) errors.push('数据库密码不能为空');
      }
      
      // 验证模型配置
      if (modelConfig.selectedModel && modelConfig.models.length > 0) {
        const selectedModel = modelConfig.models.find(m => m.id === modelConfig.selectedModel);
        if (selectedModel) {
          if (!selectedModel.apiKey?.trim()) errors.push('模型API密钥不能为空');
          if (!selectedModel.apiDomain?.trim()) errors.push('模型API域名不能为空');
        }
      } else {
        errors.push('请先选择一个AI模型');
      }
      
      // 如果有验证错误，显示错误信息并停止保存
      if (errors.length > 0) {
        alert(`保存设置失败，请检查以下问题：\n\n${errors.join('\n')}`);
        return;
      }
      
      // 准备保存到后端的数据
      const dbConfig = databaseConfig.databases[0];
      const selectedModel = modelConfig.models.find(m => m.id === modelConfig.selectedModel);
      
      if (!selectedModel) {
        alert('模型配置错误，请重试');
        return;
      }
      
      const settingsData = {
        ai_model_config: {
          model_id: selectedModel.id,
          api_key: selectedModel.apiKey,
          api_domain: selectedModel.apiDomain,
          base_url: selectedModel.baseUrl || '',
          prompt: selectedModel.prompt || ''
        },
        database_config: {
          host: dbConfig.host,
          port: dbConfig.port,
          database: dbConfig.database,
          username: dbConfig.username,
          password: dbConfig.password,
          schema_name: dbConfig.schema || ''
        },
        workspace_id: 'default' // 默认工作空间ID
      };
      
      // 调用后端API保存设置
      const response = await fetch('/api/v1/smart-assistant/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settingsData)
      });
      
      if (!response.ok) {
        // 尝试获取更详细的错误信息
        let errorMessage = `保存失败: ${response.statusText}`;
        
        try {
          const errorResult = await response.json();
          if (errorResult && errorResult.message) {
            errorMessage = errorResult.message;
          }
          if (errorResult && errorResult.detail) {
            errorMessage = errorResult.detail;
          }
        } catch (parseError) {
          // 如果无法解析JSON，使用默认错误信息
          console.warn('无法解析错误响应:', parseError);
        }
        
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      
      console.log('设置保存成功:', result);
      alert('设置保存成功！');
      setSettingsOpen(false);
    } catch (error) {
      console.error('保存设置失败:', error);
      
      // 显示具体的错误信息
      let errorMessage = '保存设置失败，请重试';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      alert(`保存设置失败：${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 处理模型配置更新
  const handleModelUpdate = (modelId: string, updates: Partial<ModelConfig>) => {
    setModelConfig(prev => ({
      ...prev,
      models: prev.models.map(model => 
        model.id === modelId 
          ? { ...model, ...updates }
          : model
      )
    }));
  };

  // 处理数据库配置更新
  const handleDatabaseUpdate = (database: DatabaseConfig) => {
    setDatabaseConfig(prev => ({
      ...prev,
      databases: prev.databases.map(db => 
        db.id === database.id 
          ? { ...db, ...database }
          : db
      )
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* 页面初始化加载状态 */}
          {isInitializing && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
                <div className="flex flex-col items-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">正在初始化智能助手</h3>
                  <p className="text-gray-600 text-center">请稍候，正在加载配置和检查服务状态...</p>
                </div>
              </div>
            </div>
          )}
          
          {/* 初始化错误提示 */}
          {initError && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
                <div className="flex flex-col items-center">
                  <div className="text-red-500 mb-4">
                    <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">初始化失败</h3>
                  <p className="text-gray-600 text-center mb-6">{initError}</p>
                  <div className="flex space-x-3">
                    <button
                      onClick={retryInitialization}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
                    >
                      <Loader2 className="w-4 h-4" />
                      <span>重试</span>
                    </button>
                    <button
                      onClick={() => window.location.reload()}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg"
                    >
                      刷新页面
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* 页面标题和设置按钮 */}
          <div className="flex justify-between items-center mb-8">
            <div className="text-center flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                智能数据助手
              </h1>
              <p className="text-gray-600">
                基于AI的智能数据查询助手，支持自然语言查询和分析
              </p>
              <div className="flex justify-center space-x-4 mt-4">
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <Database className="w-3 h-3" />
                  <span>{databaseConfig.selectedDatabase.toUpperCase()} 数据库</span>
                </Badge>
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <Bot className="w-3 h-3" />
                  <span>{modelConfig.selectedModel} 模型</span>
                </Badge>
                <Badge variant={mcpReady ? "default" : "destructive"} className="flex items-center space-x-1">
                  <Activity className="w-3 h-3" />
                  <span>助手 {mcpReady ? "已就绪" : "未就绪"}</span>
                </Badge>
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <MessageSquare className="w-3 h-3" />
                  <span>会话 {chatSessions.length}</span>
                </Badge>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button
                onClick={() => setSessionsOpen(true)}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700"
              >
                <MessageSquare className="w-4 h-4" />
                <span>会话管理</span>
              </Button>
              <Button
                onClick={() => setSettingsOpen(true)}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
              >
                <Settings className="w-4 h-4" />
                <span>设置</span>
              </Button>
            </div>
          </div>

          {/* 主内容区域 */}
          <div className="h-[calc(100vh-200px)] min-h-[600px]">
            {/* 聊天界面 */}
            <div className="h-full bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
              <ChatContainer
                messages={messages}
                inputValue={inputValue}
                onInputChange={setInputValue}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                placeholder="请输入您的问题..."
              />
            </div>
          </div>

          {/* 会话管理弹窗 */}
          {sessionsOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-96 overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-900">会话管理</h3>
                    <button
                      onClick={() => setSessionsOpen(false)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      ×
                    </button>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm text-gray-600">共 {chatSessions.length} 个会话</span>
                    <Button
                      onClick={createNewSession}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                      size="sm"
                    >
                      新建会话
                    </Button>
                  </div>
                  
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {chatSessions.map((session) => (
                      <div
                        key={session.id}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          session.id === currentSessionId
                            ? 'bg-blue-50 border-blue-200'
                            : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                        }`}
                        onClick={() => switchSession(session.id)}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">{session.name}</div>
                            <div className="text-xs text-gray-500 mt-1">
                              {session.createdAt.toLocaleDateString()} {session.createdAt.toLocaleTimeString()}
                            </div>
                            <div className="text-xs text-gray-500">
                              消息数: {session.messageCount}
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              if (chatSessions.length > 1) {
                                deleteSession(session.id);
                              } else {
                                alert('不能删除最后一个会话');
                              }
                            }}
                            className="text-red-500 hover:text-red-700 text-xs"
                          >
                            删除
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 设置弹窗 */}
          <SettingsDialog
            open={settingsOpen}
            onOpenChange={setSettingsOpen}
            
            // 数据库配置
            databases={databaseConfig.databases}
            selectedDatabase={databaseConfig.selectedDatabase}
            onDatabaseSelect={(databaseId) => setDatabaseConfig({
              ...databaseConfig,
              selectedDatabase: databaseId
            })}
            onDatabaseUpdate={handleDatabaseUpdate}
            connectionStatus={databaseConfig.connectionStatus}
            
            // AI模型配置
            models={modelConfig.models}
            selectedModel={modelConfig.selectedModel}
            onModelSelect={(modelId) => setModelConfig({
              ...modelConfig,
              selectedModel: modelId
            })}
            onModelUpdate={handleModelUpdate}
            

            

            
            // 保存设置回调
            onSave={handleSaveSettings}
          />
        </div>
      </div>
    </div>
  );
};

export default SmartAssistantPage;