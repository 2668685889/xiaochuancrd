import React, { useState } from 'react';
import { Save, RefreshCw, Bell, Shield, Database, Users } from 'lucide-react';

interface SystemSettings {
  companyName: string;
  currency: string;
  dateFormat: string;
  timeFormat: string;
  lowStockThreshold: number;
  enableEmailNotifications: boolean;
  enableSmsNotifications: boolean;
  backupFrequency: string;
}

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    companyName: '我的公司',
    currency: 'CNY',
    dateFormat: 'YYYY-MM-DD',
    timeFormat: 'HH:mm:ss',
    lowStockThreshold: 10,
    enableEmailNotifications: true,
    enableSmsNotifications: false,
    backupFrequency: 'daily'
  });

  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: parseInt(value) || 0
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMessage('系统设置已成功保存！');
    } catch (error) {
      setMessage('保存失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSettings({
      companyName: '我的公司',
      currency: 'CNY',
      dateFormat: 'YYYY-MM-DD',
      timeFormat: 'HH:mm:ss',
      lowStockThreshold: 10,
      enableEmailNotifications: true,
      enableSmsNotifications: false,
      backupFrequency: 'daily'
    });
    setMessage('设置已重置为默认值');
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">系统设置</h1>
        <p className="text-gray-600 mt-1">管理系统的基本配置和参数设置</p>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.includes('成功') ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'
        }`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 基本设置 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Shield className="w-5 h-5 text-primary-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">基本设置</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                公司名称
              </label>
              <input
                type="text"
                name="companyName"
                value={settings.companyName}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                货币单位
              </label>
              <select
                name="currency"
                value={settings.currency}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="CNY">人民币 (CNY)</option>
                <option value="USD">美元 (USD)</option>
                <option value="EUR">欧元 (EUR)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  日期格式
                </label>
                <select
                  name="dateFormat"
                  value={settings.dateFormat}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  时间格式
                </label>
                <select
                  name="timeFormat"
                  value={settings.timeFormat}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="HH:mm:ss">24小时制</option>
                  <option value="hh:mm:ss A">12小时制</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* 库存设置 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Database className="w-5 h-5 text-primary-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">库存设置</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                低库存预警阈值
              </label>
              <input
                type="number"
                name="lowStockThreshold"
                value={settings.lowStockThreshold}
                onChange={handleNumberChange}
                min="1"
                max="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">当库存数量低于此值时触发预警</p>
            </div>
          </div>
        </div>

        {/* 通知设置 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Bell className="w-5 h-5 text-primary-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">通知设置</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                name="enableEmailNotifications"
                checked={settings.enableEmailNotifications}
                onChange={handleInputChange}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label className="ml-2 text-sm text-gray-700">
                启用邮件通知
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="enableSmsNotifications"
                checked={settings.enableSmsNotifications}
                onChange={handleInputChange}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label className="ml-2 text-sm text-gray-700">
                启用短信通知
              </label>
            </div>
          </div>
        </div>

        {/* 数据设置 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Users className="w-5 h-5 text-primary-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">数据设置</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                数据备份频率
              </label>
              <select
                name="backupFrequency"
                value={settings.backupFrequency}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="daily">每日</option>
                <option value="weekly">每周</option>
                <option value="monthly">每月</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="mt-6 flex justify-end space-x-4">
        <button
          type="button"
          onClick={handleReset}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <RefreshCw className="w-4 h-4 mr-2 inline" />
          重置
        </button>
        
        <button
          type="button"
          onClick={handleSave}
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 inline animate-spin" />
              保存中...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2 inline" />
              保存设置
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default SettingsPage;