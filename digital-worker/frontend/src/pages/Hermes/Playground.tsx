import React, { useState, useRef, useEffect } from 'react';
import {
  Card, Input, Button, Typography, Space, Tag, Alert, Spin,
  Divider, Timeline, message, Row, Col, Select, Empty, Badge,
} from 'antd';
import {
  SendOutlined, RobotOutlined, UserOutlined, ClearOutlined,
  ApiOutlined, CheckCircleFilled, CloseCircleFilled, LoadingOutlined,
  ThunderboltOutlined, BugOutlined, ExperimentOutlined,
} from '@ant-design/icons';
import { hermesApi } from '@/services/hermes';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

const presetQuestions = [
  { label: '连通性测试', value: '请回复OK确认你已就绪' },
  { label: '简单问候', value: '你好，请介绍一下你自己' },
  { label: '数据分析', value: '请分析一下数据运维中常见的延迟原因有哪些' },
];

const demoRootCausePresets = [
  {
    key: 'demo_delay_1',
    title: '任务延迟根因分析',
    desc: 'JT_PROD_INST_UPLOAD 超时延迟',
    taskId: 'JT_PROD_INST_UPLOAD',
  },
  {
    key: 'demo_delay_2',
    title: '数据同步失败分析',
    desc: 'ETL_SYNC_001 数据同步失败',
    taskId: 'ETL_SYNC_001',
  },
];

const Playground: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [sending, setSending] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'unknown' | 'ok' | 'error'>('unknown');
  const [healthCheckLoading, setHealthCheckLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleHealthCheck = async () => {
    setHealthCheckLoading(true);
    try {
      const res = await hermesApi.health();
      const status = res.data?.status || 'unknown';
      setHealthStatus(status === 'ok' ? 'ok' : 'error');
      if (status === 'ok') {
        message.success('Hermes Agent 连接正常');
      } else {
        message.warning('Hermes Agent 返回异常状态');
      }
    } catch {
      setHealthStatus('error');
      message.error('Hermes Agent 连接失败');
    } finally {
      setHealthCheckLoading(false);
    }
  };

  const addMessage = (role: 'user' | 'assistant', content: string, isStreaming = false) => {
    const msg: ChatMessage = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 6),
      role,
      content,
      timestamp: new Date(),
      isStreaming,
    };
    setMessages((prev) => [...prev, msg]);
    return msg;
  };

  const updateLastMessage = (content: string) => {
    setMessages((prev) => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content,
          isStreaming: false,
        };
      }
      return updated;
    });
  };

  const handleSend = async (text?: string) => {
    const message = (text || inputValue).trim();
    if (!message) return;
    if (sending) return;

    setInputValue('');
    addMessage('user', message);
    setSending(true);

    // Add a placeholder assistant message
    addMessage('assistant', '', true);

    try {
      const res = await hermesApi.chat({ message });
      updateLastMessage(res.data?.reply || '（无响应）');
    } catch (err: any) {
      updateLastMessage(`❌ 请求失败：${err?.message || '未知错误'}`);
    } finally {
      setSending(false);
    }
  };

  const handlePresetQuestion = (value: string) => {
    handleSend(value);
  };

  const handleRootCauseDemo = async (preset: typeof demoRootCausePresets[0]) => {
    if (sending) return;

    const userMsg = `请对任务 ${preset.taskId} 进行根因分析：${preset.desc}`;
    setInputValue('');
    addMessage('user', userMsg);
    setSending(true);
    addMessage('assistant', '', true);

    try {
      const res = await hermesApi.analyzeRootCause({
        task_id: preset.taskId,
        problem_description: preset.desc,
      });
      const data = res.data || {};
      // Format the result as readable text
      const lines: string[] = [];
      lines.push(`✅ **分析完成**`);
      lines.push(``);
      lines.push(`**根因类型**：${data.root_cause || '未知'}`);
      lines.push(``);
      lines.push(`**溯源链路**：`);
      lines.push(`  ${data.trace_path || '无'}`);
      lines.push(``);
      lines.push(`**根因详情**：`);
      lines.push(`  ${data.root_cause_detail || '无'}`);
      lines.push(``);

      if (data.evidence?.length) {
        lines.push(`**核心证据**：`);
        data.evidence.forEach((ev: string) => lines.push(`  - ${ev}`));
        lines.push(``);
      }

      if (data.solution?.length) {
        lines.push(`**解决方案**：`);
        data.solution.forEach((s: string, i: number) => lines.push(`  ${i+1}. ${s}`));
        lines.push(``);
      }

      if (data.analysis_logs?.length) {
        lines.push(`**分析步骤**：`);
        data.analysis_logs.forEach((log: any) => {
          lines.push(`  Step ${log.step}: ${log.action} (${log.duration || 'N/A'})`);
        });
      }

      lines.push(``);
      lines.push(`---`);
      lines.push(`⏱ 人工处理：${data.manual_time || 'N/A'} | 数字员工：${data.auto_time || 'N/A'} | 提升：${data.improvement_pct || 'N/A'}`);

      updateLastMessage(lines.join('\n'));
    } catch (err: any) {
      updateLastMessage(`❌ 分析请求失败：${err?.message || '未知错误'}`);
    } finally {
      setSending(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
  };

  return (
    <div>
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>
          <ExperimentOutlined style={{ marginRight: 8 }} />Hermes Agent 实验台
        </Title>
      </div>

      {/* Status banner */}
      <Card size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
        <Row gutter={16} align="middle">
          <Col>
            <Badge
              status={healthStatus === 'ok' ? 'success' : healthStatus === 'error' ? 'error' : 'default'}
              text={
                <Text type="secondary">
                  Hermes Agent 状态：
                  {healthStatus === 'ok' ? ' 已连接' : healthStatus === 'error' ? ' 异常' : ' 未检测'}
                </Text>
              }
            />
          </Col>
          <Col>
            <Button
              size="small"
              icon={<ApiOutlined />}
              loading={healthCheckLoading}
              onClick={handleHealthCheck}
            >
              检测连接
            </Button>
          </Col>
          <Col flex="auto" />
          <Col>
            <Tag icon={<RobotOutlined />} color="blue">localhost:7860</Tag>
          </Col>
        </Row>
      </Card>

      <Row gutter={16}>
        {/* Main chat area */}
        <Col xs={24} md={16}>
          <Card
            title={
              <Space>
                <RobotOutlined style={{ color: '#1677ff' }} />
                <span>Hermes Agent 对话</span>
                {sending && <Spin size="small" />}
              </Space>
            }
            extra={
              <Button size="small" icon={<ClearOutlined />} onClick={handleClear} disabled={messages.length === 0}>
                清空
              </Button>
            }
            style={{ minHeight: 600 }}
            bodyStyle={{ display: 'flex', flexDirection: 'column', height: 560 }}
          >
            {/* Messages area */}
            <div style={{ flex: 1, overflow: 'auto', marginBottom: 16 }}>
              {messages.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '80px 20px', color: '#999' }}>
                  <RobotOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
                  <div style={{ fontSize: 15, marginBottom: 8 }}>Hermes Agent 实验台</div>
                  <div style={{ fontSize: 13 }}>
                    输入问题或选择下方的预设场景测试 Hermes Agent 的能力
                  </div>
                </div>
              ) : (
                <Timeline
                  items={messages.map((msg) => ({
                    color: msg.role === 'user' ? '#1677ff' : '#52c41a',
                    dot: msg.role === 'user'
                      ? <UserOutlined style={{ color: '#1677ff', fontSize: 14 }} />
                      : msg.isStreaming
                        ? <LoadingOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                        : <RobotOutlined style={{ color: '#52c41a', fontSize: 14 }} />,
                    children: (
                      <div
                        style={{
                          background: msg.role === 'user' ? '#e6f4ff' : '#f6ffed',
                          padding: '10px 14px',
                          borderRadius: 8,
                          whiteSpace: 'pre-wrap',
                          fontFamily: msg.role === 'assistant' ? 'monospace' : 'inherit',
                          fontSize: 13,
                          lineHeight: 1.6,
                        }}
                      >
                        <div style={{ fontWeight: 600, marginBottom: 4, fontSize: 12, color: '#888' }}>
                          {msg.role === 'user' ? '🧑 用户' : '🤖 Hermes Agent'}
                        </div>
                        {msg.isStreaming ? (
                          <Space><Spin size="small" /><Text type="secondary">正在思考...</Text></Space>
                        ) : (
                          msg.content
                        )}
                      </div>
                    ),
                  }))}
                />
              )}
              <div ref={messagesEndRef} />
            </div>

            <Divider style={{ margin: '8px 0' }} />

            {/* Input area */}
            <Space.Compact style={{ width: '100%' }}>
              <TextArea
                rows={2}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="输入问题，回车发送（Shift+Enter 换行）..."
                disabled={sending}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={() => handleSend()}
                loading={sending}
                disabled={!inputValue.trim()}
                style={{ height: 'auto' }}
              >
                发送
              </Button>
            </Space.Compact>
          </Card>
        </Col>

        {/* Presets sidebar */}
        <Col xs={24} md={8}>
          {/* Simple chat presets */}
          <Card title="💬 快速对话" size="small" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {presetQuestions.map((q) => (
                <Button
                  key={q.value}
                  block
                  size="small"
                  onClick={() => handlePresetQuestion(q.value)}
                  disabled={sending}
                >
                  {q.label}
                </Button>
              ))}
            </Space>
          </Card>

          {/* Root cause demo presets */}
          <Card
            title={
              <Space>
                <BugOutlined style={{ color: '#ff4d4f' }} />
                <span>🔍 根因分析演示</span>
              </Space>
            }
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Alert
              type="info"
              message="点击下方场景，Hermes Agent 将自主完成根因分析"
              showIcon
              style={{ marginBottom: 12, fontSize: 12 }}
            />
            <Space direction="vertical" style={{ width: '100%' }}>
              {demoRootCausePresets.map((p) => (
                <Card
                  key={p.key}
                  size="small"
                  hoverable
                  style={{ borderLeft: '3px solid #ff4d4f' }}
                  onClick={() => handleRootCauseDemo(p)}
                >
                  <Space>
                    <ThunderboltOutlined style={{ color: '#ff4d4f' }} />
                    <div>
                      <div style={{ fontWeight: 500, fontSize: 13 }}>{p.title}</div>
                      <div style={{ fontSize: 11, color: '#999' }}>{p.desc}</div>
                    </div>
                  </Space>
                </Card>
              ))}
            </Space>
          </Card>

          {/* Tips */}
          <Card title="💡 提示" size="small">
            <Timeline
              items={[
                {
                  color: 'blue',
                  children: <Text style={{ fontSize: 12 }}>先点击「检测连接」确认 Hermes 可用</Text>,
                },
                {
                  color: 'green',
                  children: <Text style={{ fontSize: 12 }}>使用预设问题快速测试对话能力</Text>,
                },
                {
                  color: 'orange',
                  children: <Text style={{ fontSize: 12 }}>根因分析演示会展示完整的分析过程</Text>,
                },
                {
                  color: 'gray',
                  children: <Text style={{ fontSize: 12 }}>返回格式为结构化文本，完整结果可在根因分析页面查看</Text>,
                },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Playground;
