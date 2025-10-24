import React from 'react';
import { Button } from './button';
import { Database, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';

interface QuickAction {
  label: string;
  query: string;
  icon: React.ReactNode;
  color?: 'blue' | 'green' | 'orange' | 'purple';
}

interface QuickActionsProps {
  actions: QuickAction[];
  onActionClick: (query: string) => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ actions, onActionClick }) => {
  const getColorClasses = (color: string = 'blue') => {
    const colors = {
      blue: 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200',
      green: 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200',
      orange: 'bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-200',
      purple: 'bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      {actions.map((action, index) => (
        <Button
          key={index}
          variant="outline"
          className={`
            h-16 flex-col items-center justify-center gap-1 
            border-2 rounded-xl transition-all duration-200
            hover:scale-105 active:scale-95
            ${getColorClasses(action.color)}
          `}
          onClick={() => onActionClick(action.query)}
        >
          <div className="flex items-center gap-2">
            {action.icon}
            <span className="text-sm font-medium">{action.label}</span>
          </div>
        </Button>
      ))}
    </div>
  );
};

// 预定义的快速操作
const defaultActions: QuickAction[] = [
  {
    label: '今日销售统计',
    query: '请显示今日的销售统计',
    icon: <TrendingUp className="w-4 h-4" />,
    color: 'green'
  },
  {
    label: '库存预警',
    query: '哪些产品库存需要预警？',
    icon: <AlertTriangle className="w-4 h-4" />,
    color: 'orange'
  },
  {
    label: '热门产品',
    query: '最近一周哪些产品最受欢迎？',
    icon: <BarChart3 className="w-4 h-4" />,
    color: 'purple'
  },
  {
    label: '供应商分析',
    query: '分析各供应商的供货情况',
    icon: <Database className="w-4 h-4" />,
    color: 'blue'
  }
];

export { defaultActions };