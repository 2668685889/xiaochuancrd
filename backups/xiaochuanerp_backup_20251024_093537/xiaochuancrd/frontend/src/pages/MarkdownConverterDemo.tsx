import React, { useState } from 'react';
import { convertMarkdownToTextFormat } from '../utils/markdown-converter';

const MarkdownConverterDemo: React.FC = () => {
  const [input, setInput] = useState(`商品数据库查询结果

查询时间：2023-10-25 14:30:00
总记录数：4 条
查询说明：以下为商品数据库查询结果

| 商品ID | 商品名称 | 分类 | 价格 | 库存 | 上架时间 | 状态 |
|--------|----------|------|------|------|----------|------|
| P001 | 无线蓝牙耳机 | 电子产品 | 299.00 | 150 | 2023-08-05 | 销售中 |
| P002 | 不锈钢保温杯 | 生活用品 | 89.00 | 200 | 2023-09-12 | 销售中 |
| P003 | 经典文学套装全集 | 图书 | 120.50 | 80 | 2023-07-22 | 缺货 |
| P004 | 便携式投影仪 | 电子产品 | 850.00 | 30 | 2023-10-10 | 销售中 |

查询完成，共返回 4 条记录。`);

  const [output, setOutput] = useState(convertMarkdownToTextFormat(input));

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newInput = e.target.value;
    setInput(newInput);
    setOutput(convertMarkdownToTextFormat(newInput));
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6 text-center">Markdown 格式转换器演示</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">输入 (Markdown 格式)</h2>
          <textarea
            className="w-full h-96 p-3 border border-gray-300 rounded-md font-mono text-sm"
            value={input}
            onChange={handleInputChange}
            placeholder="在此输入 Markdown 格式的内容..."
          />
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">输出 (文字排版格式)</h2>
          <div className="w-full h-96 p-3 border border-gray-300 rounded-md overflow-auto bg-gray-50">
            <pre className="whitespace-pre-wrap font-sans text-sm">{output}</pre>
          </div>
        </div>
      </div>
      
      <div className="mt-6 bg-blue-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2 text-blue-800">使用说明</h3>
        <ul className="list-disc list-inside text-blue-700 space-y-1">
          <li>在左侧输入框中输入包含表格的 Markdown 格式内容</li>
          <li>右侧会自动显示转换后的文字排版格式</li>
          <li>转换器会自动识别表格和查询结果，并将其转换为更易读的格式</li>
          <li>非表格内容会保持不变</li>
        </ul>
      </div>
    </div>
  );
};

export default MarkdownConverterDemo;