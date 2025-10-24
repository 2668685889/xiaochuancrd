# Markdown 格式转换器

## 概述

Markdown 格式转换器是一个用于将后端返回的 Markdown 格式数据转换为特定排版的文字格式的工具。它特别适用于将表格数据转换为更易读的文字排版格式，提升用户体验。

## 功能特点

- 自动检测 Markdown 内容中的表格
- 将表格数据转换为键值对列表格式
- 保留查询时间和记录数等元信息
- 支持多种表格格式
- 保持非表格内容不变

## 使用方法

### 基本用法

```typescript
import { convertMarkdownToTextFormat } from '@/utils/markdown-converter';

// 转换包含表格的 Markdown 内容
const markdownContent = `
商品数据库查询结果

| 商品ID | 商品名称 | 分类 | 价格 |
|--------|----------|------|------|
| P001 | 无线蓝牙耳机 | 电子产品 | 299.00 |
| P002 | 不锈钢保温杯 | 生活用品 | 89.00 |
`;

const textContent = convertMarkdownToTextFormat(markdownContent);
console.log(textContent);
```

### 转换效果

**输入内容**:
```markdown
商品数据库查询结果

| 商品ID | 商品名称 | 分类 | 价格 |
|--------|----------|------|------|
| P001 | 无线蓝牙耳机 | 电子产品 | 299.00 |
| P002 | 不锈钢保温杯 | 生活用品 | 89.00 |
```

**输出内容**:
```markdown
**商品数据库查询结果**

**查询时间**：2023-10-25 14:30:00
**总记录数**：2 条

---

**记录 1**
- 商品ID：P001
- 商品名称：无线蓝牙耳机
- 分类：电子产品
- 价格：299.00

**记录 2**
- 商品ID：P002
- 商品名称：不锈钢保温杯
- 分类：生活用品
- 价格：89.00

---

以上为查询结果。如果您需要按特定条件进行查询，请随时告诉我。
```

## API 参考

### 主要函数

#### `convertMarkdownToTextFormat(content: string): string`

将 Markdown 内容转换为文字排版格式。

- **参数**:
  - `content`: 要转换的 Markdown 内容字符串
- **返回值**: 转换后的文字排版格式字符串

#### `containsTable(content: string): boolean`

检测内容是否包含表格。

- **参数**:
  - `content`: 要检测的内容字符串
- **返回值**: 如果包含表格返回 `true`，否则返回 `false`

#### `isQueryResult(content: string): boolean`

检测内容是否是查询结果。

- **参数**:
  - `content`: 要检测的内容字符串
- **返回值**: 如果是查询结果返回 `true`，否则返回 `false`

#### `extractTableData(content: string)`

从 Markdown 内容中提取表格数据。

- **参数**:
  - `content`: 包含表格的 Markdown 内容字符串
- **返回值**: 包含表头和数据行的对象，格式为 `{ headers: string[], dataRows: string[][] }`

#### `extractQueryTime(content: string): string`

从内容中提取查询时间。

- **参数**:
  - `content`: 可能包含查询时间的内容字符串
- **返回值**: 提取到的查询时间字符串，如果没有找到则返回空字符串

## 在智能助手页面中的集成

在 `SmartAssistantPage.tsx` 中，我们已经在 `formatMarkdownData` 函数中集成了这个转换器：

```typescript
const formatMarkdownData = (content: string): string => {
  // 使用新的markdown转换器将表格数据转换为文字排版格式
  return convertMarkdownToTextFormat(content);
};
```

这样，当后端返回包含表格的 Markdown 数据时，前端会自动将其转换为用户友好的文字排版格式。

## 测试

项目包含了完整的单元测试，位于 `src/test/markdown-converter.unit.test.ts`。运行测试：

```bash
npx tsx src/test/markdown-converter.unit.test.ts
```

## 注意事项

1. 转换器只处理包含表格的内容，非表格内容会保持不变
2. 查询结果需要有明确的标识（如包含"查询结果"或"数据库查询"）
3. 查询时间格式应为 `YYYY-MM-DD HH:MM:SS`
4. 表格必须使用标准的 Markdown 表格格式

## 更新日志

- v1.0.0: 初始版本，支持基本的表格到文字转换
- 修复了 `isQueryResult` 函数的逻辑，使其只检测明确的查询结果标识
- 修复了 `extractQueryTime` 函数，在没有查询时间时返回空字符串而非当前时间