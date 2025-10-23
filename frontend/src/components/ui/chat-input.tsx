import React, { useState } from 'react';
import { Send, Paperclip, Mic } from 'lucide-react';
import { Button } from './button';
import { Input } from './input';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = "请输入您的问题..."
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className={`
      relative border rounded-xl transition-all duration-200
      ${isFocused 
        ? 'border-primary-500 shadow-lg shadow-primary-500/10' 
        : 'border-gray-200 shadow-sm'
      }
      ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
    `}>
      {/* 输入框 */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        disabled={disabled}
        placeholder={placeholder}
        className="
          w-full px-4 py-3 pr-20 bg-transparent 
          focus:outline-none resize-none
          placeholder-gray-400 text-sm leading-relaxed
          min-h-[60px] max-h-[120px]
        "
        rows={1}
      />

      {/* 操作按钮 */}
      <div className="absolute right-3 bottom-3 flex items-center gap-2">
        {/* 附件按钮 */}
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600"
          disabled={disabled}
        >
          <Paperclip className="w-4 h-4" />
        </Button>

        {/* 语音按钮 */}
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600"
          disabled={disabled}
        >
          <Mic className="w-4 h-4" />
        </Button>

        {/* 发送按钮 */}
        <Button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          size="sm"
          className="h-8 px-3 bg-primary-500 hover:bg-primary-600 text-white"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};