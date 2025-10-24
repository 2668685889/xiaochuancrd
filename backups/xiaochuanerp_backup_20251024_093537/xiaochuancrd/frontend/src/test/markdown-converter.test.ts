import { convertMarkdownToTextFormat, containsTable, isQueryResult, extractTableData } from '../utils/markdown-converter';

// 测试用例
const testCases = [
  {
    name: '标准表格测试',
    input: `| 商品ID | 商品名称 | 分类 | 价格 | 库存 | 上架时间 | 状态 |
|--------|----------|------|------|------|----------|------|
| P001 | 无线蓝牙耳机 | 电子产品 | 299.00 | 150 | 2023-08-05 | 销售中 |
| P002 | 不锈钢保温杯 | 生活用品 | 89.00 | 200 | 2023-09-12 | 销售中 |
| P003 | 经典文学套装全集 | 图书 | 120.50 | 80 | 2023-07-22 | 缺货 |`,
    expected: '商品数据库查询结果'
  },
  {
    name: '非表格内容测试',
    input: '这是一段普通的文本内容，不包含表格。',
    expected: '这是一段普通的文本内容，不包含表格。'
  }
];

// 运行测试
testCases.forEach(testCase => {
  console.log(`\n=== 测试: ${testCase.name} ===`);
  console.log('输入内容:', testCase.input);
  
  const result = convertMarkdownToTextFormat(testCase.input);
  console.log('转换结果:', result);
  
  const hasTable = containsTable(testCase.input);
  console.log('包含表格:', hasTable);
  
  const isQuery = isQueryResult(testCase.input);
  console.log('是查询结果:', isQuery);
  
  if (hasTable) {
    const tableData = extractTableData(testCase.input);
    console.log('表格数据:', tableData);
  }
  
  console.log('---');
});