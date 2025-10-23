import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { 
  Upload, 
  Play, 
  Pause, 
  Trash2, 
  RefreshCw, 
  Filter, 
  Plus, 
  Minus,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Database,
  Circle,
  PauseCircle,
  Settings,
  Sliders,
  Wifi,
  FileText
} from 'lucide-react';
import { cozeApi } from '@/services/api/coze';
import { useAuthStore } from '@/stores/authStore';
import { useNavigate } from 'react-router-dom';
import { getCozeConfig, saveCozeConfig } from '@/services/config/cozeConfig';
import toast from 'react-hot-toast';

interface CozeTableInfo {
  tableName: string;
  displayName: string;
  description: string;
  recordCount: number;
  lastUpdated: string;
}

interface CozeFieldInfo {
  fieldName: string;
  displayName: string;
  fieldType: string;
  isRequired: boolean;
  description: string;
}

interface CozeUploadFilter {
  field: string;
  operator: string;
  value: any;
}

interface CozeUploadRequest {
  tableName: string;
  cozeWorkflowId: string;
  cozeApiKey?: string;
  cozeApiUrl: string;
  filters?: CozeUploadFilter[];
  batchSize: number;
  selectedFields?: string[];
  configTitle?: string;
  cozeWorkflowIdInsert?: string;
  cozeWorkflowIdUpdate?: string;
  cozeWorkflowIdDelete?: string;
}

interface CozeUploadResponse {
  uploadId: string;
  message: string;
  status: string;
}

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

const CozeUploadPage: React.FC = () => {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  const [tables, setTables] = useState<CozeTableInfo[]>([]);
  const [syncConfigs, setSyncConfigs] = useState<any[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableFields, setTableFields] = useState<CozeFieldInfo[]>([]);
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [cozeWorkflowId, setCozeWorkflowId] = useState('');
  const [globalCozeApiKey, setGlobalCozeApiKey] = useState('');
  const [cozeApiUrl, setCozeApiUrl] = useState('https://api.coze.cn');
  const [batchSize, setBatchSize] = useState<number>(100);
  const [filters, setFilters] = useState<Array<{field: string; operator: string; value: string}>>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('config');
  const [authError, setAuthError] = useState<string>('');
  const [realTimeSyncEnabled, setRealTimeSyncEnabled] = useState<boolean>(false);
  const [testingConnection, setTestingConnection] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<{
    success: boolean; 
    message: string;
    responseData?: any;
    requestData?: any;
    timestamp?: string;
  } | null>(null);
  const [savingConfig, setSavingConfig] = useState<boolean>(false);
  const [confirmedFields, setConfirmedFields] = useState<string[]>([]);
  const [showRequestHeaders, setShowRequestHeaders] = useState<boolean>(false);
  const [sampleData, setSampleData] = useState<any[]>([]);
  const [showAllData, setShowAllData] = useState<boolean>(false);
  const [configTitle, setConfigTitle] = useState<string>('');
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<any>(null);
  const [showTemplatePreview, setShowTemplatePreview] = useState<boolean>(true); // 模板预览模式
  
  // 三个工作流ID配置
  const [cozeWorkflowIdInsert, setCozeWorkflowIdInsert] = useState('');
  const [cozeWorkflowIdUpdate, setCozeWorkflowIdUpdate] = useState('');
  const [cozeWorkflowIdDelete, setCozeWorkflowIdDelete] = useState('');

  // 获取可上传的数据表列表
  const fetchTables = async () => {
    if (!isAuthenticated) {
      setAuthError('请先登录系统');
      return;
    }
    
    try {
      const response = await cozeApi.getTables();
      if (response.success) {
        setTables(response.data);
        setAuthError('');
      } else {
        setAuthError('获取数据表列表失败: ' + response.message);
      }
    } catch (error: any) {
      console.error('获取数据表列表失败:', error);
      if (error.response?.status === 401) {
        setAuthError('认证失败，请重新登录');
        navigate('/login');
      } else {
        setAuthError('获取数据表列表失败: ' + error.message);
      }
    }
  };

  // 获取数据表的字段信息
  const fetchTableFields = async (tableName: string) => {
    if (!tableName) {
      setTableFields([]);
      setSelectedFields([]);
      return;
    }
    
    try {
      const response = await cozeApi.getTableFields(tableName);
      if (response.success) {
        setTableFields(response.data);
        // 默认选择所有字段
        setSelectedFields(response.data.map((field: CozeFieldInfo) => field.fieldName));
      } else {
        setTableFields([]);
        setSelectedFields([]);
        console.error('获取字段信息失败:', response.message);
      }
    } catch (error: any) {
      console.error('获取字段信息失败:', error);
      setTableFields([]);
      setSelectedFields([]);
    }
  };

  // 获取上传历史记录 (已废弃，保留函数但不使用)
  const fetchUploadHistory = async () => {
    // 此功能已废弃，不再使用
    console.log('上传历史功能已废弃');
  };

  // 创建实时同步配置
  const createSyncConfig = async () => {
    if (!isAuthenticated) {
      setAuthError('请先登录系统');
      navigate('/login');
      return;
    }
    
    if (!selectedTable) {
      alert('请选择数据表');
      return;
    }
    
    // 验证至少有一个工作流ID不为空
    if (!cozeWorkflowIdInsert && !cozeWorkflowIdUpdate && !cozeWorkflowIdDelete) {
      alert('请至少输入一个工作流ID（新增、更新或删除操作）');
      return;
    }
    
    // 检查全局配置是否已设置
    if (!cozeApiUrl) {
      alert('请先在全局配置中设置Coze API地址');
      return;
    }
    
    if (!globalCozeApiKey) {
      alert('请先在全局配置中设置Coze API密钥');
      return;
    }

    // 检查是否选择了字段
    if (confirmedFields.length === 0) {
      alert('请先选择字段并点击确认按钮');
      return;
    }

    setLoading(true);
    try {
      // 如果没有填写标题，自动生成一个
      const finalConfigTitle = configTitle.trim() || `${selectedTable} - ${cozeWorkflowId}`;
      
      const request: CozeUploadRequest = {
        tableName: selectedTable,
        cozeWorkflowId: cozeWorkflowId,
        cozeApiKey: globalCozeApiKey || undefined,
        cozeApiUrl: cozeApiUrl,
        filters: [],
        batchSize: 100,
        // 添加选择的字段信息
        selectedFields: confirmedFields,
        // 添加配置标题
        configTitle: finalConfigTitle,
        // 添加三个工作流ID
        cozeWorkflowIdInsert: cozeWorkflowIdInsert || undefined,
        cozeWorkflowIdUpdate: cozeWorkflowIdUpdate || undefined,
        cozeWorkflowIdDelete: cozeWorkflowIdDelete || undefined
      };

      const response = await cozeApi.createSyncConfig(request);
      if (response.success) {
        // 刷新同步配置列表
        await fetchSyncConfigs();
        setDialogOpen(false);
        setAuthError('');
        
        alert('实时同步配置创建成功！数据将在数据库变化时自动同步到Coze。');
      } else {
        setAuthError('创建同步配置失败: ' + response.message);
        alert('创建同步配置失败: ' + response.message);
      }
    } catch (error: any) {
      console.error('创建同步配置失败:', error);
      if (error.response?.status === 401) {
        setAuthError('认证失败，请重新登录');
        navigate('/login');
      } else {
        setAuthError('创建同步配置失败: ' + error.message);
        alert('创建同步配置失败: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  // 确认选择的字段
  const confirmSelectedFields = async () => {
    if (selectedFields.length === 0) {
      toast.error('请至少选择一个要同步的字段');
      return;
    }
    
    setConfirmedFields([...selectedFields]);
    setShowRequestHeaders(true);
    setShowTemplatePreview(true); // 设置为模板预览模式
    
    // 生成不带数据的请求头模板，使用数据库中的蛇形命名
    generateRequestTemplate(selectedFields);
    
    toast.success(`已确认 ${selectedFields.length} 个字段，已生成同步模板`);
  };

  // 生成不带数据的请求头模板
  const generateRequestTemplate = (fields: string[]) => {
    // 清空样本数据，只显示模板
    setSampleData([]);
    
    // 创建模板数据，使用蛇形命名作为变量名
    const templateData = [{
      // 使用蛇形命名作为占位符，表示这些字段将在同步时从数据库动态获取
      ...Object.fromEntries(fields.map(field => [field, `[${field}]`]))
    }];
    
    setSampleData(templateData);
  };

  // 重置对话框状态
  const resetDialogState = () => {
    setConfirmedFields([]);
    setShowRequestHeaders(false);
    setSelectedFields([]);
    setSelectedTable('');
    setTableFields([]);
    setCozeWorkflowId('');
    setConfigTitle('');
    // 重置三个工作流ID
    setCozeWorkflowIdInsert('');
    setCozeWorkflowIdUpdate('');
    setCozeWorkflowIdDelete('');
  };

  // 测试数据传输
  const testDataTransfer = async () => {
    if (!cozeApiUrl || !globalCozeApiKey || !cozeWorkflowId) {
      setTestResult({
        success: false,
        message: '请先填写API地址、API密钥和工作流ID'
      });
      return;
    }

    if (!selectedTable) {
      setTestResult({
        success: false,
        message: '请先选择数据表'
      });
      return;
    }

    if (confirmedFields.length === 0) {
      setTestResult({
        success: false,
        message: '请先确认字段'
      });
      return;
    }

    setTestingConnection(true);
    setTestResult(null);
    
    try {
      // 询问用户是否获取所有数据
      const getAllData = confirm('是否获取所有数据？点击"确定"获取所有数据，点击"取消"仅获取3条样本数据');
      
      // 根据用户选择设置数据获取参数
      const sampleSize = getAllData ? 1000 : 3; // 获取所有数据时使用较大的数量
      
      // 首先从后端获取真实数据库数据
      const realDataResponse = await fetch(`/api/v1/coze/tables/${selectedTable}/sample?sample_size=${sampleSize}`);
      if (!realDataResponse.ok) {
        throw new Error(`获取真实数据失败: ${realDataResponse.status}`);
      }
      
      const realData = await realDataResponse.json();
      
      if (!realData || realData.length === 0) {
        throw new Error('数据库中暂无数据，请先添加测试数据');
      }
      
      // 将蛇形命名的字段名转换为大驼峰命名，以便正确访问后端返回的数据
      const snakeToCamel = (str: string) => {
        return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      };
      
      // 转换字段名映射
      const fieldMapping: Record<string, string> = {};
      confirmedFields.forEach(field => {
        const camelField = snakeToCamel(field);
        fieldMapping[field] = camelField;
      });
      
      // 使用真正的批量传输模式：将多条记录的数据合并到parameters中
      // 每条记录的字段名作为独立的参数，使用数字后缀区分不同记录
      const parameters: Record<string, any> = {};
      
      let successCount = 0;
      let errorCount = 0;
      
      // 逐条传输数据，每条数据间隔1秒
      for (let i = 0; i < realData.length; i++) {
        const record = realData[i];
        
        // 构建单条数据的parameters
        const singleParameters: Record<string, any> = {};
        
        confirmedFields.forEach(field => {
          // 优先使用大驼峰命名字段，如果不存在则使用原字段名
          const camelField = fieldMapping[field];
          const fieldValue = record[camelField] !== undefined ? record[camelField] : record[field];
          
          if (fieldValue !== undefined) {
            // 字段映射：将uuid映射为user_id，避免与Coze数据库中的uuid字段冲突
            const mappedFieldName = field === 'uuid' ? 'user_id' : field;
            
            // 直接使用蛇形命名参数，符合Coze工作流参数格式
            singleParameters[mappedFieldName] = fieldValue;
          }
        });
        
        const testData = {
          workflow_id: cozeWorkflowId,
          parameters: singleParameters
        };

        console.log(`发送第${i+1}条数据到Coze API:`, testData);

        try {
          const response = await fetch(`${cozeApiUrl}/v1/workflow/run`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${globalCozeApiKey}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(testData)
          });

          if (response.ok) {
            const result = await response.json();
            console.log(`第${i+1}条数据传输成功:`, result);
            successCount++;
          } else {
            const errorText = await response.text();
            console.error(`第${i+1}条数据传输失败:`, errorText);
            errorCount++;
          }
        } catch (error: any) {
          console.error(`第${i+1}条数据传输异常:`, error);
          errorCount++;
        }
        
        // 如果不是最后一条数据，等待1秒后再发送下一条
        if (i < realData.length - 1) {
          console.log(`等待1秒后发送下一条数据...`);
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }

      // 根据传输结果设置测试结果
      if (successCount > 0) {
        setTestResult({
          success: true,
          message: `数据传输完成！成功 ${successCount} 条，失败 ${errorCount} 条`,
          responseData: { successCount, errorCount, total: realData.length },
          requestData: null,
          timestamp: new Date().toLocaleString()
        });
      } else {
        setTestResult({
          success: false,
          message: `数据传输全部失败！共 ${errorCount} 条失败`,
          responseData: { successCount, errorCount, total: realData.length },
          requestData: null,
          timestamp: new Date().toLocaleString()
        });
      }
    } catch (error: any) {
      console.error('数据传输测试失败:', error);
      setTestResult({
        success: false,
        message: `数据传输测试失败！`,
        responseData: { error: error.message, name: error.name },
        requestData: null,
        timestamp: new Date().toLocaleString()
      });
    } finally {
      setTestingConnection(false);
    }
  };

  // 获取同步配置列表
  const fetchSyncConfigs = async () => {
    if (!isAuthenticated) {
      setAuthError('请先登录系统');
      return;
    }
    
    try {
      const response = await cozeApi.getSyncConfigs();
      if (response.success) {
        setSyncConfigs(response.data || []);
        setAuthError('');
      } else {
        setAuthError('获取同步配置失败: ' + response.message);
      }
    } catch (error: any) {
      console.error('获取同步配置失败:', error);
      if (error.response?.status === 401) {
        setAuthError('认证失败，请重新登录');
        navigate('/login');
      } else {
        setAuthError('获取同步配置失败: ' + error.message);
      }
    }
  };

  // 删除同步配置
  const deleteSyncConfig = async (configId: string) => {
    if (!confirm('确定要删除此同步配置吗？删除后将停止该表的实时数据同步。')) {
      return;
    }

    try {
      const response = await cozeApi.deleteSyncConfig(configId);
      if (response.success) {
        await fetchSyncConfigs();
        alert('同步配置删除成功');
      } else {
        alert('删除同步配置失败: ' + response.message);
      }
    } catch (error: any) {
      console.error('删除同步配置失败:', error);
      alert('删除同步配置失败: ' + error.message);
    }
  };

  // 手动触发同步
  const handleManualSync = async (configId: string) => {
    if (!confirm('确定要手动触发同步吗？这将立即同步当前数据表中的所有数据到Coze。')) {
      return;
    }

    try {
      const response = await cozeApi.triggerManualSync(configId);
      if (response.success) {
        alert(`手动同步成功！${response.message}`);
        // 刷新同步配置列表以更新状态
        await fetchSyncConfigs();
      } else {
        alert(`手动同步失败: ${response.message}`);
      }
    } catch (error: any) {
      console.error('手动同步失败:', error);
      alert(`手动同步失败: ${error.message}`);
    }
  };

  // 打开编辑对话框
  const handleEditConfig = async (config: any) => {
    setEditingConfig(config);
    setCozeWorkflowId(config.cozeWorkflowId);
    setConfigTitle(config.configTitle || '');
    setSelectedTable(config.tableName || '');
    // 设置三个工作流ID
    setCozeWorkflowIdInsert(config.cozeWorkflowIdInsert || '');
    setCozeWorkflowIdUpdate(config.cozeWorkflowIdUpdate || '');
    setCozeWorkflowIdDelete(config.cozeWorkflowIdDelete || '');
    
    // 设置模板预览模式为默认显示
    setShowTemplatePreview(true);
    
    // 加载配置的字段信息
    if (config.tableName) {
      try {
        // 获取数据表字段
        const fieldsResponse = await cozeApi.getTableFields(config.tableName);
        if (fieldsResponse.success) {
          setTableFields(fieldsResponse.data || []);
          
          // 设置已选择的字段（从配置中获取）
          if (config.selectedFields && Array.isArray(config.selectedFields)) {
            setSelectedFields(config.selectedFields);
            setConfirmedFields(config.selectedFields);
            setShowRequestHeaders(true);
            
            // 生成请求模板
            generateRequestTemplate(config.selectedFields);
          }
        }
      } catch (error) {
        console.error('加载配置字段信息失败:', error);
        // 如果加载失败，设置默认字段
        setSelectedFields([]);
        setConfirmedFields([]);
        setShowRequestHeaders(false);
      }
    }
    
    setEditDialogOpen(true);
  };

  // 保存编辑的配置
  const handleSaveEdit = async () => {
    if (!editingConfig) return;
    
    // 验证至少有一个工作流ID不为空
    if (!cozeWorkflowIdInsert.trim() && !cozeWorkflowIdUpdate.trim() && !cozeWorkflowIdDelete.trim()) {
      alert('请至少输入一个工作流ID（新增、更新或删除操作）');
      return;
    }

    if (!selectedTable) {
      alert('请选择数据表');
      return;
    }

    if (confirmedFields.length === 0) {
      alert('请选择要同步的字段');
      return;
    }

    try {
      const updates = {
        cozeWorkflowId: cozeWorkflowIdInsert.trim() || cozeWorkflowIdUpdate.trim() || cozeWorkflowIdDelete.trim(),
        configTitle: configTitle.trim() || undefined,
        tableName: selectedTable,
        selectedFields: confirmedFields,
        // 添加三个工作流ID
        cozeWorkflowIdInsert: cozeWorkflowIdInsert.trim() || undefined,
        cozeWorkflowIdUpdate: cozeWorkflowIdUpdate.trim() || undefined,
        cozeWorkflowIdDelete: cozeWorkflowIdDelete.trim() || undefined
      };
      
      await updateSyncConfig(editingConfig.configId, updates);
      setEditDialogOpen(false);
      setEditingConfig(null);
      
      // 重置状态
      setSelectedTable('');
      setSelectedFields([]);
      setConfirmedFields([]);
      setShowRequestHeaders(false);
    } catch (error: any) {
      console.error('保存编辑失败:', error);
      alert(`保存编辑失败: ${error.message}`);
    }
  };

  // 取消编辑
  const handleCancelEdit = () => {
    setEditDialogOpen(false);
    setEditingConfig(null);
    setCozeWorkflowId('');
    setConfigTitle('');
    setSelectedTable('');
    setSelectedFields([]);
    setConfirmedFields([]);
    setShowRequestHeaders(false);
    // 重置三个工作流ID
    setCozeWorkflowIdInsert('');
    setCozeWorkflowIdUpdate('');
    setCozeWorkflowIdDelete('');
  };

  // 更新同步配置
  const updateSyncConfig = async (configId: string, updates: Partial<CozeUploadRequest>) => {
    try {
      const response = await cozeApi.updateSyncConfig(configId, updates);
      if (response.success) {
        await fetchSyncConfigs();
        alert('同步配置更新成功');
      } else {
        alert('更新同步配置失败: ' + response.message);
      }
    } catch (error: any) {
      console.error('更新同步配置失败:', error);
      alert('更新同步配置失败: ' + error.message);
    }
  };

  // 保存Coze配置
  const saveConfig = async () => {
    if (!cozeApiUrl) {
      alert('请先填写API地址');
      return;
    }

    if (!globalCozeApiKey) {
      alert('请先填写API密钥');
      return;
    }

    setSavingConfig(true);
    
    try {
      const config = {
        apiUrl: cozeApiUrl,
        apiKey: globalCozeApiKey
      };
      
      const success = saveCozeConfig(config);
      
      if (success) {
        alert('✅ Coze配置保存成功！');
      } else {
        alert('❌ Coze配置保存失败');
      }
    } catch (error: any) {
      console.error('保存配置失败:', error);
      alert(`❌ Coze配置保存失败: ${error.message || '未知错误'}`);
    } finally {
      setSavingConfig(false);
    }
  };

  // 添加筛选条件
  const addFilter = () => {
    setFilters(prev => [...prev, { field: '', operator: '=', value: '' }]);
  };

  // 移除筛选条件
  const removeFilter = (index: number) => {
    setFilters(prev => prev.filter((_, i) => i !== index));
  };

  // 更新筛选条件
  const updateFilter = (index: number, field: string, value: any) => {
    setFilters(prev => prev.map((filter, i) => 
      i === index ? { ...filter, [field]: value } : filter
    ));
  };

  // 获取状态对应的图标和颜色
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'PENDING':
        return { icon: Clock, color: 'bg-yellow-100 text-yellow-800' };
      case 'PROCESSING':
        return { icon: RefreshCw, color: 'bg-blue-100 text-blue-800' };
      case 'COMPLETED':
        return { icon: CheckCircle, color: 'bg-green-100 text-green-800' };
      case 'FAILED':
        return { icon: XCircle, color: 'bg-red-100 text-red-800' };
      case 'CANCELLED':
        return { icon: XCircle, color: 'bg-gray-100 text-gray-800' };
      default:
        return { icon: Clock, color: 'bg-gray-100 text-gray-800' };
    }
  };

  // 获取样本数据用于显示API请求头
  const fetchSampleData = async (tableName: string, fields: string[], showAllData: boolean = false) => {
    if (!tableName || fields.length === 0) {
      setSampleData([]);
      return;
    }
    
    try {
      // 根据showAllData参数决定获取的数据量
      const sampleSize = showAllData ? 1000 : 3;
      const response = await fetch(`/api/v1/coze/tables/${tableName}/sample?sample_size=${sampleSize}`);
      if (!response.ok) {
        throw new Error(`获取样本数据失败: ${response.status}`);
      }
      
      const data = await response.json();
      
      // 将蛇形命名的字段名转换为大驼峰命名，以便正确访问后端返回的数据
      const snakeToCamel = (str: string) => {
        return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      };
      
      // 转换字段名映射
      const fieldMapping: Record<string, string> = {};
      fields.forEach(field => {
        const camelField = snakeToCamel(field);
        fieldMapping[field] = camelField;
      });
      
      // 确保数据中的字段名使用正确的格式
      const processedData = data.map((record: any) => {
        const processedRecord: Record<string, any> = {};
        fields.forEach(field => {
          const camelField = fieldMapping[field];
          // 优先使用大驼峰命名字段，如果不存在则使用原字段名
          processedRecord[field] = record[camelField] !== undefined ? record[camelField] : record[field];
        });
        return processedRecord;
      });
      
      setSampleData(processedData);
    } catch (error: any) {
      console.error('获取样本数据失败:', error);
      setSampleData([]);
    }
  };

  // 获取同步状态对应的图标、颜色和文本
  const getSyncStatusConfig = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return { 
          icon: Circle, 
          color: 'bg-green-100 text-green-800 border-green-200',
          text: '运行中'
        };
      case 'PAUSED':
        return { 
          icon: PauseCircle, 
          color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          text: '已暂停'
        };
      case 'ERROR':
        return { 
          icon: XCircle, 
          color: 'bg-red-100 text-red-800 border-red-200',
          text: '错误'
        };
      case 'INACTIVE':
      default:
        return { 
          icon: Circle, 
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          text: '未激活'
        };
    }
  };

  // 组件初始化时检查认证状态并获取数据
  useEffect(() => {
    if (!isAuthenticated) {
      setAuthError('请先登录系统');
      navigate('/login');
      return;
    }
    
    // 从本地存储加载Coze配置
    const savedConfig = getCozeConfig();
    setCozeApiUrl(savedConfig.apiUrl);
    setGlobalCozeApiKey(savedConfig.apiKey);
    
    fetchTables();
    fetchSyncConfigs();
  }, [isAuthenticated, navigate]);

  // 当选择的数据表变化时，获取字段信息
  useEffect(() => {
    if (selectedTable) {
      fetchTableFields(selectedTable);
    } else {
      setTableFields([]);
      setSelectedFields([]);
    }
  }, [selectedTable]);

  // 定时刷新同步配置状态
  useEffect(() => {
    const interval = setInterval(() => {
      if (syncConfigs.length > 0) {
        fetchSyncConfigs();
      }
    }, 10000); // 每10秒刷新一次

    return () => clearInterval(interval);
  }, [syncConfigs.length]);

  return (
    <div className="space-y-6">
      {/* 认证错误提示 */}
      {authError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-red-800 font-medium">{authError}</span>
          </div>
        </div>
      )}
      
      {/* 全局密钥配置区域 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            全局配置
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            配置全局Coze API密钥，所有同步配置将使用此密钥
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Coze API地址</label>
              <Input
                value={cozeApiUrl}
                onChange={(e) => setCozeApiUrl(e.target.value)}
                placeholder="https://api.coze.cn"
              />
            </div>
            <div>
              <label className="text-sm font-medium">全局Coze API密钥</label>
              <Input
                type="password"
                value={globalCozeApiKey}
                onChange={(e) => setGlobalCozeApiKey(e.target.value)}
                placeholder="输入全局Coze API密钥"
              />
            </div>
          </div>
          <div className="mt-4 space-y-3">
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={testDataTransfer}
                disabled={testingConnection}
                size="sm"
              >
                {testingConnection ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    测试中...
                  </>
                ) : (
                  <>
                    <Wifi className="h-4 w-4 mr-2" />
                    测试数据传输
                  </>
                )}
              </Button>
              
              <Button
                onClick={saveConfig}
                disabled={savingConfig}
                size="sm"
              >
                {savingConfig ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    保存配置
                  </>
                )}
              </Button>
            </div>
            
            {/* 测试结果显示区域 */}
            {testResult && (
              <div className={`p-4 rounded-lg border ${
                testResult.success 
                  ? 'bg-green-50 border-green-200' 
                  : 'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    {testResult.success ? (
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500 mr-2" />
                    )}
                    <span className={`font-medium ${
                      testResult.success ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {testResult.success ? '✅ 数据传输测试成功' : '❌ 数据传输测试失败'}
                    </span>
                  </div>
                  {testResult.timestamp && (
                    <span className="text-xs text-gray-500">
                      {testResult.timestamp}
                    </span>
                  )}
                </div>
                
                <div className="space-y-2">
                  <p className={`text-sm ${
                    testResult.success ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {testResult.message}
                  </p>
                  
                  {/* 显示详细结果 */}
                  {testResult.responseData && (
                    <div className="mt-3">
                      <details className="text-sm">
                        <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                          📊 查看详细响应数据
                        </summary>
                        <div className="mt-2 p-3 bg-gray-50 rounded border overflow-x-auto">
                          <pre className="text-xs whitespace-pre-wrap">
                            {JSON.stringify(testResult.responseData, null, 2)}
                          </pre>
                        </div>
                      </details>
                    </div>
                  )}
                  
                  {/* 显示请求数据 */}
                  {testResult.requestData && (
                    <div className="mt-2">
                      <details className="text-sm">
                        <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                          📤 查看发送的请求数据
                        </summary>
                        <div className="mt-2 p-3 bg-gray-50 rounded border overflow-x-auto">
                          <pre className="text-xs whitespace-pre-wrap">
                            {JSON.stringify(testResult.requestData, null, 2)}
                          </pre>
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Coze数据同步</h1>
          <p className="text-muted-foreground">
            实时同步数据库数据到Coze平台
          </p>
        </div>
      </div>

      {/* 添加同步配置的Dialog */}
      <Dialog open={dialogOpen} onOpenChange={(open) => {
        setDialogOpen(open);
        if (!open) {
          resetDialogState();
        }
      }}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>添加同步配置</DialogTitle>
            <DialogDescription>
              配置数据表与Coze工作流的实时同步
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* 基础配置区域 */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">基础配置</h3>
              
              <div>
                <label className="text-sm font-medium">配置标题</label>
                <Input
                  value={configTitle}
                  onChange={(e) => setConfigTitle(e.target.value)}
                  placeholder="输入同步配置标题（如：用户数据同步到Coze）"
                />
                <p className="text-xs text-gray-500 mt-1">
                  用于区分不同的同步配置，如果不填写将自动生成
                </p>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">新增操作工作流ID</label>
                  <Input
                    value={cozeWorkflowIdInsert}
                    onChange={(e) => setCozeWorkflowIdInsert(e.target.value)}
                    placeholder="新增操作的工作流ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    当数据新增时触发的工作流
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-medium">更新操作工作流ID</label>
                  <Input
                    value={cozeWorkflowIdUpdate}
                    onChange={(e) => setCozeWorkflowIdUpdate(e.target.value)}
                    placeholder="更新操作的工作流ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    当数据更新时触发的工作流
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-medium">删除操作工作流ID</label>
                  <Input
                    value={cozeWorkflowIdDelete}
                    onChange={(e) => setCozeWorkflowIdDelete(e.target.value)}
                    placeholder="删除操作的工作流ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    当数据删除时触发的工作流
                  </p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium">数据表选择</label>
                <Select value={selectedTable} onValueChange={setSelectedTable}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择要同步的数据表" />
                  </SelectTrigger>
                  <SelectContent>
                    {tables.map((table) => (
                      <SelectItem key={table.tableName} value={table.tableName}>
                        {table.displayName} ({table.recordCount} 条记录)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* 字段选择区域 */}
              {selectedTable && tableFields.length > 0 && (
                <div>
                  <label className="text-sm font-medium">选择同步字段</label>
                  <div className="mt-2 p-4 border border-gray-200 rounded-lg bg-gray-50 max-h-60 overflow-y-auto">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">字段列表</span>
                      <div className="flex space-x-2">
                        <Button 
                          type="button" 
                          variant="outline" 
                          size="sm"
                          onClick={() => setSelectedFields(tableFields.map(field => field.fieldName))}
                        >
                          全选
                        </Button>
                        <Button 
                          type="button" 
                          variant="outline" 
                          size="sm"
                          onClick={() => setSelectedFields([])}
                        >
                          全不选
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {tableFields.map((field) => (
                        <div key={field.fieldName} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`field-${field.fieldName}`}
                            checked={selectedFields.includes(field.fieldName)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedFields(prev => [...prev, field.fieldName]);
                              } else {
                                setSelectedFields(prev => prev.filter(f => f !== field.fieldName));
                              }
                            }}
                            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <label 
                            htmlFor={`field-${field.fieldName}`}
                            className="text-sm flex-1 cursor-pointer"
                            title={field.description}
                          >
                            <span className="font-medium">{field.displayName}</span>
                            <span className="text-gray-500 ml-2 text-xs">({field.fieldType})</span>
                            {field.isRequired && (
                              <span className="text-red-500 ml-1 text-xs">*</span>
                            )}
                          </label>
                        </div>
                      ))}
                    </div>
                    
                    {/* 确认按钮 */}
                    <div className="mt-4 flex justify-center">
                      <Button 
                        type="button" 
                        variant="default" 
                        size="sm"
                        onClick={confirmSelectedFields}
                        disabled={selectedFields.length === 0}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        确认添加所选字段
                      </Button>
                    </div>
                  </div>
                  
                  {/* API请求头显示框 */}
                  {showRequestHeaders && confirmedFields.length > 0 && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium">Coze API同步模板</label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            // 切换显示模板预览或测试数据传输
                            if (showTemplatePreview) {
                              // 切换到测试数据传输模式
                              setShowTemplatePreview(false);
                              fetchSampleData(selectedTable, confirmedFields, false);
                            } else {
                              // 切换到模板预览模式
                              setShowTemplatePreview(true);
                              generateRequestTemplate(confirmedFields);
                            }
                          }}
                        >
                          {showTemplatePreview ? (
                            <>
                              <Database className="h-4 w-4 mr-2" />
                              测试数据传输
                            </>
                          ) : (
                            <>
                              <FileText className="h-4 w-4 mr-2" />
                              查看模板
                            </>
                          )}
                        </Button>
                      </div>
                      <div className="mt-2 p-4 border border-gray-200 rounded-lg bg-gray-50">
                        <div className="text-sm font-mono bg-white p-3 rounded border">
                            <div className="text-blue-600">POST {cozeApiUrl ? `${cozeApiUrl}/v1/workflow/run` : 'https://api.coze.cn/v1/workflow/run'}</div>
                            <div className="text-green-600">Authorization: Bearer {globalCozeApiKey || '{API密钥}'}</div>
                            <div className="text-purple-600">Content-Type: application/json</div>
                            <div className="text-orange-600 mt-2">请求体:</div>
                            <div className="ml-4 text-gray-700">
                              <div>{'{'}</div>
                              <div className="ml-4">"workflow_id": "{cozeWorkflowIdInsert || cozeWorkflowIdUpdate || cozeWorkflowIdDelete || '{工作流ID}'}",</div>
                              <div className="ml-4">// 系统会根据操作类型自动选择对应的工作流ID</div>
                              <div className="ml-4">// 新增操作: {cozeWorkflowIdInsert || '未设置'} {cozeWorkflowIdInsert ? '(已设置)' : ''}</div>
                              <div className="ml-4">// 更新操作: {cozeWorkflowIdUpdate || '未设置'} {cozeWorkflowIdUpdate ? '(已设置)' : ''}</div>
                              <div className="ml-4">// 删除操作: {cozeWorkflowIdDelete || '未设置'} {cozeWorkflowIdDelete ? '(已设置)' : ''}</div>
                              <div className="ml-4">// 注意：实际同步时会根据操作类型自动选择对应的工作流ID</div>
                              <div className="ml-4">"parameters": {'{'}</div>
                              {showTemplatePreview ? (
                                // 显示模板 - 使用蛇形命名作为变量名，不带数据
                                confirmedFields.map((field, fieldIndex) => {
                                  // 字段映射：将uuid映射为user_id，避免与Coze数据库中的uuid字段冲突
                                  const mappedFieldName = field === 'uuid' ? 'user_id' : field;
                                  // 使用蛇形命名作为变量名，表示这些字段将在同步时从数据库动态获取
                                  return (
                                    <div key={field} className="ml-8">
                                      "{mappedFieldName}": "[{mappedFieldName}]"{fieldIndex < confirmedFields.length - 1 ? ',' : ''}
                                    </div>
                                  );
                                })
                              ) : (
                                // 显示样本数据用于测试
                                sampleData.length > 0 ? (
                                  sampleData.map((record, recordIndex) => (
                                    <div key={recordIndex}>
                                      <div className="ml-6 text-blue-600">// 第{recordIndex + 1}条数据</div>
                                      {confirmedFields.map((field, fieldIndex) => {
                                        const rawValue = record[field] !== undefined ? record[field] : "";
                                        // 安全处理值：如果是对象，转换为JSON字符串；如果是其他类型，转换为字符串
                                        const value = typeof rawValue === 'object' && rawValue !== null 
                                          ? JSON.stringify(rawValue) 
                                          : String(rawValue);
                                        // 字段映射：将uuid映射为user_id，避免与Coze数据库中的uuid字段冲突
                                        const mappedFieldName = field === 'uuid' ? 'user_id' : field;
                                        return (
                                          <div key={field} className="ml-8">
                                            "{mappedFieldName}": "{value}"{fieldIndex < confirmedFields.length - 1 ? ',' : ''}
                                          </div>
                                        );
                                      })}
                                      {recordIndex < sampleData.length - 1 && (
                                        <div className="ml-6 text-gray-500">,</div>
                                      )}
                                    </div>
                                  ))
                                ) : (
                                  // 如果没有样本数据，显示占位符
                                  confirmedFields.map((field, fieldIndex) => {
                                    let placeholder = "[真实数据]";
                                    if (field.includes('uuid') || field.includes('id')) {
                                      placeholder = "[UUID值]";
                                    } else if (field.includes('price') || field.includes('quantity')) {
                                      placeholder = "[数值]";
                                    } else if (field.includes('name') || field.includes('code')) {
                                      placeholder = "[文本值]";
                                    } else if (field.includes('date') || field.includes('time') || field.includes('at')) {
                                      placeholder = "[时间值]";
                                    }
                                    const mappedFieldName = field === 'uuid' ? 'user_id' : field;
                                    return (
                                      <div key={field} className="ml-8">
                                        "{mappedFieldName}": "{placeholder}"{fieldIndex < confirmedFields.length - 1 ? ',' : ''}
                                      </div>
                                    );
                                  })
                                )
                              )}
                              <div className="ml-4">{'}'}</div>
                              <div>{'}'}</div>
                            </div>
                          </div>
                        <div className="mt-2 text-xs text-gray-500">
                          {showTemplatePreview 
                            ? `已生成同步模板，${confirmedFields.length} 个字段将在同步时从数据库动态获取数据`
                            : `已确认 ${confirmedFields.length} 个字段将作为独立参数添加到API请求的parameters中`
                          }
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            

          </div>
          
          <DialogFooter>
            <div className="flex items-center justify-between w-full">
              <Button
                variant="outline"
                onClick={testDataTransfer}
                disabled={testingConnection || confirmedFields.length === 0}
              >
                {testingConnection ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    测试中...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    测试传输
                  </>
                )}
              </Button>
              
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                >
                  取消
                </Button>
                <Button
                  onClick={createSyncConfig}
                  disabled={loading || !selectedTable || (!cozeWorkflowIdInsert && !cozeWorkflowIdUpdate && !cozeWorkflowIdDelete) || !cozeApiUrl || confirmedFields.length === 0}
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      创建中...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      创建同步配置
                    </>
                  )}
                </Button>
              </div>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑同步配置对话框 */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>编辑同步配置</DialogTitle>
            <DialogDescription>
              修改同步配置的数据表、字段选择、工作流ID和标题
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* 基础配置区域 */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">基础配置</h3>
              
              <div>
                <label className="text-sm font-medium">配置标题</label>
                <Input
                  value={configTitle}
                  onChange={(e) => setConfigTitle(e.target.value)}
                  placeholder="输入同步配置标题（如：用户数据同步到Coze）"
                />
                <p className="text-xs text-gray-500 mt-1">
                  用于区分不同的同步配置，如果不填写将自动生成
                </p>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">新增操作工作流ID</label>
                  <Input
                    value={cozeWorkflowIdInsert}
                    onChange={(e) => setCozeWorkflowIdInsert(e.target.value)}
                    placeholder="新增操作的工作流ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    当数据新增时触发的工作流
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-medium">更新操作工作流ID</label>
                  <Input
                    value={cozeWorkflowIdUpdate}
                    onChange={(e) => setCozeWorkflowIdUpdate(e.target.value)}
                    placeholder="更新操作的工作流ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    当数据更新时触发的工作流
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-medium">删除操作工作流ID</label>
                  <Input
                    value={cozeWorkflowIdDelete}
                    onChange={(e) => setCozeWorkflowIdDelete(e.target.value)}
                    placeholder="删除操作的工作流ID"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    当数据删除时触发的工作流
                  </p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium">数据表选择</label>
                <Select value={selectedTable} onValueChange={setSelectedTable}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择要同步的数据表" />
                  </SelectTrigger>
                  <SelectContent>
                    {tables.map((table) => (
                      <SelectItem key={table.tableName} value={table.tableName}>
                        {table.displayName} ({table.recordCount} 条记录)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* 字段选择区域 */}
              {selectedTable && tableFields.length > 0 && (
                <div>
                  <label className="text-sm font-medium">选择同步字段</label>
                  <div className="mt-2 p-4 border border-gray-200 rounded-lg bg-gray-50 max-h-60 overflow-y-auto">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">字段列表</span>
                      <div className="flex space-x-2">
                        <Button 
                          type="button" 
                          variant="outline" 
                          size="sm"
                          onClick={() => setSelectedFields(tableFields.map(field => field.fieldName))}
                        >
                          全选
                        </Button>
                        <Button 
                          type="button" 
                          variant="outline" 
                          size="sm"
                          onClick={() => setSelectedFields([])}
                        >
                          全不选
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {tableFields.map((field) => (
                        <div key={field.fieldName} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`edit-field-${field.fieldName}`}
                            checked={selectedFields.includes(field.fieldName)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedFields(prev => [...prev, field.fieldName]);
                              } else {
                                setSelectedFields(prev => prev.filter(f => f !== field.fieldName));
                              }
                            }}
                            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <label 
                            htmlFor={`edit-field-${field.fieldName}`}
                            className="text-sm flex-1 cursor-pointer"
                            title={field.description}
                          >
                            <span className="font-medium">{field.displayName}</span>
                            <span className="text-gray-500 ml-2 text-xs">({field.fieldType})</span>
                            {field.isRequired && (
                              <span className="text-red-500 ml-1 text-xs">*</span>
                            )}
                          </label>
                        </div>
                      ))}
                    </div>
                    
                    {/* 确认按钮 */}
                    <div className="mt-4 flex justify-center">
                      <Button 
                        type="button" 
                        variant="default" 
                        size="sm"
                        onClick={confirmSelectedFields}
                        disabled={selectedFields.length === 0}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        确认添加所选字段
                      </Button>
                    </div>
                  </div>
                  
                  {/* API请求头显示框 */}
                  {showRequestHeaders && confirmedFields.length > 0 && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium">Coze API请求头</label>
                        <div className="flex space-x-2">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              if (showTemplatePreview) {
                                // 切换到测试数据传输模式
                                setShowTemplatePreview(false);
                                fetchSampleData(selectedTable, confirmedFields, false);
                              } else {
                                // 切换到模板预览模式
                                setShowTemplatePreview(true);
                                generateRequestTemplate(confirmedFields);
                              }
                            }}
                          >
                            {showTemplatePreview ? (
                              <>
                                <Database className="h-4 w-4 mr-2" />
                                测试数据传输
                              </>
                            ) : (
                              <>
                                <FileText className="h-4 w-4 mr-2" />
                                查看模板
                              </>
                            )}
                          </Button>
                          {!showTemplatePreview && (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setShowAllData(!showAllData);
                                // 重新获取数据以更新显示
                                fetchSampleData(selectedTable, confirmedFields, !showAllData);
                              }}
                            >
                              {showAllData ? (
                                <>
                                  <Minus className="h-4 w-4 mr-2" />
                                  显示样本数据(3条)
                                </>
                              ) : (
                                <>
                                  <Plus className="h-4 w-4 mr-2" />
                                  显示所有数据
                                </>
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                      <div className="mt-2 p-4 border border-gray-200 rounded-lg bg-gray-50">
                        <div className="text-sm font-mono bg-white p-3 rounded border">
                            <div className="text-blue-600">POST {cozeApiUrl ? `${cozeApiUrl}/v1/workflow/run` : 'https://api.coze.cn/v1/workflow/run'}</div>
                            <div className="text-green-600">Authorization: Bearer {globalCozeApiKey || '{API密钥}'}</div>
                            <div className="text-purple-600">Content-Type: application/json</div>
                            <div className="text-orange-600 mt-2">请求体:</div>
                            <div className="ml-4 text-gray-700">
                              <div>{'{'}</div>
                              <div className="ml-4">"workflow_id": "{cozeWorkflowIdInsert || cozeWorkflowIdUpdate || cozeWorkflowIdDelete || '{工作流ID}'}",</div>
                              <div className="ml-4">// 系统会根据操作类型自动选择对应的工作流ID</div>
                              <div className="ml-4">// 新增操作: {cozeWorkflowIdInsert || '未设置'} {cozeWorkflowIdInsert ? '(已设置)' : ''}</div>
                              <div className="ml-4">// 更新操作: {cozeWorkflowIdUpdate || '未设置'} {cozeWorkflowIdUpdate ? '(已设置)' : ''}</div>
                              <div className="ml-4">// 删除操作: {cozeWorkflowIdDelete || '未设置'} {cozeWorkflowIdDelete ? '(已设置)' : ''}</div>
                              <div className="ml-4">// 注意：实际同步时会根据操作类型自动选择对应的工作流ID</div>
                              <div className="ml-4">"parameters": {'{'}</div>
                              {showTemplatePreview ? (
                                // 显示模板 - 使用蛇形命名作为变量名，不带数据
                                confirmedFields.map((field, fieldIndex) => {
                                  // 字段映射：将uuid映射为user_id，避免与Coze数据库中的uuid字段冲突
                                  const mappedFieldName = field === 'uuid' ? 'user_id' : field;
                                  // 使用蛇形命名作为变量名，表示这些字段将在同步时从数据库动态获取
                                  return (
                                    <div key={field} className="ml-8">
                                      "{mappedFieldName}": "[{mappedFieldName}]"{fieldIndex < confirmedFields.length - 1 ? ',' : ''}
                                    </div>
                                  );
                                })
                              ) : (
                                // 显示样本数据用于测试
                                sampleData.length > 0 ? (
                                  sampleData.map((record, recordIndex) => (
                                    <div key={recordIndex}>
                                      <div className="ml-6 text-blue-600">// 第{recordIndex + 1}条数据</div>
                                      {confirmedFields.map((field, fieldIndex) => {
                                        const rawValue = record[field] !== undefined ? record[field] : "";
                                        // 安全处理值：如果是对象，转换为JSON字符串；如果是其他类型，转换为字符串
                                        const value = typeof rawValue === 'object' && rawValue !== null 
                                          ? JSON.stringify(rawValue) 
                                          : String(rawValue);
                                        // 字段映射：将uuid映射为user_id，避免与Coze数据库中的uuid字段冲突
                                        const mappedFieldName = field === 'uuid' ? 'user_id' : field;
                                        return (
                                          <div key={field} className="ml-8">
                                            "{mappedFieldName}": "{value}"{fieldIndex < confirmedFields.length - 1 ? ',' : ''}
                                          </div>
                                        );
                                      })}
                                      {recordIndex < sampleData.length - 1 && (
                                        <div className="ml-6 text-gray-500">,</div>
                                      )}
                                    </div>
                                  ))
                                ) : (
                                  // 如果没有样本数据，显示占位符
                                  confirmedFields.map((field, fieldIndex) => {
                                    let placeholder = "[真实数据]";
                                    if (field.includes('uuid') || field.includes('id')) {
                                      placeholder = "[UUID值]";
                                    } else if (field.includes('price') || field.includes('quantity')) {
                                      placeholder = "[数值]";
                                    } else if (field.includes('name') || field.includes('code')) {
                                      placeholder = "[文本值]";
                                    } else if (field.includes('date') || field.includes('time') || field.includes('at')) {
                                      placeholder = "[时间值]";
                                    }
                                    const mappedFieldName = field === 'uuid' ? 'user_id' : field;
                                    return (
                                      <div key={field} className="ml-8">
                                        "{mappedFieldName}": "{placeholder}"{fieldIndex < confirmedFields.length - 1 ? ',' : ''}
                                      </div>
                                    );
                                  })
                                )
                              )}
                              <div className="ml-4">{'}'}</div>
                              <div>{'}'}</div>
                            </div>
                          </div>
                        <div className="mt-2 text-xs text-gray-500">
                          {showTemplatePreview 
                            ? `已生成同步模板，${confirmedFields.length} 个字段将在同步时从数据库动态获取数据`
                            : `已确认 ${confirmedFields.length} 个字段将作为独立参数添加到API请求的parameters中`
                          }
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <div className="flex items-center justify-between w-full">
              <Button
                variant="outline"
                onClick={testDataTransfer}
                disabled={testingConnection || confirmedFields.length === 0}
              >
                {testingConnection ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    测试中...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    测试传输
                  </>
                )}
              </Button>
              
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={handleCancelEdit}
                >
                  取消
                </Button>
                <Button
                  onClick={handleSaveEdit}
                  disabled={loading || !selectedTable || (!cozeWorkflowIdInsert && !cozeWorkflowIdUpdate && !cozeWorkflowIdDelete) || !cozeApiUrl || confirmedFields.length === 0}
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      保存中...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      保存更改
                    </>
                  )}
                </Button>
              </div>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 主要内容区域 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="config">同步配置管理</TabsTrigger>
          <TabsTrigger value="monitor">实时监控面板</TabsTrigger>
        </TabsList>

        {/* 同步配置标签页 */}
        <TabsContent value="config" className="space-y-6">
          {/* 页面标题和操作按钮 */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">同步配置管理</h2>
              <p className="text-muted-foreground">
                管理数据表与Coze工作流的同步配置
              </p>
            </div>
            <Button 
              onClick={() => {
                setDialogOpen(true);
                resetDialogState();
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Plus className="h-4 w-4 mr-2" />
              添加同步配置
            </Button>
          </div>

          <Separator />

          {syncConfigs.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <Database className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">暂无同步配置</h3>
                <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                  点击"添加同步配置"按钮设置数据表与Coze工作流的实时同步
                </p>
                <Button 
                  onClick={() => {
                    setDialogOpen(true);
                    resetDialogState();
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  创建第一个配置
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* 配置列表表格 */}
              <Card>
                <CardHeader>
                  <CardTitle>同步配置列表</CardTitle>
                  <div className="text-sm text-muted-foreground">
                    共 {syncConfigs.length} 个同步配置
                  </div>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[300px]">配置名称</TableHead>
                        <TableHead>数据表</TableHead>
                        <TableHead>工作流ID</TableHead>
                        <TableHead>状态</TableHead>
                        <TableHead>同步统计</TableHead>
                        <TableHead>最后同步</TableHead>
                        <TableHead className="text-right">操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {syncConfigs.map((config) => {
                        const { icon: StatusIcon, color, text } = getSyncStatusConfig(config.status || 'INACTIVE');
                        
                        return (
                          <TableRow key={config.uuid}>
                            <TableCell className="font-medium">
                              <div className="flex items-center">
                                <StatusIcon className={`h-4 w-4 mr-2 ${color}`} />
                                {config.configTitle || `${config.tableName} - 实时同步`}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="font-mono text-sm">{config.tableName}</div>
                            </TableCell>
                            <TableCell>
                              <div className="font-mono text-xs max-w-[120px] truncate">
                                {config.cozeWorkflowId}
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge className={color}>
                                {text}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="space-y-1">
                                <div className="flex items-center text-xs">
                                  <span className="text-muted-foreground mr-2">总计:</span>
                                  <span className="font-medium">{config.totalSyncCount || 0}</span>
                                </div>
                                <div className="flex items-center text-xs">
                                  <span className="text-green-600 mr-2">✓</span>
                                  <span className="text-green-600">{config.successSyncCount || 0}</span>
                                  <span className="text-muted-foreground mx-1">/</span>
                                  <span className="text-red-600 mr-2">✗</span>
                                  <span className="text-red-600">{config.failedSyncCount || 0}</span>
                                </div>
                                <div className="flex items-center text-xs">
                                  <span className="text-blue-400 mr-1">+{config.insertSyncCount || 0}</span>
                                  <span className="text-purple-400 mr-1">↻{config.updateSyncCount || 0}</span>
                                  <span className="text-amber-400">-{config.deleteSyncCount || 0}</span>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="text-xs">
                                {config.lastSyncTime ? (
                                  <>
                                    <div className="font-medium">
                                      {new Date(config.lastSyncTime).toLocaleDateString()}
                                    </div>
                                    <div className="text-muted-foreground">
                                      {new Date(config.lastSyncTime).toLocaleTimeString()}
                                    </div>
                                  </>
                                ) : (
                                  <span className="text-muted-foreground">尚未同步</span>
                                )}
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex items-center justify-end space-x-2">
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => handleEditConfig(config)}
                                  title="编辑配置"
                                >
                                  <Sliders className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => handleManualSync(config.uuid)}
                                  disabled={config.status !== 'ACTIVE'}
                                  title="手动同步"
                                >
                                  <RefreshCw className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => deleteSyncConfig(config.uuid)}
                                  title="删除配置"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              {/* 详细统计卡片 */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {syncConfigs.map((config) => {
                  const { icon: StatusIcon, color, text } = getSyncStatusConfig(config.status || 'INACTIVE');
                  
                  return (
                    <Card key={config.uuid} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-base flex items-center">
                            <StatusIcon className={`h-4 w-4 mr-2 ${color}`} />
                            {config.configTitle || config.tableName}
                          </CardTitle>
                          <Badge className={color}>
                            {text}
                          </Badge>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          工作流ID: {config.cozeWorkflowId}
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="space-y-3">
                          {/* 基础信息 */}
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <div className="text-muted-foreground">创建时间</div>
                              <div className="font-medium">
                                {config.createdAt ? new Date(config.createdAt).toLocaleDateString() : '-'}
                              </div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">最后同步</div>
                              <div className="font-medium">
                                {config.lastSyncTime ? new Date(config.lastSyncTime).toLocaleDateString() : '无'}
                              </div>
                            </div>
                          </div>
                          
                          {/* 同步类型和时间 */}
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <div className="text-muted-foreground">最后同步类型</div>
                              <div className="font-medium">
                                {config.lastSyncType ? (
                                  config.lastSyncType === 'MANUAL' ? '手动同步' :
                                  config.lastSyncType === 'AUTO_INSERT' ? '自动新增' :
                                  config.lastSyncType === 'AUTO_UPDATE' ? '自动更新' :
                                  config.lastSyncType === 'AUTO_DELETE' ? '自动删除' : config.lastSyncType
                                ) : '无'}
                              </div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">最后手动同步</div>
                              <div className="font-medium">
                                {config.lastManualSyncTime ? new Date(config.lastManualSyncTime).toLocaleDateString() : '无'}
                              </div>
                            </div>
                          </div>

                          {/* 同步统计 */}
                          <div className="space-y-2">
                            <div className="grid grid-cols-3 gap-2 text-xs">
                              <div className="text-center">
                                <div className="text-muted-foreground">总计</div>
                                <div className="font-medium">{config.totalSyncCount || 0}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-green-600">成功</div>
                                <div className="font-medium text-green-600">{config.successSyncCount || 0}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-red-600">失败</div>
                                <div className="font-medium text-red-600">{config.failedSyncCount || 0}</div>
                              </div>
                            </div>
                            
                            {/* 详细操作统计 */}
                            <div className="grid grid-cols-3 gap-2 text-xs">
                              <div className="text-center">
                                <div className="text-blue-400">新增</div>
                                <div className="font-medium text-blue-400">{config.insertSyncCount || 0}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-purple-400">更新</div>
                                <div className="font-medium text-purple-400">{config.updateSyncCount || 0}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-amber-400">删除</div>
                                <div className="font-medium text-amber-400">{config.deleteSyncCount || 0}</div>
                              </div>
                            </div>
                          </div>

                          {/* 手动/自动统计 */}
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="text-center">
                              <div className="text-blue-600">手动</div>
                              <div className="font-medium text-blue-600">{config.manualSyncCount || 0}</div>
                            </div>
                            <div className="text-center">
                              <div className="text-orange-600">自动</div>
                              <div className="font-medium text-orange-600">{config.autoSyncCount || 0}</div>
                            </div>
                          </div>

                          {/* 操作按钮 */}
                          <div className="flex space-x-2 pt-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="flex-1"
                              onClick={() => handleEditConfig(config)}
                            >
                              <Sliders className="h-3 w-3 mr-1" />
                              编辑
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="flex-1"
                              onClick={() => handleManualSync(config.uuid)}
                              disabled={config.status !== 'ACTIVE'}
                            >
                              <RefreshCw className="h-3 w-3 mr-1" />
                              同步
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </TabsContent>

        {/* 同步监控标签页 */}
        <TabsContent value="monitor" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>实时同步监控</CardTitle>
              <p className="text-sm text-muted-foreground">
                监控当前正在进行的同步任务和最近的活动记录
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* 当前活动任务 */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">当前活动任务</h3>
                  <div className="bg-muted/50 rounded-lg p-4 text-center">
                    <p className="text-muted-foreground">暂无正在进行的同步任务</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      当有同步任务执行时，这里会显示实时进度和状态
                    </p>
                  </div>
                </div>
                
                {/* 最近同步活动 */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">最近同步活动</h3>
                  <div className="space-y-3">
                    {syncConfigs.filter(config => config.lastSyncTime).slice(0, 5).map((config) => (
                      <div key={config.uuid} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 rounded-full bg-green-500"></div>
                          <div>
                            <div className="font-medium">{config.tableName}</div>
                            <div className="text-sm text-muted-foreground">
                              最后同步: {config.lastSyncTime ? new Date(config.lastSyncTime).toLocaleString() : '尚未同步'}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">
                            {config.lastSyncType === 'MANUAL' ? '手动同步' : '自动同步'}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            成功: {config.successSyncCount || 0}
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {syncConfigs.filter(config => config.lastSyncTime).length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-muted-foreground">暂无同步活动记录</p>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* 同步统计概览 */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">同步统计概览</h3>
                  <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {syncConfigs.reduce((sum, config) => sum + (config.manualSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">手动同步</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">
                        {syncConfigs.reduce((sum, config) => sum + (config.autoSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">自动同步</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {syncConfigs.reduce((sum, config) => sum + (config.successSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">成功次数</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-red-600">
                        {syncConfigs.reduce((sum, config) => sum + (config.failedSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">失败次数</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-400">
                        {syncConfigs.reduce((sum, config) => sum + (config.insertSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">新增操作</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-purple-400">
                        {syncConfigs.reduce((sum, config) => sum + (config.updateSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">更新操作</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-amber-400">
                        {syncConfigs.reduce((sum, config) => sum + (config.deleteSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">删除操作</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-gray-600">
                        {syncConfigs.reduce((sum, config) => sum + (config.totalSyncCount || 0), 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">总操作数</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-indigo-400">
                        {syncConfigs.filter(config => config.lastSyncTime).length}
                      </div>
                      <div className="text-sm text-muted-foreground">活跃配置</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-teal-400">
                        {syncConfigs.filter(config => config.status === 'ACTIVE').length}
                      </div>
                      <div className="text-sm text-muted-foreground">启用配置</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CozeUploadPage;