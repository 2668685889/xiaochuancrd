import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api/client';
import { ProductModel, CreateProductModelRequest, ProductSpecification } from '../types';

const ProductModelDeleteTestPage: React.FC = () => {
  const [productModels, setProductModels] = useState<ProductModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<string[]>([]);
  const [testMode, setTestMode] = useState<'simulation' | 'real'>('simulation');

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  // 加载产品型号数据
  const loadProductModels = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getProductModels();
      setProductModels(response.items);
      addLog(`加载了 ${response.items.length} 个产品型号`);
    } catch (error) {
      addLog(`加载产品型号失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  // 模拟删除确认逻辑（用于测试）
  const simulateDeleteConfirmation = async (model: ProductModel) => {
    addLog(`开始模拟删除确认流程 - 型号: ${model.modelName}`);
    
    // 模拟事件对象
    const mockEvent = {
      preventDefault: () => addLog('✓ preventDefault() 被调用'),
      stopPropagation: () => addLog('✓ stopPropagation() 被调用'),
      stopImmediatePropagation: () => addLog('✓ stopImmediatePropagation() 被调用')
    };
    
    // 执行事件阻止
    mockEvent.preventDefault();
    mockEvent.stopPropagation();
    mockEvent.stopImmediatePropagation();
    
    // 显示确认对话框
    addLog('弹出确认对话框...');
    const confirmed = window.confirm(
      `确定要删除产品型号 "${model.modelName}" 吗？\n\n` +
      `型号编码: ${model.modelCode}\n` +
      `删除后将无法恢复！`
    );
    
    if (!confirmed) {
      addLog('❌ 用户取消了删除操作');
      return;
    }
    
    addLog('✅ 用户确认了删除操作');
    
    if (testMode === 'real') {
      // 执行真实的删除操作
      await performRealDelete(model.uuid);
    } else {
      // 模拟删除成功
      addLog('✅ 模拟删除操作成功完成');
      addLog('✅ 产品型号已从列表中移除（模拟）');
    }
  };

  // 执行真实的删除操作
  const performRealDelete = async (uuid: string) => {
    try {
      addLog('开始执行真实删除操作...');
      await apiClient.deleteProductModel(uuid);
      addLog('✅ 真实删除操作成功');
      
      // 重新加载数据
      await loadProductModels();
    } catch (error) {
      addLog(`❌ 删除操作失败: ${error}`);
    }
  };

  // 创建测试型号
  const createTestModel = async () => {
    try {
      const testData: CreateProductModelRequest = {
        modelName: `测试型号_${Date.now()}`,
        modelCode: `TEST_${Date.now()}`,
        description: '这是一个测试用的产品型号',
        categoryUuid: '',
        specifications: [
          { key: '处理器', value: 'Intel Core i7', unit: '' },
          { key: '内存', value: '16', unit: 'GB' },
          { key: '存储', value: '512', unit: 'GB SSD' }
        ]
      };
      
      addLog('开始创建测试型号...');
      await apiClient.createProductModel(testData);
      addLog('✅ 测试型号创建成功');
      
      // 重新加载数据
      await loadProductModels();
    } catch (error) {
      addLog(`❌ 创建测试型号失败: ${error}`);
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadProductModels();
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">产品型号删除确认功能测试</h1>
      
      {/* 测试控制面板 */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-4">测试设置</h2>
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">测试模式</label>
            <select 
              value={testMode} 
              onChange={(e) => setTestMode(e.target.value as 'simulation' | 'real')}
              className="input-field"
            >
              <option value="simulation">模拟模式（安全）</option>
              <option value="real">真实模式（实际删除）</option>
            </select>
          </div>
          
          <button 
            onClick={createTestModel}
            className="btn-primary"
          >
            创建测试型号
          </button>
          
          <button 
            onClick={loadProductModels}
            className="btn-secondary"
          >
            刷新数据
          </button>
          
          <button 
            onClick={() => setLogs([])}
            className="btn-secondary"
          >
            清空日志
          </button>
        </div>
        
        <div className="mt-2 text-sm text-gray-600">
          {testMode === 'simulation' ? (
            <span className="text-green-600">✅ 当前为模拟模式，删除操作不会实际执行</span>
          ) : (
            <span className="text-red-600">⚠️ 当前为真实模式，删除操作会实际执行</span>
          )}
        </div>
      </div>

      {/* 产品型号列表 */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">产品型号列表</h2>
          <p className="text-sm text-gray-600">点击删除按钮测试确认功能</p>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">加载中...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">型号信息</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">型号编码</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">描述</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {productModels.map((model) => (
                  <tr key={model.uuid} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{model.modelName}</div>
                      <div className="text-sm text-gray-500">
                        {model.categoryName || '未分类'}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <code className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">
                        {model.modelCode}
                      </code>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {model.description || '暂无描述'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          simulateDeleteConfirmation(model);
                        }}
                        className="btn-danger btn-sm"
                      >
                        测试删除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {productModels.length === 0 && (
              <div className="p-8 text-center text-gray-500">
                暂无产品型号数据
              </div>
            )}
          </div>
        )}
      </div>

      {/* 测试日志 */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-4">测试日志</h2>
        <div className="bg-white p-3 rounded border max-h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500">暂无日志记录</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="text-sm font-mono py-1 border-b border-gray-100 last:border-b-0">
                {log}
              </div>
            ))
          )}
        </div>
      </div>

      {/* 测试说明 */}
      <div className="bg-yellow-50 p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">测试说明</h2>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• 点击"测试删除"按钮会触发完整的删除确认流程</li>
          <li>• 模拟模式：不会实际删除数据，仅测试确认流程</li>
          <li>• 真实模式：会实际执行删除操作（谨慎使用）</li>
          <li>• 观察确认对话框是否正常弹出</li>
          <li>• 测试点击"取消"和"确定"的不同行为</li>
          <li>• 检查日志输出确认事件处理是否正确</li>
        </ul>
      </div>
    </div>
  );
};

export default ProductModelDeleteTestPage;