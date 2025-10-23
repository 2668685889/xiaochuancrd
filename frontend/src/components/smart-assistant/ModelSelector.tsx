import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Brain, Check, Zap, Cpu, Edit2, Save, X, Eye, EyeOff } from 'lucide-react';

export interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  model?: string;
  apiKey?: string;
  baseUrl?: string;
  apiDomain?: string;
  prompt?: string;
  status: 'available' | 'unavailable' | 'error';
  capabilities: string[];
  cost: 'free' | 'low' | 'medium' | 'high';
}

interface ModelSelectorProps {
  models: ModelConfig[];
  selectedModel?: string;
  onModelSelect: (modelId: string) => void;
  onModelUpdate?: (modelId: string, updates: Partial<ModelConfig>) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModel,
  onModelSelect,
  onModelUpdate
}) => {

  const [editingModel, setEditingModel] = useState<ModelConfig | null>(null);
  const [editingData, setEditingData] = useState<Partial<ModelConfig>>({});
  const [showApiKey, setShowApiKey] = useState(false);

  const handleEdit = (model: ModelConfig) => {
    setEditingModel(model);
    setEditingData({
      apiKey: model.apiKey || '',
      baseUrl: model.baseUrl || '',
      apiDomain: model.apiDomain || '',
      prompt: model.prompt || ''
    });
  };

  const handleSaveEdit = () => {
    if (editingModel && onModelUpdate) {
      onModelUpdate(editingModel.id, editingData);
    }
    setEditingModel(null);
    setEditingData({});
  };

  const handleCancelEdit = () => {
    setEditingModel(null);
    setEditingData({});
  };

  const handleEditingDataChange = (field: keyof ModelConfig, value: string) => {
    setEditingData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai': return '🤖';
      case 'aliyun': return '☁️';
      case 'baidu': return '🔍';
      case 'deepseek': return '🚀';
      case 'tencent': return '💬';
      case 'iflytek': return '✨';
      case 'google': return '🌐';
      case 'kimi': return '🔍';
      case 'tencent-cloud': return '☁️';
      case 'volcengine': return '🌋';
      case 'anthropic': return '🔮';
      case 'azure': return '☁️';
      case 'local': return '💻';
      default: return '⚡';
    }
  };

  const getProviderName = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai': return 'OpenAI';
      case 'aliyun': return '阿里云百炼';
      case 'baidu': return '千帆大模型';
      case 'deepseek': return 'DeepSeek';
      case 'tencent': return '腾讯混元';
      case 'iflytek': return '讯飞星火';
      case 'google': return 'Google';
      case 'kimi': return 'Kimi';
      case 'tencent-cloud': return '腾讯云';
      case 'volcengine': return '火山引擎';
      case 'anthropic': return 'Anthropic';
      case 'azure': return 'Azure';
      case 'local': return '本地部署';
      default: return provider;
    }
  };

  const getStatusColor = (status: ModelConfig['status']) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'unavailable': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: ModelConfig['status']) => {
    switch (status) {
      case 'available': return '可用';
      case 'unavailable': return '不可用';
      case 'error': return '错误';
      default: return '未知';
    }
  };

  const getCostColor = (cost: ModelConfig['cost']) => {
    switch (cost) {
      case 'free': return 'text-green-600';
      case 'low': return 'text-blue-600';
      case 'medium': return 'text-orange-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getCostText = (cost: ModelConfig['cost']) => {
    switch (cost) {
      case 'free': return '免费';
      case 'low': return '低成本';
      case 'medium': return '中等成本';
      case 'high': return '高成本';
      default: return '未知';
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <Brain className="w-5 h-5 text-purple-600" />
          <span>大模型选择</span>
        </CardTitle>
        <CardDescription>
          选择AI大语言模型，不同模型具有不同的能力和成本
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {models.length > 0 ? (
          models.map((model) => (
            <div
              key={model.id}
              className={`p-3 border rounded-lg transition-all duration-200 ${
                selectedModel === model.id
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              } ${model.status === 'unavailable' ? 'opacity-60' : ''}`}
            >
              {editingModel?.id === model.id ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="font-medium text-purple-800">配置API密钥</h4>
                    <div className="flex space-x-2">
                      <Button size="sm" onClick={handleSaveEdit} className="flex items-center space-x-1">
                        <Save className="w-3 h-3" />
                        <span>保存</span>
                      </Button>
                      <Button size="sm" variant="outline" onClick={handleCancelEdit} className="flex items-center space-x-1">
                        <X className="w-3 h-3" />
                        <span>取消</span>
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label htmlFor={`api-key-${model.id}`}>API密钥</Label>
                      <div className="relative">
                        <Input
                          id={`api-key-${model.id}`}
                          type={showApiKey ? "text" : "password"}
                          value={editingData.apiKey || ''}
                          onChange={(e) => handleEditingDataChange('apiKey', e.target.value)}
                          placeholder="请输入API密钥"
                          className="pr-10"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                          onClick={() => setShowApiKey(!showApiKey)}
                        >
                          {showApiKey ? (
                            <EyeOff className="h-4 w-4 text-gray-500" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-500" />
                          )}
                        </Button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor={`base-url-${model.id}`}>API基础地址</Label>
                      <Input
                        id={`base-url-${model.id}`}
                        value={editingData.baseUrl || ''}
                        onChange={(e) => handleEditingDataChange('baseUrl', e.target.value)}
                        placeholder="例如：https://api.openai.com/v1"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor={`api-domain-${model.id}`}>API域名</Label>
                      <Input
                        id={`api-domain-${model.id}`}
                        value={editingData.apiDomain || ''}
                        onChange={(e) => handleEditingDataChange('apiDomain', e.target.value)}
                        placeholder="例如：dashscope.aliyuncs.com"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor={`prompt-${model.id}`}>提示词</Label>
                      <textarea
                        id={`prompt-${model.id}`}
                        value={editingData.prompt || ''}
                        onChange={(e) => handleEditingDataChange('prompt', e.target.value)}
                        placeholder="请输入模型提示词，用于指导AI的回复行为"
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <div 
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => model.status === 'available' && onModelSelect(model.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{getProviderIcon(model.provider)}</div>
                      <div>
                        <div className="font-medium flex items-center space-x-2">
                          <span>{model.name}</span>
                          {selectedModel === model.id && (
                            <Check className="w-4 h-4 text-purple-600" />
                          )}
                        </div>
                        <div className="text-sm text-gray-500">
                          {getProviderName(model.provider)}{model.model ? ` • ${model.model}` : ''}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className={getStatusColor(model.status)}>
                        {getStatusText(model.status)}
                      </Badge>
                      <Badge variant="outline" className={getCostColor(model.cost)}>
                        {getCostText(model.cost)}
                      </Badge>
                      {onModelUpdate && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(model);
                          }}
                          className="flex items-center space-x-1"
                        >
                          <Edit2 className="w-3 h-3" />
                          <span>配置</span>
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-2 flex flex-wrap gap-1">
                    {model.capabilities.map((capability, index) => (
                      <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {capability}
                      </span>
                    ))}
                  </div>
                  
                  {model.status === 'unavailable' && (
                    <div className="mt-2 text-xs text-yellow-600">
                      需要配置API密钥或服务地址
                    </div>
                  )}
                </>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Brain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>暂无可用模型配置</p>
          </div>
        )}
        
        <div className="text-xs text-gray-500 space-y-1">
          <div className="flex items-center space-x-1">
            <Zap className="w-3 h-3" />
            <span>选择适合您需求的模型，考虑成本、性能和功能</span>
          </div>
          <div className="flex items-center space-x-1">
            <Cpu className="w-3 h-3" />
            <span>本地模型提供更好的数据安全性</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ModelSelector;