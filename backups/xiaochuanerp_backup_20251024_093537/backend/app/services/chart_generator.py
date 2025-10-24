"""
图表生成引擎服务
将SQL查询结果转换为可视化图表
"""
import json
import logging
import base64
from io import BytesIO
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ChartGenerator:
    """图表生成引擎类"""
    
    def __init__(self):
        self.supported_chart_types = ['bar', 'line', 'pie', 'scatter', 'area']
        self.default_style = {
            'font_family': 'SimHei',  # 支持中文
            'font_size': 12,
            'figsize': (10, 6),
            'dpi': 100
        }
    
    async def generate_chart(self, data: List[Dict], chart_type: str = 'bar', 
                           title: str = "", x_label: str = "", y_label: str = "") -> Dict[str, Any]:
        """
        生成图表
        
        Args:
            data: 数据列表
            chart_type: 图表类型
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            
        Returns:
            包含图表信息的字典
        """
        try:
            if chart_type not in self.supported_chart_types:
                chart_type = 'bar'  # 默认使用柱状图
            
            # 创建图表
            plt.figure(figsize=self.default_style['figsize'])
            plt.rcParams['font.family'] = self.default_style['font_family']
            plt.rcParams['font.size'] = self.default_style['font_size']
            
            # 处理数据
            df = self._prepare_data(data)
            
            if df.empty:
                return {
                    'success': False,
                    'error': '没有有效数据可生成图表',
                    'chart_data': None
                }
            
            # 根据图表类型生成图表
            if chart_type == 'bar':
                chart_result = self._generate_bar_chart(df, title, x_label, y_label)
            elif chart_type == 'line':
                chart_result = self._generate_line_chart(df, title, x_label, y_label)
            elif chart_type == 'pie':
                chart_result = self._generate_pie_chart(df, title)
            elif chart_type == 'scatter':
                chart_result = self._generate_scatter_chart(df, title, x_label, y_label)
            elif chart_type == 'area':
                chart_result = self._generate_area_chart(df, title, x_label, y_label)
            else:
                chart_result = self._generate_bar_chart(df, title, x_label, y_label)
            
            # 保存图表为Base64编码
            chart_base64 = self._save_chart_to_base64()
            
            return {
                'success': True,
                'chart_type': chart_type,
                'title': title,
                'chart_data': chart_result,
                'chart_image': chart_base64,
                'data_summary': self._generate_data_summary(df)
            }
            
        except Exception as e:
            logger.error(f"图表生成失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'chart_data': None
            }
    
    def _prepare_data(self, data: List[Dict]) -> pd.DataFrame:
        """准备数据"""
        if not data:
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        
        # 清理数据
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        return df
    
    def _generate_bar_chart(self, df: pd.DataFrame, title: str, x_label: str, y_label: str) -> Dict[str, Any]:
        """生成柱状图"""
        # 自动选择数值列作为Y轴
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            # 如果没有数值列，使用第一列作为X轴，计数作为Y轴
            x_col = df.columns[0]
            y_data = df[x_col].value_counts().sort_index()
            plt.bar(y_data.index.astype(str), y_data.values)
            x_label = x_label or x_col
            y_label = y_label or '数量'
        else:
            # 使用第一个数值列作为Y轴
            y_col = numeric_columns[0]
            x_col = df.columns[0] if len(df.columns) > 1 else 'index'
            
            if x_col == 'index':
                plt.bar(range(len(df)), df[y_col])
                plt.xticks(range(len(df)), df.index.astype(str), rotation=45)
            else:
                plt.bar(df[x_col].astype(str), df[y_col])
            
            x_label = x_label or x_col
            y_label = y_label or y_col
        
        plt.title(title or '柱状图')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return {
            'type': 'bar',
            'x_label': x_label,
            'y_label': y_label,
            'data_points': len(df)
        }
    
    def _generate_line_chart(self, df: pd.DataFrame, title: str, x_label: str, y_label: str) -> Dict[str, Any]:
        """生成折线图"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            # 如果没有数值列，使用计数
            x_col = df.columns[0]
            y_data = df[x_col].value_counts().sort_index()
            plt.plot(y_data.index.astype(str), y_data.values, marker='o')
            x_label = x_label or x_col
            y_label = y_label or '数量'
        else:
            y_col = numeric_columns[0]
            x_col = df.columns[0] if len(df.columns) > 1 else 'index'
            
            if x_col == 'index':
                plt.plot(range(len(df)), df[y_col], marker='o')
                plt.xticks(range(len(df)), df.index.astype(str), rotation=45)
            else:
                plt.plot(df[x_col].astype(str), df[y_col], marker='o')
            
            x_label = x_label or x_col
            y_label = y_label or y_col
        
        plt.title(title or '折线图')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return {
            'type': 'line',
            'x_label': x_label,
            'y_label': y_label,
            'data_points': len(df)
        }
    
    def _generate_pie_chart(self, df: pd.DataFrame, title: str) -> Dict[str, Any]:
        """生成饼图"""
        # 使用第一列作为标签，第二列（如果有）作为数值
        if len(df.columns) >= 2:
            labels = df.iloc[:, 0].astype(str)
            values = df.iloc[:, 1]
        else:
            # 只有一个列，使用该列的计数
            value_counts = df.iloc[:, 0].value_counts()
            labels = value_counts.index.astype(str)
            values = value_counts.values
        
        # 限制显示数量，避免饼图过于拥挤
        if len(values) > 8:
            # 取前7个最大的，其余归为"其他"
            sorted_indices = np.argsort(values)[::-1]
            top_values = values.iloc[sorted_indices[:7]]
            other_value = values.iloc[sorted_indices[7:]].sum()
            
            values = pd.concat([top_values, pd.Series([other_value], index=['其他'])])
            labels = pd.concat([labels.iloc[sorted_indices[:7]], pd.Series(['其他'])])
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(title or '饼图')
        plt.axis('equal')  # 确保饼图是圆形
        plt.tight_layout()
        
        return {
            'type': 'pie',
            'categories': len(values),
            'total_value': values.sum()
        }
    
    def _generate_scatter_chart(self, df: pd.DataFrame, title: str, x_label: str, y_label: str) -> Dict[str, Any]:
        """生成散点图"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            return self._generate_bar_chart(df, title, x_label, y_label)
        
        x_col = numeric_columns[0]
        y_col = numeric_columns[1]
        
        plt.scatter(df[x_col], df[y_col], alpha=0.6)
        plt.title(title or '散点图')
        plt.xlabel(x_label or x_col)
        plt.ylabel(y_label or y_col)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return {
            'type': 'scatter',
            'x_label': x_label or x_col,
            'y_label': y_label or y_col,
            'data_points': len(df)
        }
    
    def _generate_area_chart(self, df: pd.DataFrame, title: str, x_label: str, y_label: str) -> Dict[str, Any]:
        """生成面积图"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            return self._generate_bar_chart(df, title, x_label, y_label)
        
        y_col = numeric_columns[0]
        x_col = df.columns[0] if len(df.columns) > 1 else 'index'
        
        if x_col == 'index':
            x_values = range(len(df))
            x_labels = df.index.astype(str)
        else:
            x_values = df[x_col].astype(str)
            x_labels = x_values
        
        plt.fill_between(range(len(df)), df[y_col], alpha=0.4)
        plt.plot(range(len(df)), df[y_col], marker='o', alpha=0.6)
        plt.title(title or '面积图')
        plt.xlabel(x_label or x_col)
        plt.ylabel(y_label or y_col)
        plt.xticks(range(len(df)), x_labels, rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return {
            'type': 'area',
            'x_label': x_label or x_col,
            'y_label': y_label or y_col,
            'data_points': len(df)
        }
    
    def _save_chart_to_base64(self) -> str:
        """将图表保存为Base64编码"""
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=self.default_style['dpi'], bbox_inches='tight')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()  # 关闭图表释放内存
        
        return image_base64
    
    def _generate_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成数据摘要"""
        summary = {
            'total_records': len(df),
            'columns': list(df.columns),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
        }
        
        # 数值列的统计信息
        numeric_stats = {}
        for col in summary['numeric_columns']:
            numeric_stats[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'min': df[col].min(),
                'max': df[col].max(),
                'std': df[col].std()
            }
        
        summary['numeric_stats'] = numeric_stats
        
        return summary
    
    def get_supported_chart_types(self) -> List[str]:
        """获取支持的图表类型"""
        return self.supported_chart_types


# 全局图表生成器实例
_chart_generator: Optional[ChartGenerator] = None


def get_chart_generator() -> ChartGenerator:
    """获取图表生成器实例"""
    global _chart_generator
    if _chart_generator is None:
        _chart_generator = ChartGenerator()
    return _chart_generator


async def initialize_chart_generator():
    """初始化图表生成器"""
    global _chart_generator
    _chart_generator = ChartGenerator()