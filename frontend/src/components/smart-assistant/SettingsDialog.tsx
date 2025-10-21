import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import DatabaseSelector from './DatabaseSelector';
import ModelSelector, { ModelConfig } from './ModelSelector';


import { Settings, Save, X } from 'lucide-react';

// 定义数据库配置接口（因为DatabaseSelector没有导出）
interface DatabaseConfig {
  id: string;
  name: string;
  type: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password?: string;
  schemaName?: string;
  status: 'connected' | 'disconnected' | 'error' | 'available';
}

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  
  // 数据库相关配置
  databases: DatabaseConfig[];
  selectedDatabase: string;
  onDatabaseSelect: (databaseId: string) => void;
  onDatabaseUpdate?: (database: DatabaseConfig) => void;
  connectionStatus: string;
  
  // AI模型相关配置
  models: ModelConfig[];
  selectedModel?: string;
  onModelSelect: (modelId: string) => void;
  onModelUpdate?: (modelId: string, updates: Partial<ModelConfig>) => void;
  

  

  
  // 保存设置回调
  onSave?: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({
  open,
  onOpenChange,
  
  databases,
  selectedDatabase,
  onDatabaseSelect,
  onDatabaseUpdate,
  connectionStatus,
  
  models,
  selectedModel,
  onModelSelect,
  onModelUpdate,
  

  

  
  onSave
}) => {
  
  const handleSave = () => {
    // 触发保存回调
    onSave?.();
    // 关闭弹窗
    onOpenChange(false);
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2 text-xl">
            <Settings className="w-6 h-6 text-blue-600" />
            <span>智能助手设置</span>
          </DialogTitle>
          <DialogDescription>
            配置数据库连接、AI模型和高级功能，优化智能助手的使用体验
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* 数据库配置部分 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
              数据库配置
            </h3>
            <DatabaseSelector
              databases={databases}
              selectedDatabase={selectedDatabase}
              onDatabaseSelect={onDatabaseSelect}
              onDatabaseUpdate={onDatabaseUpdate}
              connectionStatus={connectionStatus}
            />
          </div>

          {/* AI模型配置部分 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
              AI模型配置
            </h3>
            <ModelSelector
              models={models}
              selectedModel={selectedModel}
              onModelSelect={onModelSelect}
              onModelUpdate={onModelUpdate}
            />
          </div>




        </div>

        <DialogFooter className="flex justify-end space-x-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleCancel}
            className="flex items-center space-x-2"
          >
            <X className="w-4 h-4" />
            <span>取消</span>
          </Button>
          <Button
            onClick={handleSave}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
          >
            <Save className="w-4 h-4" />
            <span>保存设置</span>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default SettingsDialog;