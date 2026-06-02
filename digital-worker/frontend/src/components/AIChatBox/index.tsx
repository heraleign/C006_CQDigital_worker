import React, { useEffect, useMemo } from 'react';
import { Button, Space, Typography, Divider, Tag, Tooltip, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { PlusOutlined, FileSearchOutlined, DashboardOutlined, CloseOutlined, HolderOutlined, HistoryOutlined } from '@ant-design/icons';
import { useAssistantStore } from '@/stores/useAssistantStore';
import ChatWindow from '@/components/ChatWindow';

const { Text } = Typography;

interface AIChatBoxProps {
  onClose?: () => void;
}

const quickSuggestions = ['查进度', '看告警', '问任务', '导数据'];

const caseDemos = [
  { key: '场景一：任务延期诊断', label: '任务延期诊断', icon: <FileSearchOutlined />, color: '#1890ff' },
  { key: '场景二：指标波动诊断', label: '指标波动诊断', icon: <DashboardOutlined />, color: '#52c41a' },
];

const taskQuickSuggestions = [
  '上游依赖有哪些',
  '影响范围有多大',
  '当前进度如何',
  '预计完成时间',
];

const AIChatBox: React.FC<AIChatBoxProps> = ({ onClose }) => {
  const { messages, sending, sendMessage, createNewSession, currentSession, taskContext, setTaskContext, sessions, selectSession, loadSessions } = useAssistantStore();

  const hasMessages = messages.length > 0;

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const sessionMenuItems: MenuProps['items'] = useMemo(() =>
    sessions.map((session) => ({
      key: session.session_id,
      label: (
        <span style={{ fontWeight: currentSession?.session_id === session.session_id ? 600 : 'normal' }}>
          {session.title}
        </span>
      ),
      onClick: () => selectSession(session),
    })),
    [sessions, currentSession, selectSession],
  );

  // Clear task context when user starts a new conversation manually
  const handleNewSession = () => {
    setTaskContext(null);
    createNewSession();
  };

  // Clear task context when assistant is closed
  useEffect(() => {
    return () => {
      // Don't clear on unmount — keep it visible while drawer is open
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Session header */}
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#fafafa',
        }}
      >
        <Space size={4}>
          {taskContext ? (
            <Tooltip title={`任务 ${taskContext.task_id} — ${taskContext.status}`}>
              <Tag
                color="processing"
                style={{ fontSize: 12, padding: '2px 8px', cursor: 'pointer' }}
                closable
                onClose={(e) => { e.stopPropagation(); setTaskContext(null); }}
              >
                📋 {taskContext.task_name}
              </Tag>
            </Tooltip>
          ) : (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {currentSession?.title || '数字员工小智'}
            </Text>
          )}
        </Space>
        <Space size={4}>
          {taskContext && (
            <Button size="small" type="text" icon={<CloseOutlined />} onClick={() => setTaskContext(null)} style={{ fontSize: 11 }}>
              清除
            </Button>
          )}
          <Dropdown menu={{ items: sessionMenuItems }} trigger={['click']} placement="bottomRight">
            <Button size="small" icon={<HistoryOutlined />}>
              历史会话
            </Button>
          </Dropdown>
          <Button
            size="small"
            icon={<PlusOutlined />}
            onClick={handleNewSession}
          >
            新对话
          </Button>
        </Space>
      </div>

        {/* Quick suggestions & demo scenarios - only show at start */}
      {!hasMessages && (
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid #f0f0f0',
            background: '#fafafa',
          }}
        >
          {taskContext ? (
            <>
              <Text type="secondary" style={{ fontSize: 12, marginBottom: 8, display: 'block' }}>
                当前关注任务：<Text strong style={{ color: '#1890ff' }}>{taskContext.task_name}</Text>
              </Text>
              <Space wrap size={[8, 8]}>
                {taskQuickSuggestions.map((suggestion) => (
                  <Button
                    key={suggestion}
                    size="small"
                    type="default"
                    style={{ borderRadius: 12, fontSize: 12, borderColor: '#1890ff', color: '#1890ff' }}
                    onClick={() => sendMessage(`关于任务「${taskContext.task_name}」${suggestion}`)}
                  >
                    {suggestion}
                  </Button>
                ))}
              </Space>
            </>
          ) : (
            <>
              <Text type="secondary" style={{ fontSize: 12, marginBottom: 8, display: 'block' }}>
                快捷提问
              </Text>
              <Space wrap size={[8, 8]}>
                {quickSuggestions.map((suggestion) => (
                  <Button
                    key={suggestion}
                    size="small"
                    type="default"
                    style={{ borderRadius: 12, fontSize: 12, borderColor: '#d9d9d9' }}
                    onClick={() => sendMessage(suggestion)}
                  >
                    {suggestion}
                  </Button>
                ))}
              </Space>

              <Divider style={{ margin: '12px 0' }} />

              <Text type="secondary" style={{ fontSize: 12, marginBottom: 8, display: 'block' }}>
                <Tag color="blue" style={{ fontSize: 10 }}>演示</Tag> 典型案例分析
              </Text>
              <Space wrap size={[8, 8]}>
                {caseDemos.map((demo) => (
                  <Button
                    key={demo.key}
                    size="small"
                    icon={demo.icon}
                    style={{
                      borderRadius: 12,
                      fontSize: 12,
                      borderColor: demo.color,
                      color: demo.color,
                    }}
                    onClick={() => sendMessage(demo.key)}
                  >
                    {demo.label}
                  </Button>
                ))}
              </Space>
            </>
          )}
        </div>
      )}

      {/* Chat messages */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <ChatWindow
          messages={messages}
          onSend={sendMessage}
          loading={sending}
          placeholder="请输入问题，按 Enter 发送..."
        />
      </div>
    </div>
  );
};

export default AIChatBox;
