import { convertMarkdownToTextFormat } from '../utils/markdown-converter';

// 模拟后端返回的实际数据格式
const mockBackendResponse = `📊 数据库查询结果

查询时间：2023-10-25 14:30:00
总记录数：4 条
查询说明：以下为商品数据库查询结果

| 商品ID | 商品名称 | 分类 | 价格 | 库存 | 上架时间 | 状态 |
|--------|----------|------|------|------|----------|------|
| P001 | 无线蓝牙耳机 | 电子产品 | 299.00 | 150 | 2023-08-05 | 销售中 |
| P002 | 不锈钢保温杯 | 生活用品 | 89.00 | 200 | 2023-09-12 | 销售中 |
| P003 | 经典文学套装全集 | 图书 | 120.50 | 80 | 2023-07-22 | 缺货 |
| P004 | 便携式投影仪 | 电子产品 | 850.00 | 30 | 2023-10-10 | 销售中 |

查询完成，共返回 4 条记录。`;

// 运行测试
console.log('=== 模拟后端响应转换测试 ===');
console.log('原始响应内容:');
console.log(mockBackendResponse);
console.log('\n=====================\n');

console.log('转换后的内容:');
const convertedContent = convertMarkdownToTextFormat(mockBackendResponse);
console.log(convertedContent);