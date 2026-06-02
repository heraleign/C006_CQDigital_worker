import React, { useRef, useEffect } from 'react';
import { Input, Button, Typography, Spin } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import type { ChatMessage } from '@/types';

const { Text } = Typography;
const { TextArea } = Input;

interface ChatWindowProps {
  messages: ChatMessage[];
  onSend: (content: string) => void;
  loading?: boolean;
  placeholder?: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSend,
  loading = false,
  placeholder = '请输入您的问题...',
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const value = inputRef.current?.resizableTextArea?.textArea?.value || inputRef.current?.textarea?.value;
    if (value?.trim()) {
      onSend(value.trim());
      if (inputRef.current?.resizableTextArea) {
        inputRef.current.resizableTextArea.textArea.value = '';
      } else if (inputRef.current?.textarea) {
        inputRef.current.textarea.value = '';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: '#fff',
      }}
    >
      {/* Messages area */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px 20px',
        }}
      >
        {messages.length === 0 && !loading && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: '#bfbfbf',
            }}
          >
            <div style={{ fontSize: 48, marginBottom: 16 }}>💬</div>
            <Text type="secondary">发送一条消息，开启与数字员工小智的对话</Text>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.message_id}
            className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}
          >
            {msg.role === 'assistant' && (
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #1677ff, #4096ff)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 14,
                  color: '#fff',
                  marginRight: 8,
                  flexShrink: 0,
                  marginTop: 4,
                }}
              >
                智
              </div>
            )}
            <div className="bubble" style={{ whiteSpace: 'pre-wrap' }}>
              {msg.content}
            </div>
            {msg.role === 'user' && (
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: '#52c41a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 14,
                  color: '#fff',
                  marginLeft: 8,
                  flexShrink: 0,
                  marginTop: 4,
                }}
              >
                我
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble-ai">
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #1677ff, #4096ff)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 14,
                color: '#fff',
                marginRight: 8,
                flexShrink: 0,
              }}
            >
              智
            </div>
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div
        style={{
          borderTop: '1px solid #f0f0f0',
          padding: '12px 16px',
          background: '#fafafa',
        }}
      >
        <div style={{ display: 'flex', gap: 8 }}>
          <TextArea
            ref={inputRef}
            rows={2}
            placeholder={placeholder}
            onKeyDown={handleKeyDown}
            style={{ borderRadius: 8, resize: 'none' }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            style={{ height: 'auto', borderRadius: 8 }}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
