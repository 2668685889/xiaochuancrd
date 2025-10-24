import { 
  convertMarkdownToTextFormat, 
  containsTable, 
  isQueryResult, 
  extractTableData,
  extractQueryTime
} from '../utils/markdown-converter';

// 简单的测试框架
function assert(condition, message) {
  if (!condition) {
    console.error(`❌ 测试失败: ${message}`);
    return false;
  } else {
    console.log(`✅ 测试通过: ${message}`);
    return true;
  }
}

function runTests() {
  console.log('开始运行 Markdown Converter 单元测试...\n');
  
  let passedTests = 0;
  let totalTests = 0;

  // 测试1: 表格检测
  totalTests++;
  const markdownWithTable = '| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1 | Cell 2 |';
  if (assert(containsTable(markdownWithTable), '应该检测到表格')) {
    passedTests++;
  }
  
  totalTests++;
  const markdownWithoutTable = 'This is just text without a table.';
  if (assert(!containsTable(markdownWithoutTable), '不应该检测到表格')) {
    passedTests++;
  }

  // 测试2: 查询结果检测
  totalTests++;
  const queryResult = '📊 数据库查询结果\n| ID | Name |\n|----|------|\n| 1 | Test |';
  if (assert(isQueryResult(queryResult), '应该检测到查询结果')) {
    passedTests++;
  }
  
  totalTests++;
  const notQueryResult = '| ID | Name |\n|----|------|\n| 1 | Test |';
  if (assert(!isQueryResult(notQueryResult), '不应该检测到查询结果')) {
    passedTests++;
  }

  // 测试3: 表格数据提取
  totalTests++;
  const markdown = '| Name | Age |\n|------|-----|\n| John | 25 |\n| Jane | 30 |';
  const tableData = extractTableData(markdown);
  const headersMatch = JSON.stringify(tableData.headers) === JSON.stringify(['Name', 'Age']);
  const dataRowsMatch = JSON.stringify(tableData.dataRows) === JSON.stringify([['John', '25'], ['Jane', '30']]);
  if (assert(headersMatch && dataRowsMatch, '应该正确提取表格数据')) {
    passedTests++;
  }

  // 测试4: 查询时间提取
  totalTests++;
  const markdownWithTime = '查询时间：2023-10-25 14:30:00\n| ID | Name |';
  if (assert(extractQueryTime(markdownWithTime) === '2023-10-25 14:30:00', '应该正确提取查询时间')) {
    passedTests++;
  }
  
  totalTests++;
  const markdownWithoutTime = '| ID | Name |';
  if (assert(extractQueryTime(markdownWithoutTime) === '', '没有查询时间时应该返回空字符串')) {
    passedTests++;
  }

  // 测试5: 完整转换
  totalTests++;
  const complexMarkdown = `商品数据库查询结果

| 商品ID | 商品名称 | 分类 | 价格 |
|--------|----------|------|------|
| P001 | 无线蓝牙耳机 | 电子产品 | 299.00 |
| P002 | 不锈钢保温杯 | 生活用品 | 89.00 |`;

  const result = convertMarkdownToTextFormat(complexMarkdown);
  const hasTitle = result.includes('**商品数据库查询结果**');
  const hasRecord1 = result.includes('**记录 1**');
  const hasProductID1 = result.includes('- 商品ID：P001');
  const hasProductName1 = result.includes('- 商品名称：无线蓝牙耳机');
  const hasRecord2 = result.includes('**记录 2**');
  const hasProductID2 = result.includes('- 商品ID：P002');
  const hasProductName2 = result.includes('- 商品名称：不锈钢保温杯');
  
  if (assert(hasTitle && hasRecord1 && hasProductID1 && hasProductName1 && hasRecord2 && hasProductID2 && hasProductName2, '应该正确转换表格为文字格式')) {
    passedTests++;
  }

  // 测试6: 非表格内容保持不变
  totalTests++;
  const plainText = 'This is a simple text without any tables.';
  const plainResult = convertMarkdownToTextFormat(plainText);
  if (assert(plainResult === plainText, '非表格内容应该保持不变')) {
    passedTests++;
  }

  // 输出测试结果
  console.log(`\n测试完成！通过 ${passedTests}/${totalTests} 项测试`);
  
  if (passedTests === totalTests) {
    console.log('🎉 所有测试都通过了！');
  } else {
    console.log('⚠️ 有测试失败，请检查代码');
  }
}

// 运行测试
runTests();