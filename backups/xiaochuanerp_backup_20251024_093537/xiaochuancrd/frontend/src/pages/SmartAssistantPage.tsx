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
  // 智能字段名称转换器 - 基于完整数据库字段信息的智能转换
  const smartFieldNameConverter = (fieldName: string): string => {
    const fieldNameLower = fieldName.toLowerCase().trim();
    
    // 基于数据库结构文件的完整字段映射规则
    const rules = [
      // 通用字段
      { patterns: ['uuid', 'id'], name: 'ID' },
      { patterns: ['code', '编码'], name: '编码' },
      { patterns: ['name', '名称'], name: '名称' },
      { patterns: ['title', '标题'], name: '标题' },
      { patterns: ['description', '描述'], name: '描述' },
      
      // 供应商相关字段
      { patterns: ['supplier_name'], name: '供应商名称' },
      { patterns: ['supplier_code'], name: '供应商编码' },
      { patterns: ['contact_person'], name: '联系人' },
      { patterns: ['phone'], name: '联系电话' },
      { patterns: ['email'], name: '邮箱地址' },
      { patterns: ['address'], name: '地址信息' },
      
      // 客户相关字段
      { patterns: ['customer_name'], name: '客户名称' },
      { patterns: ['customer_code'], name: '客户编码' },
      
      // 产品相关字段
      { patterns: ['product_name'], name: '产品名称' },
      { patterns: ['product_code'], name: '产品编码' },
      { patterns: ['model_name'], name: '型号名称' },
      { patterns: ['model_code'], name: '型号编码' },
      { patterns: ['category_name'], name: '分类名称' },
      { patterns: ['category_code'], name: '分类编码' },
      
      // 库存相关字段
      { patterns: ['quantity', '库存', '数量'], name: '库存数量' },
      { patterns: ['current_quantity'], name: '当前库存' },
      { patterns: ['quantity_change'], name: '库存变动' },
      { patterns: ['min_quantity'], name: '最低库存' },
      { patterns: ['max_quantity'], name: '最高库存' },
      
      // 价格相关字段
      { patterns: ['price', '单价', '价格'], name: '价格' },
      { patterns: ['cost_price'], name: '成本价' },
      { patterns: ['sale_price'], name: '销售价' },
      { patterns: ['purchase_price'], name: '采购价' },
      
      // 状态相关字段
      { patterns: ['status', '状态'], name: '状态' },
      { patterns: ['is_active', 'active'], name: '是否激活' },
      { patterns: ['enabled'], name: '是否启用' },
      { patterns: ['processed'], name: '是否已处理' },
      
      // 时间相关字段
      { patterns: ['date', 'time', '时间'], name: '时间' },
      { patterns: ['created_at'], name: '创建时间' },
      { patterns: ['updated_at'], name: '更新时间' },
      { patterns: ['deleted_at'], name: '删除时间' },
      { patterns: ['record_date'], name: '记录日期' },
      { patterns: ['operation_time'], name: '操作时间' },
      { patterns: ['last_sync_time'], name: '最后同步时间' },
      { patterns: ['last_manual_sync_time'], name: '最后手动同步时间' },
      { patterns: ['last_auto_sync_time'], name: '最后自动同步时间' },
      
      // 操作相关字段
      { patterns: ['operation_type'], name: '操作类型' },
      { patterns: ['operation_module'], name: '操作模块' },
      { patterns: ['operation_description'], name: '操作描述' },
      { patterns: ['operation_status'], name: '操作状态' },
      { patterns: ['change_type'], name: '变动类型' },
      { patterns: ['remark', '备注'], name: '备注' },
      
      // 同步相关字段
      { patterns: ['sync_on_insert'], name: '同步插入' },
      { patterns: ['sync_on_update'], name: '同步更新' },
      { patterns: ['sync_on_delete'], name: '同步删除' },
      { patterns: ['total_sync_count'], name: '总同步次数' },
      { patterns: ['success_sync_count'], name: '成功同步次数' },
      { patterns: ['failed_sync_count'], name: '失败同步次数' },
      { patterns: ['insert_sync_count'], name: '新增同步次数' },
      { patterns: ['update_sync_count'], name: '更新同步次数' },
      { patterns: ['delete_sync_count'], name: '删除同步次数' },
      { patterns: ['manual_sync_count'], name: '手动同步次数' },
      { patterns: ['auto_sync_count'], name: '自动同步次数' },
      
      // 人员相关字段
      { patterns: ['created_by'], name: '创建者' },
      { patterns: ['operator_uuid'], name: '操作者ID' },
      { patterns: ['operator_name'], name: '操作者姓名' },
      { patterns: ['operator_ip'], name: '操作者IP' },
      
      // 其他字段
      { patterns: ['table_name'], name: '表名' },
      { patterns: ['record_uuid'], name: '记录ID' },
      { patterns: ['target_uuid'], name: '目标ID' },
      { patterns: ['target_name'], name: '目标名称' },
      { patterns: ['before_data'], name: '操作前数据' },
      { patterns: ['after_data'], name: '操作后数据' },
      { patterns: ['error_message'], name: '错误信息' },
      { patterns: ['change_data'], name: '变化数据' },
      { patterns: ['specifications'], name: '规格参数' },
      { patterns: ['selected_fields'], name: '选择字段' },
      { patterns: ['coze_api_url'], name: 'Coze API地址' },
      { patterns: ['coze_api_key'], name: 'Coze API密钥' },
      { patterns: ['coze_workflow_id'], name: 'Coze工作流ID' },
      { patterns: ['parent_uuid'], name: '父级ID' },
      { patterns: ['sort_order'], name: '排序顺序' }
    ];
    
    // 精确匹配优先
    for (const rule of rules) {
      if (rule.patterns.some(pattern => fieldNameLower === pattern.toLowerCase())) {
        return rule.name;
      }
    }
    
    // 模糊匹配
    for (const rule of rules) {
      if (rule.patterns.some(pattern => fieldNameLower.includes(pattern.toLowerCase()))) {
        return rule.name;
      }
    }
    
    // 如果没有匹配到规则，返回原始字段名（首字母大写）
    return fieldName.charAt(0).toUpperCase() + fieldName.slice(1);
  };

  // 智能值格式化器 - 基于完整数据库字段信息的智能格式化
  const smartValueFormatter = (fieldName: string, value: string): string => {
    const fieldNameLower = fieldName.toLowerCase().trim();
    
    // 处理空值
    if (!value || value === 'None' || value === 'null' || value === '' || value === 'NULL') {
      return '-';
    }
    
    // 布尔值处理
    if (value === 'true' || value === 'false' || value === '1' || value === '0') {
      const boolValue = value === 'true' || value === '1';
      
      // 状态字段
      if (fieldNameLower.includes('is_active') || fieldNameLower.includes('active')) {
        return boolValue ? '激活' : '未激活';
      }
      if (fieldNameLower.includes('enabled')) {
        return boolValue ? '启用' : '禁用';
      }
      if (fieldNameLower.includes('processed')) {
        return boolValue ? '已处理' : '未处理';
      }
      if (fieldNameLower.includes('sync_on_insert')) {
        return boolValue ? '同步' : '不同步';
      }
      if (fieldNameLower.includes('sync_on_update')) {
        return boolValue ? '同步' : '不同步';
      }
      if (fieldNameLower.includes('sync_on_delete')) {
        return boolValue ? '同步' : '不同步';
      }
      
      return boolValue ? '是' : '否';
    }
    
    // 数值格式化
    if (!isNaN(Number(value)) && value.trim() !== '') {
      const numValue = Number(value);
      
      // 价格字段
      if (fieldNameLower.includes('price') || fieldNameLower.includes('单价') || fieldNameLower.includes('价格')) {
        return numValue.toLocaleString('zh-CN', { 
          minimumFractionDigits: 2, 
          maximumFractionDigits: 2 
        }) + ' 元';
      }
      
      // 库存数量字段
      if (fieldNameLower.includes('quantity') || fieldNameLower.includes('库存') || fieldNameLower.includes('数量')) {
        return numValue.toLocaleString('zh-CN');
      }
      
      // 计数字段
      if (fieldNameLower.includes('count') || fieldNameLower.includes('次数')) {
        return numValue.toLocaleString('zh-CN') + ' 次';
      }
      
      // 排序字段
      if (fieldNameLower.includes('sort_order') || fieldNameLower.includes('排序')) {
        return numValue.toLocaleString('zh-CN');
      }
      
      // 其他数值字段
      return numValue.toLocaleString('zh-CN');
    }
    
    // 状态字段处理
    if (fieldNameLower.includes('status') || fieldNameLower.includes('状态')) {
      if (value.includes('🟢') || value.includes('🔴') || value.includes('🟡')) {
        return value; // 保持原始状态显示
      }
      
      // 产品状态
      if (value === '1' || value === '销售中') {
        return '销售中';
      }
      if (value === '0' || value === '已下架') {
        return '已下架';
      }
      if (value === '缺货') {
        return '缺货';
      }
      
      // 供应商状态
      if (value === '合作中') {
        return '合作中';
      }
      if (value === '暂停合作') {
        return '暂停合作';
      }
      if (value === '已终止') {
        return '已终止';
      }
      
      // 同步状态
      if (value === 'ACTIVE') {
        return '活跃';
      }
      if (value === 'PAUSED') {
        return '暂停';
      }
      if (value === 'ERROR') {
        return '错误';
      }
      
      // 操作状态
      if (value === 'SUCCESS') {
        return '成功';
      }
      if (value === 'FAILED') {
        return '失败';
      }
    }
    
    // 操作类型字段
    if (fieldNameLower.includes('operation_type') || fieldNameLower.includes('change_type')) {
      if (value === 'INSERT') {
        return '新增';
      }
      if (value === 'UPDATE') {
        return '更新';
      }
      if (value === 'DELETE') {
        return '删除';
      }
      if (value === 'IN') {
        return '入库';
      }
      if (value === 'OUT') {
        return '出库';
      }
      if (value === 'ADJUST') {
        return '调整';
      }
      if (value === 'LOGIN') {
        return '登录';
      }
      if (value === 'LOGOUT') {
        return '登出';
      }
    }
    
    // 同步类型字段
    if (fieldNameLower.includes('last_sync_type')) {
      if (value === 'MANUAL') {
        return '手动同步';
      }
      if (value === 'AUTO_INSERT') {
        return '自动新增';
      }
      if (value === 'AUTO_UPDATE') {
        return '自动更新';
      }
      if (value === 'AUTO_DELETE') {
        return '自动删除';
      }
    }
    
    // 电话字段处理
    if (fieldNameLower.includes('phone') || fieldNameLower.includes('电话') || fieldNameLower.includes('mobile')) {
      // 格式化电话号码
      const phone = value.replace(/[^\d]/g, '');
      if (phone.length === 11) {
        return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
      }
      if (phone.length === 10) {
        return phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
      }
    }
    
    // 邮箱字段处理
    if (fieldNameLower.includes('email') || fieldNameLower.includes('邮箱')) {
      // 保持邮箱格式不变
      return value;
    }
    
    // 日期字段处理
    if (fieldNameLower.includes('date') || fieldNameLower.includes('time') || fieldNameLower.includes('时间')) {
      const date = new Date(value);
      if (!isNaN(date.getTime())) {
        // 区分日期和时间
        if (fieldNameLower.includes('created_at') || fieldNameLower.includes('updated_at') || 
            fieldNameLower.includes('deleted_at') || fieldNameLower.includes('operation_time')) {
          return date.toLocaleString('zh-CN');
        } else {
          return date.toLocaleDateString('zh-CN');
        }
      }
    }
    
    // JSON字段处理
    if (fieldNameLower.includes('json') || fieldNameLower.includes('specifications') || 
        fieldNameLower.includes('selected_fields') || fieldNameLower.includes('change_data') ||
        fieldNameLower.includes('before_data') || fieldNameLower.includes('after_data')) {
      try {
        const jsonData = JSON.parse(value);
        if (Array.isArray(jsonData)) {
          return jsonData.join(', ');
        } else if (typeof jsonData === 'object') {
          return Object.keys(jsonData).map(key => `${key}: ${jsonData[key]}`).join(', ');
        }
      } catch (e) {
        // 不是有效的JSON，返回原始值
      }
    }
    
    // 默认返回原始值
    return value;
  };

  const convertToTextListFormat = (rawContent: string): string => {
    try {
      console.log('开始转换表格数据为纯文本键值对列表格式');
      console.log('原始内容:', rawContent);
      
      // 通用表格识别逻辑 - 不再硬编码特定格式
      let tableSection = '';
      
      // 方法1：查找包含表格结构的任何部分
      const lines = rawContent.split('\n');
      let tableStartIndex = -1;
      let tableEndIndex = -1;
      
      // 查找表头行（包含|符号但不包含---分隔线）
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.includes('|') && !line.includes('---') && line.split('|').filter(cell => cell.trim()).length > 1) {
          // 找到表头行，检查下一行是否是分隔线
          if (i + 1 < lines.length && lines[i + 1].includes('|---')) {
            tableStartIndex = i;
            break;
          }
        }
      }
      
      if (tableStartIndex !== -1) {
        // 查找表格结束位置（空行或文件结束）
        tableEndIndex = lines.length;
        for (let i = tableStartIndex + 2; i < lines.length; i++) { // 从数据行开始查找
          if (lines[i].trim() === '') {
            tableEndIndex = i;
            break;
          }
        }
        tableSection = lines.slice(tableStartIndex, tableEndIndex).join('\n');
      }
      
      // 方法2：如果没有找到标准表格结构，查找任何包含|符号的数据行
      if (!tableSection) {
        const pipeLines = lines.filter(line => 
          line.includes('|') && 
          !line.includes('---') && 
          line.split('|').filter(cell => cell.trim()).length > 1
        );
        
        if (pipeLines.length > 0) {
          // 假设第一行是表头
          const headerLine = pipeLines[0];
          const dataLines = pipeLines.slice(1);
          
          // 检查数据行是否与表头列数匹配
          const headerCols = headerLine.split('|').filter(cell => cell.trim()).length;
          const validDataLines = dataLines.filter(line => 
            line.split('|').filter(cell => cell.trim()).length === headerCols
          );
          
          if (validDataLines.length > 0) {
            tableSection = [headerLine, ...validDataLines].join('\n');
          }
        }
      }
      
      if (!tableSection) {
        console.log('未找到表格结构，返回原始内容');
        return rawContent;
      }
      
      const tableLines = tableSection.split('\n').filter(line => line.trim());
      
      // 提取表头和数据行
      const headerLine = tableLines[0];
      const headers = headerLine.split('|').map(h => h.trim()).filter(h => h);
      console.log('提取的表头:', headers);
      
      // 提取数据行（跳过表头行和可能的分隔线）
      const dataRows = tableLines.slice(1).filter(line => 
        line.includes('|') && 
        !line.includes('---')
      ).map(line => 
        line.split('|').map(cell => cell.trim()).filter(cell => cell)
      ).filter(row => row.length > 0 && row.length === headers.length);
      
      console.log('提取的数据行:', dataRows);
      
      if (dataRows.length === 0) {
        console.log('未找到有效数据行，返回原始内容');
        return rawContent;
      }
      
      // 构建纯文本键值对格式 - 通用格式，不再硬编码"商品数据库"
      const currentTime = new Date().toLocaleString('zh-CN');
      
      // 基于数据库字段信息的精确数据类型识别
      let dataType = '数据库';
      
      // 供应商表识别
      if (headers.some(h => h.toLowerCase().includes('supplier_name') || h.toLowerCase().includes('supplier_code') || 
                          h.toLowerCase().includes('contact_person') || h.toLowerCase().includes('供应商'))) {
        dataType = '供应商';
      }
      // 客户表识别
      else if (headers.some(h => h.toLowerCase().includes('customer_name') || h.toLowerCase().includes('customer_code') || 
                               h.toLowerCase().includes('contact_person') || h.toLowerCase().includes('客户'))) {
        dataType = '客户';
      }
      // 产品表识别
      else if (headers.some(h => h.toLowerCase().includes('product_name') || h.toLowerCase().includes('product_code') || 
                               h.toLowerCase().includes('sku') || h.toLowerCase().includes('商品'))) {
        dataType = '商品';
      }
      // 采购订单表识别
      else if (headers.some(h => h.toLowerCase().includes('purchase_order') || h.toLowerCase().includes('po_number') || 
                               h.toLowerCase().includes('order_date') || h.toLowerCase().includes('采购订单'))) {
        dataType = '采购订单';
      }
      // 销售订单表识别
      else if (headers.some(h => h.toLowerCase().includes('sales_order') || h.toLowerCase().includes('so_number') || 
                               h.toLowerCase().includes('order_date') || h.toLowerCase().includes('销售订单'))) {
        dataType = '销售订单';
      }
      // 库存记录表识别
      else if (headers.some(h => h.toLowerCase().includes('stock_record') || h.toLowerCase().includes('inventory') || 
                               h.toLowerCase().includes('quantity') || h.toLowerCase().includes('库存记录'))) {
        dataType = '库存记录';
      }
      // 同步配置表识别
      else if (headers.some(h => h.toLowerCase().includes('sync_config') || h.toLowerCase().includes('coze_sync') || 
                               h.toLowerCase().includes('sync_status') || h.toLowerCase().includes('同步配置'))) {
        dataType = '同步配置';
      }
      // 系统助手表识别
      else if (headers.some(h => h.toLowerCase().includes('sys_assistant') || h.toLowerCase().includes('assistant') || 
                               h.toLowerCase().includes('operation') || h.toLowerCase().includes('系统助手'))) {
        dataType = '系统助手';
      }
      // 操作日志表识别
      else if (headers.some(h => h.toLowerCase().includes('operation_log') || h.toLowerCase().includes('change_log') || 
                               h.toLowerCase().includes('operation_type') || h.toLowerCase().includes('操作日志'))) {
        dataType = '操作日志';
      }
      // 用户表识别
      else if (headers.some(h => h.toLowerCase().includes('user_name') || h.toLowerCase().includes('user_code') || 
                               h.toLowerCase().includes('login_name') || h.toLowerCase().includes('用户'))) {
        dataType = '用户';
      }
      // 通用类型
      else {
        dataType = '数据库';
      }
      
      let formattedText = `好的，已切换为纯文本模式显示${dataType}查询结果。\n\n---\n\n**${dataType}查询结果**\n\n`;
      formattedText += `**查询时间**：${currentTime}\n`;
      formattedText += `**总记录数**：${dataRows.length} 条\n\n---\n`;
      
      // 为每个记录构建纯文本键值对格式 - 使用智能转换系统
      dataRows.forEach((row, index) => {
        formattedText += `\n**记录 ${index + 1}**\n`;
        
        headers.forEach((header, headerIndex) => {
          if (headerIndex < row.length) {
            // 使用智能字段名称转换器
            const friendlyHeader = smartFieldNameConverter(header);
            
            // 使用智能值格式化器
            const cellValue = smartValueFormatter(header, row[headerIndex]);
            
            formattedText += `- ${friendlyHeader}：${cellValue}\n`;
          }
        });
      });
      
      formattedText += `\n---\n\n以上为${dataType}查询结果。如果您需要按特定条件进行查询，请随时告诉我。`;
      console.log('格式化后的文本:', formattedText);
      return formattedText;
      
    } catch (error) {
      console.error('转换表格数据为纯文本键值对列表格式失败:', error);
      return rawContent;
    }
  };

  // 格式化Markdown数据，统一所有内容为Markdown格式显示
  // 类似于DeepSeek聊天界面，所有内容都通过Markdown组件统一渲染
  const formatMarkdownData = (content: string): string => {
    try {
      // 检查是否是MCP服务返回的文件路径查询响应
      if (content.includes('无法直接读取或访问您本地文件系统中的')) {
        // 对文件路径查询响应进行美化格式化
        return `📁 **文件查询结果**

${content}

---

💡 **建议**：如果您需要查询数据库中的具体数据，请直接告诉我您想了解的内容，比如：
- "查询产品库存"
- "显示今日销售统计"
- "查看库存预警产品"

我会帮您从数据库中获取准确的信息！`;
      }
      
      // 检查是否包含表格格式，如果是则转换为更美观的Markdown表格
      if (content.includes('|') && content.includes('---')) {
        return convertToMarkdownTable(content);
      }
      
      // 检查是否包含自定义列表格式（如🔹开头的行）
      if (content.includes('🔹')) {
        return convertCustomListToMarkdown(content);
      }
      
      // 对于其他内容，保持原始格式
      return content;
    } catch (error) {
      console.error('格式化Markdown数据失败:', error);
      return content; // 出错时返回原内容
    }
  };
  
  // 将自定义列表格式转换为Markdown表格
  const convertCustomListToMarkdown = (content: string): string => {
    try {
      const lines = content.split('\n').filter(line => line.trim());
      
      // 检测数据类型
      let dataType = '数据库';
      let icon = '📊';
      if (content.includes('📦')) {
        dataType = '产品';
        icon = '📦';
      }
      if (content.includes('💰')) {
        dataType = '销售订单';
        icon = '💰';
      }
      if (content.includes('🛒')) {
        dataType = '采购订单';
        icon = '🛒';
      }
      
      // 提取记录行（以🔹开头的行）
      const recordLines = lines.filter(line => line.trim().startsWith('🔹'));
      
      if (recordLines.length === 0) {
        return content; // 没有记录行，返回原内容
      }
      
      // 构建表格内容
      let markdownContent = `${icon} **${dataType}查询结果**\n\n`;
      markdownContent += `**查询时间**：${new Date().toLocaleString('zh-CN')}\n`;
      markdownContent += `**总记录数**：${recordLines.length} 条\n\n`;
      
      // 根据数据类型构建表格
      if (dataType === '产品') {
        markdownContent += `| 产品名称 | 产品代码 | 当前库存 | 最小库存 | 最大库存 | 单价 |\n`;
        markdownContent += `|---------|---------|---------|---------|---------|------|\n`;
        
        recordLines.forEach((recordLine) => {
          const recordText = recordLine.replace('🔹', '').trim();
          const productMatch = recordText.match(/^(.+?)\s*\((.+?)\)/);
          
          if (productMatch) {
            const productName = productMatch[1].trim();
            const productCode = productMatch[2].trim();
            
            // 查找后续行获取库存和价格信息
            const currentLineIndex = lines.indexOf(recordLine);
            const nextLines = lines.slice(currentLineIndex + 1, currentLineIndex + 3);
            
            let currentQuantity = '0';
            let minQuantity = '0';
            let maxQuantity = '0';
            let unitPrice = '0.00';
            
            nextLines.forEach(line => {
              if (line.includes('当前库存:')) {
                const stockMatch = line.match(/当前库存:\s*(\d+)\s*(\d+)\/(\d+)/);
                if (stockMatch) {
                  currentQuantity = stockMatch[1];
                  minQuantity = stockMatch[2];
                  maxQuantity = stockMatch[3];
                }
              } else if (line.includes('单价:')) {
                const priceMatch = line.match(/单价:\s*¥([\d.]+)/);
                if (priceMatch) {
                  unitPrice = priceMatch[1];
                }
              }
            });
            
            markdownContent += `| ${productName} | ${productCode} | ${currentQuantity} | ${minQuantity} | ${maxQuantity} | ¥${unitPrice} |\n`;
          }
        });
      } else {
        // 通用处理：创建简单的表格
        markdownContent += `| 记录 |\n`;
        markdownContent += `|------|\n`;
        
        recordLines.forEach((recordLine) => {
          const recordText = recordLine.replace('🔹', '').trim();
          markdownContent += `| ${recordText} |\n`;
        });
      }
      
      markdownContent += `\n---\n\n以上为${dataType}查询结果。如果您需要按特定条件进行查询，请随时告诉我。`;
      
      return markdownContent;
    } catch (error) {
      console.error('转换自定义列表格式失败:', error);
      return content; // 出错时返回原内容
    }
  };
  
  // 将表格内容转换为更美观的Markdown表格
  const convertToMarkdownTable = (content: string): string => {
    try {
      const lines = content.split('\n').filter(line => line.trim());
      
      // 查找表格开始位置
      const tableStartIndex = lines.findIndex(line => line.includes('|') && line.includes('---'));
      if (tableStartIndex === -1) {
        return content; // 没有找到表格，返回原内容
      }
      
      // 提取表格前的内容（标题等）
      const beforeTable = lines.slice(0, tableStartIndex - 1).join('\n');
      
      // 提取表格内容
      const tableLines = lines.slice(tableStartIndex - 1);
      
      // 确保表格格式正确
      if (tableLines.length < 3) {
        return content; // 表格不完整，返回原内容
      }
      
      // 优化表格显示
      let markdownContent = beforeTable + '\n\n';
      
      // 添加表格标题
      if (!beforeTable.includes('查询结果') && !beforeTable.includes('结果')) {
        markdownContent += '📊 **查询结果**\n\n';
      }
      
      // 添加表格内容
      markdownContent += tableLines.join('\n');
      
      // 添加表格说明
      if (!content.includes('以上为') && !content.includes('查询结果')) {
        markdownContent += '\n\n---\n\n以上为查询结果。如果您需要按特定条件进行查询，请随时告诉我。';
      }
      
      return markdownContent;
    } catch (error) {
      console.error('转换Markdown表格失败:', error);
      return content; // 出错时返回原内容
    }
  };

  // 处理发送消息
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
        
        // 优先从MCP服务的原始响应结构中提取内容
        if (result.data.data && result.data.data.raw_response && result.data.data.raw_response.content && result.data.data.raw_response.content.length > 0) {
          // 从MCP服务的原始content数组中提取第一个text内容
          const rawContent = result.data.data.raw_response.content[0];
          actualResponseContent = rawContent.text || rawContent.content || JSON.stringify(rawContent);
          console.log('🔍 使用MCP原始响应内容:', actualResponseContent);
        } else if (result.data.data && result.data.data.content && result.data.data.content.length > 0) {
          // 从data.content数组中提取
          const dataContent = result.data.data.content[0];
          actualResponseContent = dataContent.text || dataContent.content || JSON.stringify(dataContent);
          console.log('🔍 使用data.content内容:', actualResponseContent);
        } else if (result.data.response) {
          // 从response字段提取（后端包装后的内容）
          actualResponseContent = result.data.response;
          console.log('🔍 使用response字段内容:', actualResponseContent);
        } else if (result.data.content) {
          // 从content字段提取
          actualResponseContent = result.data.content;
          console.log('🔍 使用content字段内容:', actualResponseContent);
        }
        
        // 提取并只保留查询结果部分
        if (actualResponseContent) {
          console.log('原始响应内容:', actualResponseContent);
          
          // 使用新的formatMarkdownData函数格式化内容
          responseContent = formatMarkdownData(actualResponseContent);
          
          // 统一使用文本类型，让ReactMarkdown组件渲染所有内容
          // 类似于DeepSeek聊天界面，所有内容都通过Markdown格式统一显示
          messageType = 'text';
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
            
            // 分析模型配置（传递空数组和默认值）
            analysisModels={[]}
            selectedAnalysisModel=""
            onAnalysisModelSelect={() => {}}
            onAnalysisModelUpdate={() => {}}
            
            // 保存设置回调
            onSave={handleSaveSettings}
          />
        </div>
      </div>
    </div>
  );
}

export default SmartAssistantPage;
