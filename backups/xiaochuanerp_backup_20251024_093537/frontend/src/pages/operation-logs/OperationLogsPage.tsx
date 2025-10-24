import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Filter, Search, Download, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { operationLogApi } from '@/services/api/operationLogs';

interface OperationLog {
  uuid: string;
  operation_type: string;
  operation_module: string;
  operation_description: string;
  target_uuid?: string;
  target_name?: string;
  operator_uuid: string;
  operator_name: string;
  operator_ip?: string;
  operation_status: string;
  error_message?: string;
  operation_time: string;
  created_at: string;
}

interface OperationLogsResponse {
  items: OperationLog[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

interface FilterParams {
  operation_type?: string;
  operation_module?: string;
  operator_name?: string;
  target_name?: string;
  operation_status?: string;
  start_date?: Date;
  end_date?: Date;
  page: number;
  size: number;
}

const OperationLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<OperationLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<FilterParams>({
    page: 1,
    size: 20
  });
  const [pagination, setPagination] = useState({
    total: 0,
    pages: 0
  });

  // 操作类型选项
  const operationTypes = [
    { value: 'CREATE', label: '创建' },
    { value: 'UPDATE', label: '更新' },
    { value: 'DELETE', label: '删除' },
    { value: 'VIEW', label: '查看' },
    { value: 'EXPORT', label: '导出' },
    { value: 'IMPORT', label: '导入' }
  ];

  // 操作模块选项
  const operationModules = [
    { value: 'products', label: '产品管理' },
    { value: 'suppliers', label: '供应商管理' },
    { value: 'inventory', label: '库存管理' },
    { value: 'purchase_orders', label: '采购订单' },
    { value: 'sales_orders', label: '销售订单' },
    { value: 'customers', label: '客户管理' },
    { value: 'users', label: '用户管理' }
  ];

  // 操作状态选项
  const operationStatuses = [
    { value: 'SUCCESS', label: '成功' },
    { value: 'FAILED', label: '失败' }
  ];

  // 获取操作日志
  const fetchOperationLogs = async () => {
    setLoading(true);
    try {
      const response = await operationLogApi.getOperationLogs(filters);
      if (response.success) {
        setLogs(response.data.items);
        setPagination({
          total: response.data.total,
          pages: response.data.pages
        });
      }
    } catch (error) {
      console.error('获取操作日志失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    fetchOperationLogs();
  }, [filters.page]);

  // 处理筛选条件变化
  const handleFilterChange = (key: keyof FilterParams, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      // 只有当改变的不是页码时，才重置到第一页
      page: key === 'page' ? value : 1
    }));
  };

  // 重置筛选条件
  const handleResetFilters = () => {
    setFilters({
      page: 1,
      size: 20
    });
  };

  // 获取状态对应的颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-green-100 text-green-800';
      case 'FAILED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // 获取类型对应的中文
  const getTypeLabel = (type: string) => {
    const typeObj = operationTypes.find(t => t.value === type);
    return typeObj ? typeObj.label : type;
  };

  // 获取模块对应的中文
  const getModuleLabel = (module: string) => {
    const moduleObj = operationModules.find(m => m.value === module);
    return moduleObj ? moduleObj.label : module;
  };

  // 格式化时间
  const formatDateTime = (dateString: string) => {
    // 将UTC时间转换为上海时区时间
    const utcDate = new Date(dateString);
    const shanghaiDate = new Date(utcDate.getTime() + 8 * 60 * 60 * 1000); // UTC+8
    return format(shanghaiDate, 'yyyy-MM-dd HH:mm:ss');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">操作日志</h1>
          <p className="text-muted-foreground">
            查看系统的所有操作记录，包含时间、操作者和操作详情
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={fetchOperationLogs} disabled={loading}>
            <RefreshCw className={cn('h-4 w-4 mr-2', loading && 'animate-spin')} />
            刷新
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            导出
          </Button>
        </div>
      </div>

      {/* 筛选条件 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            筛选条件
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 操作类型筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">操作类型</label>
              <Select
                value={filters.operation_type || ''}
                onValueChange={(value) => handleFilterChange('operation_type', value === 'all' ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择操作类型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  {operationTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 操作模块筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">操作模块</label>
              <Select
                value={filters.operation_module || ''}
                onValueChange={(value) => handleFilterChange('operation_module', value === 'all' ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择操作模块" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  {operationModules.map(module => (
                    <SelectItem key={module.value} value={module.value}>
                      {module.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 操作状态筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">操作状态</label>
              <Select
                value={filters.operation_status || ''}
                onValueChange={(value) => handleFilterChange('operation_status', value === 'all' ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择操作状态" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  {operationStatuses.map(status => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 操作者筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">操作者</label>
              <Input
                placeholder="输入操作者姓名"
                value={filters.operator_name || ''}
                onChange={(e) => handleFilterChange('operator_name', e.target.value || undefined)}
              />
            </div>

            {/* 目标名称筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">目标名称</label>
              <Input
                placeholder="输入目标名称"
                value={filters.target_name || ''}
                onChange={(e) => handleFilterChange('target_name', e.target.value || undefined)}
              />
            </div>

            {/* 开始时间筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">开始时间</label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      'w-full justify-start text-left font-normal',
                      !filters.start_date && 'text-muted-foreground'
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {filters.start_date ? format(filters.start_date, 'yyyy-MM-dd') : '选择开始时间'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={filters.start_date}
                    onSelect={(date) => handleFilterChange('start_date', date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* 结束时间筛选 */}
            <div>
              <label className="text-sm font-medium mb-2 block">结束时间</label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      'w-full justify-start text-left font-normal',
                      !filters.end_date && 'text-muted-foreground'
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {filters.end_date ? format(filters.end_date, 'yyyy-MM-dd') : '选择结束时间'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={filters.end_date}
                    onSelect={(date) => handleFilterChange('end_date', date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="flex justify-end mt-4 space-x-2">
            <Button variant="outline" onClick={handleResetFilters}>
              重置
            </Button>
            <Button onClick={fetchOperationLogs} disabled={loading}>
              <Search className="h-4 w-4 mr-2" />
              搜索
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 操作日志表格 */}
      <Card>
        <CardHeader>
          <CardTitle>操作日志列表</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin" />
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>操作时间</TableHead>
                    <TableHead>操作类型</TableHead>
                    <TableHead>操作模块</TableHead>
                    <TableHead>操作描述</TableHead>
                    <TableHead>目标对象</TableHead>
                    <TableHead>操作者</TableHead>
                    <TableHead>IP地址</TableHead>
                    <TableHead>操作状态</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                        暂无操作日志记录
                      </TableCell>
                    </TableRow>
                  ) : (
                    logs.map((log) => (
                      <TableRow key={log.uuid}>
                        <TableCell className="font-medium">
                          {formatDateTime(log.operation_time)}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {getTypeLabel(log.operation_type)}
                          </Badge>
                        </TableCell>
                        <TableCell>{getModuleLabel(log.operation_module)}</TableCell>
                        <TableCell className="max-w-xs truncate">
                          {log.operation_description}
                        </TableCell>
                        <TableCell>
                          {log.target_name || '-'}
                        </TableCell>
                        <TableCell>{log.operator_name}</TableCell>
                        <TableCell>{log.operator_ip || '-'}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(log.operation_status)}>
                            {log.operation_status === 'SUCCESS' ? '成功' : '失败'}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>

              {/* 分页 */}
              {pagination.pages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    共 {pagination.total} 条记录，第 {filters.page} 页，共 {pagination.pages} 页
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      disabled={filters.page <= 1}
                      onClick={() => handleFilterChange('page', filters.page - 1)}
                    >
                      上一页
                    </Button>
                    <Button
                      variant="outline"
                      disabled={filters.page >= pagination.pages}
                      onClick={() => handleFilterChange('page', filters.page + 1)}
                    >
                      下一页
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default OperationLogsPage;