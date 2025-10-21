"""
JSON工具函数
"""

import json
import re
from typing import Any, Dict, List, Optional


def extract_nested_json(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取嵌套的JSON对象
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        JSON对象或None
    """
    if not text:
        return None
    
    # 尝试直接解析整个文本
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试提取JSON对象
    json_patterns = [
        r'\{[^{}]*\{[^{}]*\}[^{}]*\}',  # 嵌套JSON
        r'\{[^{}]*\}',  # 简单JSON
        r'\[.*\]',  # JSON数组
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    安全的JSON解析，解析失败时返回默认值
    
    Args:
        text: JSON文本
        default: 解析失败时的默认值
        
    Returns:
        解析后的对象或默认值
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def format_json_for_display(data: Any, indent: int = 2) -> str:
    """
    格式化JSON数据用于显示
    
    Args:
        data: 要格式化的数据
        indent: 缩进空格数
        
    Returns:
        格式化后的JSON字符串
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data)


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    简单的JSON模式验证
    
    Args:
        data: 要验证的数据
        schema: 模式定义
        
    Returns:
        是否通过验证
    """
    if not isinstance(data, dict) or not isinstance(schema, dict):
        return False
    
    for key, value_type in schema.items():
        if key not in data:
            return False
        
        if not isinstance(data[key], value_type):
            return False
    
    return True


def merge_json_objects(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并两个JSON对象，obj2会覆盖obj1中相同的键
    
    Args:
        obj1: 第一个对象
        obj2: 第二个对象
        
    Returns:
        合并后的对象
    """
    result = obj1.copy()
    
    for key, value in obj2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json_objects(result[key], value)
        else:
            result[key] = value
    
    return result


def extract_json_array(text: str) -> Optional[List[Any]]:
    """
    从文本中提取JSON数组
    
    Args:
        text: 包含JSON数组的文本
        
    Returns:
        JSON数组或None
    """
    if not text:
        return None
    
    # 尝试直接解析
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    
    # 尝试提取数组
    array_pattern = r'\[.*\]'
    matches = re.findall(array_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            continue
    
    return None


def json_contains_keys(data: Dict[str, Any], keys: List[str]) -> bool:
    """
    检查JSON对象是否包含指定的键
    
    Args:
        data: JSON对象
        keys: 要检查的键列表
        
    Returns:
        是否包含所有键
    """
    if not isinstance(data, dict):
        return False
    
    return all(key in data for key in keys)


def filter_json_by_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    根据键列表过滤JSON对象
    
    Args:
        data: 原始JSON对象
        keys: 要保留的键列表
        
    Returns:
        过滤后的JSON对象
    """
    if not isinstance(data, dict):
        return {}
    
    return {key: data[key] for key in keys if key in data}


def json_to_query_params(data: Dict[str, Any]) -> str:
    """
    将JSON对象转换为查询参数字符串
    
    Args:
        data: JSON对象
        
    Returns:
        查询参数字符串
    """
    if not isinstance(data, dict):
        return ""
    
    params = []
    for key, value in data.items():
        if value is not None:
            params.append(f"{key}={value}")
    
    return "&".join(params)