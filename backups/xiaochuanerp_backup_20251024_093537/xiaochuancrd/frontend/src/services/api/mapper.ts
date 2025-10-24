/**
 * 将蛇形命名转换为大驼峰命名
 */
export function snakeToCamel(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => snakeToCamel(item));
    }
    
    const result: any = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
            result[camelKey] = snakeToCamel(obj[key]);
        }
    }
    return result;
}

/**
 * 将大驼峰命名转换为蛇形命名
 */
export function camelToSnake(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    
    // 处理undefined值，转换为null
    if (obj === undefined) {
        return null;
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => camelToSnake(item));
    }
    
    const result: any = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
            const value = obj[key];
            // 将undefined值转换为null
            result[snakeKey] = value === undefined ? null : camelToSnake(value);
        }
    }
    return result;
}