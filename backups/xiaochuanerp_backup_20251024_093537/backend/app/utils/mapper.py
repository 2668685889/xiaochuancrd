"""
命名映射转换工具
用于前后端命名风格转换（大驼峰 <-> 蛇形命名）
"""

from typing import Any, Dict, List, Union
import re


def snake_to_camel(data: Any) -> Any:
    """将蛇形命名转换为小驼峰命名"""
    if data is None or not isinstance(data, (dict, list)):
        return data
    
    if isinstance(data, list):
        return [snake_to_camel(item) for item in data]
    
    result = {}
    for key, value in data.items():
        # 将蛇形命名转换为小驼峰
        camel_key = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), key)
        # 首字母小写（小驼峰命名）
        camel_key = camel_key[0].lower() + camel_key[1:] if camel_key else camel_key
        
        # 特殊处理UUID字段，确保格式正确
        if isinstance(value, str) and _is_uuid_field(key):
            value = _ensure_uuid_format(value)
        
        result[camel_key] = snake_to_camel(value)
    
    return result


def snake_to_pascal(data: Any) -> Any:
    """将蛇形命名转换为大驼峰命名"""
    if data is None or not isinstance(data, (dict, list)):
        return data
    
    if isinstance(data, list):
        return [snake_to_pascal(item) for item in data]
    
    result = {}
    for key, value in data.items():
        # 将蛇形命名转换为大驼峰
        pascal_key = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), key)
        # 首字母大写（大驼峰命名）
        pascal_key = pascal_key[0].upper() + pascal_key[1:] if pascal_key else pascal_key
        
        # 特殊处理UUID字段，确保格式正确
        if isinstance(value, str) and _is_uuid_field(key):
            value = _ensure_uuid_format(value)
        
        result[pascal_key] = snake_to_pascal(value)
    
    return result


def camel_to_snake(data: Any) -> Any:
    """将大驼峰命名转换为蛇形命名"""
    # 处理undefined/null值，转换为None
    if data is None or data == 'undefined' or data == 'null':
        return None
    
    if not isinstance(data, (dict, list)):
        return data
    
    if isinstance(data, list):
        return [camel_to_snake(item) for item in data]
    
    result = {}
    for key, value in data.items():
        # 将大驼峰转换为蛇形命名
        # 处理大驼峰命名（首字母大写）
        snake_key = re.sub(r'([A-Z])', r'_\1', key).lower()
        # 如果开头有下划线，去掉它
        if snake_key.startswith('_'):
            snake_key = snake_key[1:]
        
        # 特殊处理UUID字段，确保格式正确
        if isinstance(value, str) and _is_uuid_field(key):
            value = _ensure_uuid_format(value)
        
        result[snake_key] = camel_to_snake(value)
    
    return result


def _is_uuid_field(field_name: str) -> bool:
    """判断字段名是否为UUID字段"""
    uuid_patterns = ['uuid', 'id', 'uid']
    return any(pattern in field_name.lower() for pattern in uuid_patterns)


def _ensure_uuid_format(uuid_value) -> str:
    """确保UUID格式正确（带连字符）"""
    if not uuid_value:
        return uuid_value
    
    # 如果已经是UUID对象，转换为字符串
    if hasattr(uuid_value, 'hex'):
        uuid_str = str(uuid_value)
    else:
        uuid_str = str(uuid_value)
    
    # 检查是否为有效的UUID格式（带连字符）
    if re.match(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$', uuid_str):
        return uuid_str  # 已经是正确格式，直接返回
    
    # 移除所有连字符和空格
    clean_uuid = re.sub(r'[\-\s]', '', uuid_str)
    
    # 检查是否为有效的UUID格式（32位十六进制）
    if len(clean_uuid) != 32 or not re.match(r'^[a-fA-F0-9]{32}$', clean_uuid):
        return uuid_str  # 不是UUID格式，返回原值
    
    # 重新格式化为标准UUID格式：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    return f"{clean_uuid[:8]}-{clean_uuid[8:12]}-{clean_uuid[12:16]}-{clean_uuid[16:20]}-{clean_uuid[20:]}"


def model_to_dict(model_instance, exclude_none: bool = False) -> Dict[str, Any]:
    """将SQLAlchemy模型实例转换为字典"""
    if model_instance is None:
        return {}
    
    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        if exclude_none and value is None:
            continue
        
        # 特殊处理日期时间字段，确保它们可以被JSON序列化
        if value is not None:
            # 导入必要的模块
            from datetime import date, datetime
            
            # 处理datetime.date对象（只有日期部分）
            if isinstance(value, date) and not isinstance(value, datetime):
                # 如果是datetime.date对象，转换为ISO日期格式
                result[column.name] = value.isoformat()
            # 处理datetime.datetime对象（日期时间）
            elif isinstance(value, datetime):
                # 如果是datetime.datetime对象，转换为完整的ISO格式
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        else:
            result[column.name] = value
    
    return result


def model_list_to_dict_list(model_list: List, exclude_none: bool = False) -> List[Dict[str, Any]]:
    """将SQLAlchemy模型列表转换为字典列表"""
    return [model_to_dict(model, exclude_none) for model in model_list]


def paginate_response(items: List[Any], total: int, page: int, size: int) -> Dict[str, Any]:
    """构建分页响应"""
    pages = (total + size - 1) // size if size > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }