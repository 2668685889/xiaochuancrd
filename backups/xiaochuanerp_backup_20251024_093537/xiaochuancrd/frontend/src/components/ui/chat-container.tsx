import React, { useEffect, useRef } from 'react';
import ChatMessage from './chat-message';
import { ChatInput } from './chat-input';
import { QuickActions, defaultActions } from './quick-actions';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'sql' | 'chart' | 'table';
}

interface ChatContainerProps {
  messages: Message[];
  inputValue: string;
  onInputChange: (value: string) => void;
  onSendMessage: () => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  inputValue,
  onInputChange,
  onSendMessage,
  isLoading = false,
  placeholder = "请输入您的问题..."
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // 只在有新消息且用户没有手动滚动时自动滚动到底部
    if (messagesContainerRef.current) {
      const container = messagesContainerRef.current;
      const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
      
      if (isNearBottom) {
        scrollToBottom();
      }
    }
  }, [messages]);

  const handleQuickAction = (query: string) => {
    onInputChange(query);
    // 自动发送消息
    setTimeout(() => onSendMessage(), 100);
  };

  const showQuickActions = messages.length <= 1;

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200">
      {/* 聊天消息区域 */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex flex-col">
          {/* 消息列表 */}
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-6"
          >
            <div className="max-w-4xl mx-auto">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  content={message.content}
                  role={message.role}
                  timestamp={message.timestamp}
                  type={message.type}
                />
              ))}
              
              {/* 加载状态 */}
              {isLoading && (
                <div className="flex gap-3 mb-6">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                    <div className="w-4 h-4 bg-gray-300 rounded-full animate-pulse" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" />
                        <div className="w-3 h-2 bg-gray-300 rounded-full animate-pulse" />
                        <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* 快速操作区域 */}
          {showQuickActions && (
            <div className="border-t border-gray-100 bg-gray-50/50">
              <div className="max-w-4xl mx-auto p-6">
                <div className="text-center mb-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-1">
                    常用查询
                  </h3>
                  <p className="text-xs text-gray-500">
                    点击以下按钮快速开始对话
                  </p>
                </div>
                <QuickActions 
                  actions={defaultActions} 
                  onActionClick={handleQuickAction}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 输入区域 */}
      <div className="border-t border-gray-100 p-6">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            value={inputValue}
            onChange={onInputChange}
            onSend={onSendMessage}
            disabled={isLoading}
            placeholder={placeholder}
          />
          <div className="text-xs text-gray-400 mt-2 text-center">
            按 Enter 发送，Shift + Enter 换行
          </div>
        </div>
      </div>
    </div>
  );
};