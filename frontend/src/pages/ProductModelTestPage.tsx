import React, { useState } from 'react';
import { apiClient } from '../services/api/client';

const ProductModelTestPage: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [testModelUuid, setTestModelUuid] = useState<string>('');

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  // 模拟原始的删除确认逻辑
  const handleDeleteModelOriginal = async (uuid: string) => {
    if (!window.confirm('确定要删除这个产品型号吗？')) return;
    
    try {
      await apiClient.deleteProductModel(uuid);
      addLog('删除成功');
    } catch (error) {
      addLog(`删除失败: ${error}`);
    }
  };

  // 模拟增强的删除确认逻辑
  const handleDeleteModelEnhanced = async (uuid: string) => {
    const confirmed = window.confirm('确定要删除这个产品型号吗？');
    
    if (!confirmed) {
      addLog('用户取消了删除操作');
      return;
    }
    
    try {
      addLog('开始删除产品型号...');
      await apiClient.deleteProductModel(uuid);
      addLog('删除成功');
    } catch (error) {
      addLog(`删除失败: ${error}`);
    }
  };

  // 创建测试型号
  const createTestModel = async () => {
    try {
      const testData = {
        modelName: `测试型号_${Date.now()}`,
        modelCode: `TEST_${Date.now()}`,
        categoryUuid: '', // 使用空字符串而不是null
        specifications: [] // 使用空数组而不是对象
      };
      
      const response = await apiClient.createProductModel(testData);
      setTestModelUuid(response.uuid);
      addLog(`创建测试型号成功: ${response.uuid}`);
    } catch (error) {
      addLog(`创建测试型号失败: ${error}`);
    }
  };

  // 测试编辑功能
  const testEditModel = async () => {
    if (!testModelUuid) {
      addLog('请先创建测试型号');
      return;
    }

    try {
      const updateData = {
        modelName: `更新后的型号_${Date.now()}`,
        specifications: [
          { key: 'description', value: '这是更新后的描述' },
          { key: 'weight', value: '2.5kg', unit: 'kg' }
        ] // 使用ProductSpecification数组
      };
      
      addLog('开始编辑测试型号...');
      const response = await apiClient.updateProductModel(testModelUuid, updateData);
      addLog('编辑成功');
    } catch (error) {
      addLog(`编辑失败: ${error}`);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">产品型号功能测试</h1>
      
      <div className="space-y-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">测试准备</h2>
          <button 
            onClick={createTestModel}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            创建测试型号
          </button>
          {testModelUuid && (
            <p className="mt-2 text-sm">测试型号UUID: {testModelUuid}</p>
          )}
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">编辑功能测试</h2>
          <button 
            onClick={testEditModel}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            disabled={!testModelUuid}
          >
            测试编辑功能
          </button>
        </div>

        <div className="bg-yellow-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">删除确认逻辑测试</h2>
          <div className="space-x-2">
            <button 
              onClick={() => handleDeleteModelOriginal(testModelUuid)}
              className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
              disabled={!testModelUuid}
            >
              测试原始删除逻辑
            </button>
            <button 
              onClick={() => handleDeleteModelEnhanced(testModelUuid)}
              className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
              disabled={!testModelUuid}
            >
              测试增强删除逻辑
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            点击按钮后，观察确认对话框的行为和日志输出
          </p>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">测试日志</h2>
          <div className="bg-white p-3 rounded border max-h-64 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500">暂无日志</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="text-sm font-mono py-1 border-b border-gray-100 last:border-b-0">
                  {log}
                </div>
              ))
            )}
          </div>
          <button 
            onClick={() => setLogs([])}
            className="mt-2 bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
          >
            清空日志
          </button>
        </div>

        <div className="bg-red-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">问题诊断</h2>
          <p className="text-sm text-gray-700 mb-2">
            如果删除确认逻辑有问题，请检查：
          </p>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• 浏览器控制台是否有错误信息</li>
            <li>• 确认对话框是否正常弹出</li>
            <li>• 点击"取消"后是否真的取消了删除操作</li>
            <li>• 网络请求是否只在确认后发送</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ProductModelTestPage;