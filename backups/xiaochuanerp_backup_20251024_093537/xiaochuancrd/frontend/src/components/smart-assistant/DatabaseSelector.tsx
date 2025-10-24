import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Database, Settings, Check, Plus, Edit2, Save, X, Eye, EyeOff } from 'lucide-react';

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

interface DatabaseSelectorProps {
  databases: DatabaseConfig[];
  selectedDatabase: string;
  onDatabaseSelect: (databaseId: string) => void;
  onDatabaseUpdate: (database: DatabaseConfig) => void;
  onDatabaseCreate: (database: DatabaseConfig) => void;
  connectionStatus: string;
}

const DatabaseSelector: React.FC<DatabaseSelectorProps> = ({
  databases,
  selectedDatabase,
  onDatabaseSelect,
  onDatabaseUpdate,
  onDatabaseCreate,
  connectionStatus
}) => {
  const [editingDatabase, setEditingDatabase] = useState<DatabaseConfig | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newDatabase, setNewDatabase] = useState<Partial<DatabaseConfig>>({
    name: '',
    type: 'mysql',
    host: 'localhost',
    port: 3306,
    database: '',
    username: '',
    password: '',
    status: 'disconnected'
  });
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showEditingPassword, setShowEditingPassword] = useState(false);

  const getStatusColor = (status: DatabaseConfig['status']) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-800';
      case 'disconnected': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: DatabaseConfig['status']) => {
    switch (status) {
      case 'connected': return '已连接';
      case 'disconnected': return '未连接';
      case 'error': return '连接错误';
      default: return '未知状态';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'mysql': return '🐬';
      case 'postgresql': return '🐘';
      case 'postgres': return '🐘';
      case 'sqlite': return '💾';
      case 'oracle': return '🏢';
      default: return '🗄️';
    }
  };

  const handleEdit = (database: DatabaseConfig) => {
    setEditingDatabase({ ...database });
  };

  const handleSaveEdit = () => {
    if (editingDatabase) {
      onDatabaseUpdate(editingDatabase);
      setEditingDatabase(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingDatabase(null);
  };

  const handleCreate = () => {
    setIsCreating(true);
  };

  const handleSaveCreate = () => {
    if (newDatabase.name && newDatabase.host && newDatabase.database && newDatabase.username) {
      const database: DatabaseConfig = {
        id: Date.now().toString(),
        name: newDatabase.name!,
        type: newDatabase.type!,
        host: newDatabase.host!,
        port: newDatabase.port!,
        database: newDatabase.database!,
        username: newDatabase.username!,
        password: newDatabase.password || '',
        status: 'disconnected'
      };
      onDatabaseCreate(database);
      setIsCreating(false);
      setNewDatabase({
        name: '',
        type: 'mysql',
        host: 'localhost',
        port: 3306,
        database: '',
        username: '',
        password: '',
        status: 'disconnected'
      });
    }
  };

  const handleCancelCreate = () => {
    setIsCreating(false);
    setNewDatabase({
      name: '',
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      database: '',
      username: '',
      password: '',
      status: 'disconnected'
    });
  };

  const handleNewDatabaseChange = (field: keyof DatabaseConfig, value: string | number) => {
    setNewDatabase(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEditingDatabaseChange = (field: keyof DatabaseConfig, value: string | number) => {
    if (editingDatabase) {
      setEditingDatabase({
        ...editingDatabase,
        [field]: value
      });
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <Database className="w-5 h-5 text-blue-600" />
          <span>数据库选择</span>
        </CardTitle>
        <CardDescription>
          选择要查询的数据源，支持多种数据库类型
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* 创建新数据库配置 */}
        {isCreating && (
          <div className="p-4 border border-blue-300 rounded-lg bg-blue-50">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <h4 className="font-medium text-blue-800">创建新数据库配置</h4>
                <div className="flex space-x-2">
                  <Button size="sm" onClick={handleSaveCreate} className="flex items-center space-x-1">
                    <Save className="w-3 h-3" />
                    <span>保存</span>
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleCancelCreate} className="flex items-center space-x-1">
                    <X className="w-3 h-3" />
                    <span>取消</span>
                  </Button>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="new-name">配置名称</Label>
                  <Input
                    id="new-name"
                    value={newDatabase.name}
                    onChange={(e) => handleNewDatabaseChange('name', e.target.value)}
                    placeholder="例如：生产数据库"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-type">数据库类型</Label>
                  <Select value={newDatabase.type} onValueChange={(value) => handleNewDatabaseChange('type', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="mysql">MySQL</SelectItem>
                      <SelectItem value="postgresql">PostgreSQL</SelectItem>
                      <SelectItem value="sqlite">SQLite</SelectItem>
                      <SelectItem value="oracle">Oracle</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-host">主机地址</Label>
                  <Input
                    id="new-host"
                    value={newDatabase.host}
                    onChange={(e) => handleNewDatabaseChange('host', e.target.value)}
                    placeholder="localhost"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-port">端口</Label>
                  <Input
                    id="new-port"
                    type="number"
                    value={newDatabase.port}
                    onChange={(e) => handleNewDatabaseChange('port', parseInt(e.target.value) || 3306)}
                    placeholder="3306"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-database">数据库名</Label>
                  <Input
                    id="new-database"
                    value={newDatabase.database}
                    onChange={(e) => handleNewDatabaseChange('database', e.target.value)}
                    placeholder="数据库名称"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-username">用户名</Label>
                  <Input
                    id="new-username"
                    value={newDatabase.username}
                    onChange={(e) => handleNewDatabaseChange('username', e.target.value)}
                    placeholder="用户名"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="new-password">密码</Label>
                  <div className="relative">
                    <Input
                      id="new-password"
                      type={showNewPassword ? "text" : "password"}
                      value={newDatabase.password}
                      onChange={(e) => handleNewDatabaseChange('password', e.target.value)}
                      placeholder="密码"
                      className="pr-10"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                    >
                      {showNewPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-500" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-500" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 数据库配置列表 */}
        {databases.length > 0 ? (
          databases.map((db) => (
            <div
              key={db.id}
              className={`p-3 border rounded-lg transition-all duration-200 ${
                selectedDatabase === db.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {editingDatabase?.id === db.id ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="font-medium text-blue-800">编辑数据库配置</h4>
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
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label>配置名称</Label>
                      <Input
                        value={editingDatabase.name}
                        onChange={(e) => handleEditingDatabaseChange('name', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>数据库类型</Label>
                      <Select value={editingDatabase.type} onValueChange={(value) => handleEditingDatabaseChange('type', value)}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="mysql">MySQL</SelectItem>
                          <SelectItem value="postgresql">PostgreSQL</SelectItem>
                          <SelectItem value="sqlite">SQLite</SelectItem>
                          <SelectItem value="oracle">Oracle</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>主机地址</Label>
                      <Input
                        value={editingDatabase.host}
                        onChange={(e) => handleEditingDatabaseChange('host', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>端口</Label>
                      <Input
                        type="number"
                        value={editingDatabase.port}
                        onChange={(e) => handleEditingDatabaseChange('port', parseInt(e.target.value) || 3306)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>数据库名</Label>
                      <Input
                        value={editingDatabase.database}
                        onChange={(e) => handleEditingDatabaseChange('database', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>用户名</Label>
                      <Input
                        value={editingDatabase.username}
                        onChange={(e) => handleEditingDatabaseChange('username', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2 col-span-2">
                      <Label>密码</Label>
                      <div className="relative">
                        <Input
                          type={showEditingPassword ? "text" : "password"}
                          value={editingDatabase.password || ''}
                          onChange={(e) => handleEditingDatabaseChange('password', e.target.value)}
                          placeholder="留空则不修改密码"
                          className="pr-10"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                          onClick={() => setShowEditingPassword(!showEditingPassword)}
                        >
                          {showEditingPassword ? (
                            <EyeOff className="h-4 w-4 text-gray-500" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-500" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div 
                    className="flex items-center space-x-3 flex-1 cursor-pointer"
                    onClick={() => onDatabaseSelect(db.id)}
                  >
                    <div className="text-2xl">{getTypeIcon(db.type)}</div>
                    <div>
                      <div className="font-medium flex items-center space-x-2">
                        <span>{db.name}</span>
                        {selectedDatabase === db.id && (
                          <Check className="w-4 h-4 text-blue-600" />
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        {db.host}:{db.port}/{db.database}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary" className={getStatusColor(db.status)}>
                      {getStatusText(db.status)}
                    </Badge>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(db)}
                      className="flex items-center space-x-1"
                    >
                      <Edit2 className="w-3 h-3" />
                      <span>编辑</span>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Database className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>暂无可用数据库配置</p>
          </div>
        )}

        {/* 添加新数据库按钮 */}
        {!isCreating && (
          <Button
            onClick={handleCreate}
            variant="outline"
            className="w-full flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>添加新数据库配置</span>
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

export default DatabaseSelector;