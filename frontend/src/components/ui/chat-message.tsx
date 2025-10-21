import React, { useState } from 'react';
import { Copy, Check, ChevronUp, ChevronDown, Bot, User, FileText, Code, BarChart3, Database, Brain } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageProps {
  content: string;
  type?: 'text' | 'code' | 'chart' | 'table' | 'sql' | 'math';
  role: 'user' | 'assistant';
  timestamp?: string;
}

const ChatMessage: React.FC<MessageProps> = ({ 
  content, 
  type = 'text', 
  role, 
  timestamp 
}) => {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const isUser = role === 'user';
  const isLongContent = content.length > 500;

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getIcon = () => {
    switch (type) {
      case 'code':
        return <Code className="w-5 h-5 text-blue-600" />;
      case 'chart':
        return <BarChart3 className="w-5 h-5 text-purple-600" />;
      case 'table':
        return <FileText className="w-5 h-5 text-green-600" />;
      case 'sql':
        return <Database className="w-5 h-5 text-orange-600" />;
      case 'math':
        return <Brain className="w-5 h-5 text-pink-600" />;
      default:
        return isUser ? <User className="w-5 h-5 text-blue-600" /> : <Bot className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch (error) {
      return '';
    }
  };

  const timeString = formatTime(timestamp);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      {!isUser && (
        <div className="flex items-start mr-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center shadow-sm">
            {getIcon()}
          </div>
        </div>
      )}
      
      <div className="flex flex-col flex-1">
        <div className={`max-w-[85%] rounded-lg relative group ${
          isUser 
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white self-end' 
            : 'bg-white self-start'
        }`}>
          {/* 操作工具栏 */}
          <div className="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="p-1 rounded bg-white/20 hover:bg-white/30 transition-colors"
              title="复制内容"
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
            </button>
            {isLongContent && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="p-1 rounded bg-white/20 hover:bg-white/30 transition-colors"
                title={expanded ? '收起' : '展开'}
              >
                {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}
          </div>
          
          {/* 消息内容 */}
          <div className="p-4">
            <div className={`text-content ${isUser ? '' : 'markdown-content'}`}>
              {isUser ? (
                <div className="whitespace-pre-wrap">
                  {isLongContent && !expanded ? content.substring(0, 500) + '...' : content}
                </div>
              ) : (
                <div className={isLongContent && !expanded ? 'line-clamp-6' : ''}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // 自定义表格渲染 - DeepSeek风格
                      table: ({ children }) => (
                        <div className="overflow-x-auto my-3">
                          <table className="min-w-full border-collapse border border-gray-200 rounded-lg shadow-sm">
                            {children}
                          </table>
                        </div>
                      ),
                      thead: ({ children }) => (
                        <thead className="bg-gray-50 border-b border-gray-200">
                          {children}
                        </thead>
                      ),
                      th: ({ children }) => (
                        <th className="border border-gray-200 px-4 py-3 text-left text-sm font-semibold text-gray-700 bg-gray-50">
                          {children}
                        </th>
                      ),
                      td: ({ children }) => (
                        <td className="border border-gray-200 px-4 py-3 text-sm text-gray-600">
                          {children}
                        </td>
                      ),
                      // 自定义标题样式 - DeepSeek风格
                      h1: ({ children }) => (
                        <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-3 pb-2 border-b border-gray-200">{children}</h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-xl font-semibold text-gray-800 mt-5 mb-2">{children}</h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-lg font-medium text-gray-700 mt-4 mb-2">{children}</h3>
                      ),
                      h4: ({ children }) => (
                        <h4 className="text-base font-medium text-gray-600 mt-3 mb-1">{children}</h4>
                      ),
                      // 自定义列表样式 - DeepSeek风格
                      ul: ({ children }) => (
                        <ul className="list-disc list-outside my-3 space-y-2 pl-6">{children}</ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal list-outside my-3 space-y-2 pl-6">{children}</ol>
                      ),
                      li: ({ children }) => (
                        <li className="text-gray-700 leading-relaxed">{children}</li>
                      ),
                      // 自定义段落样式 - DeepSeek风格
                      p: ({ children }) => (
                        <p className="my-3 text-gray-700 leading-relaxed">{children}</p>
                      ),
                      // 自定义代码样式 - DeepSeek风格
                      code: ({ inline, children }) => (
                        inline ? (
                          <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono border border-gray-200">
                            {children}
                          </code>
                        ) : (
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-3 border border-gray-700">
                            <code className="font-mono text-sm">{children}</code>
                          </pre>
                        )
                      ),
                      // 自定义引用样式 - DeepSeek风格
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-blue-400 pl-4 my-3 italic text-gray-600 bg-blue-50 py-2 rounded-r">
                          {children}
                        </blockquote>
                      ),
                      // 自定义链接样式
                      a: ({ children, href }) => (
                        <a href={href} className="text-blue-500 hover:text-blue-700 underline transition-colors">
                          {children}
                        </a>
                      ),
                      // 自定义强调样式
                      strong: ({ children }) => (
                        <strong className="font-semibold text-gray-800">{children}</strong>
                      ),
                      // 自定义斜体样式
                      em: ({ children }) => (
                        <em className="italic text-gray-600">{children}</em>
                      ),
                    }}
                  >
                    {isLongContent && !expanded ? content.substring(0, 500) + '...' : content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className={`flex items-center mt-1 ${isUser ? 'justify-end' : 'justify-start'} space-x-2`}>
          <span className="text-xs text-gray-500">{timeString}</span>
          {isLongContent && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-blue-500 hover:text-blue-700 underline"
            >
              {expanded ? '收起' : '展开全部'}
            </button>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="flex items-start ml-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center shadow-sm">
            {getIcon()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;