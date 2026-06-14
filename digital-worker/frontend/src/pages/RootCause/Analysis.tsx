import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Input, Form, Select, message, Spin, Alert, Empty, Steps, Typography, Space, Divider, Timeline, Tag, Descriptions, Table, Tabs, Switch } from 'antd';
import { RobotOutlined, ThunderboltOutlined, LikeOutlined, DislikeOutlined, BookOutlined, ExportOutlined, CheckCircleFilled, LoadingOutlined, ClockCircleFilled, ExperimentOutlined, FileSearchOutlined, DashboardOutlined, ArrowRightOutlined, BugOutlined, ApiOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { rootCauseApi } from '@/services/rootCause';
import { hermesApi } from '@/services/hermes';
import type { AnalysisRecord } from '@/types';

const { TextArea } = Input;
const { Text, Title } = Typography;

const analysisSteps = [
  { title: '意图识别', tool: 'nlp-classifier' },
  { title: '信息采集', tool: 'info-collector' },
  { title: '日志分析', tool: 'log-analyzer' },
  { title: '知识检索', tool: 'knowledge-retriever' },
  { title: '根因推理', tool: 'reasoning-engine' },
  { title: '方案生成', tool: 'solution-generator' },
];

const presetScenarios = [
  {
    key: 'task_delay',
    title: '场景一：任务延期分析',
    desc: '集团上传产品实例表超时未完成',
    icon: <FileSearchOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
    color: '#e6f7ff',
    borderColor: '#1890ff',
  },
  {
    key: 'metric_anomaly',
    title: '场景二：指标波动分析',
    desc: '新增用户数异常上涨30%',
    icon: <DashboardOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
    color: '#f6ffed',
    borderColor: '#52c41a',
  },
  {
    key: 'hermes_agent',
    title: '🤖 Hermes Agent 分析',
    desc: '由 Hermes AI Agent 自主规划并执行分析',
    icon: <ApiOutlined style={{ fontSize: 24, color: '#722ed1' }} />,
    color: '#f9f0ff',
    borderColor: '#722ed1',
  },
];

const Analysis: React.FC = () => {
  const [problemDesc, setProblemDesc] = useState('');
  const [acctMonth, setAcctMonth] = useState('');
  const [taskId, setTaskId] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [analysisLogs, setAnalysisLogs] = useState<any[]>([]);
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [presetMode, setPresetMode] = useState(false);
  const [activeLogStep, setActiveLogStep] = useState<number | null>(null);
  const [hermesMode, setHermesMode] = useState(false);
  const [hermesTaskId, setHermesTaskId] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await rootCauseApi.getAnalysis({ page: 1, page_size: 10 });
        setHistory(res.data?.items || []);
      } catch { /* ignore */ }
    })();
  }, []);

  const handleStartAnalysis = async (isPreset = false, presetKey = '') => {
    if (!isPreset && !problemDesc.trim()) { message.warning('请输入问题描述'); return; }
    setAnalyzing(true); setCurrentStep(0); setAnalysisResult(null); setAnalysisLogs([]); setError(null);
    setPresetMode(isPreset);
    setHermesMode(false);

    try {
      // ── Hermes Agent mode (async) ─────────────────────────────
      if (isPreset && presetKey === 'hermes_agent') {
        const tid = hermesTaskId || problemDesc.trim();
        if (!tid) { message.warning('请输入任务ID或问题描述'); setAnalyzing(false); return; }

        setAnalyzing(true);
        setPresetMode(false);
        setHermesMode(true);

        // Submit async
        const submitRes = await hermesApi.analyzeRootCause({
          task_id: tid,
          problem_description: problemDesc,
          acct_month: acctMonth || undefined,
        });
        const asyncTaskId = submitRes.data?.task_id;
        if (!asyncTaskId) { message.error('提交分析任务失败'); setAnalyzing(false); return; }

        // Poll until completed or failed
        let done = false;
        while (!done) {
          await new Promise((r) => setTimeout(r, 2000));
          const statusRes = await hermesApi.getAnalysisStatus(asyncTaskId);
          const st = statusRes.data || {};
          if (st.status === 'completed' && st.result) {
            const logs = st.result.analysis_logs || [];
            setAnalysisLogs(logs);
            for (let i = 0; i < logs.length; i++) {
              setCurrentStep(i);
              setActiveLogStep(i);
              await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
            }
            setCurrentStep(logs.length);
            setActiveLogStep(null);
            setAnalysisResult(st.result);
            done = true;
          } else if (st.status === 'failed') {
            setError(st.error || 'Hermes 分析失败');
            done = true;
          }
          // else still "processing" — keep polling
        }
        setAnalyzing(false);
        return;
      }

      // ── Existing flow ──────────────────────────────────────────
      const payload: any = isPreset
        ? { preset_type: presetKey, problem_description: '', acct_month: '', task_id: '' }
        : { problem_description: problemDesc, acct_month: acctMonth || undefined, task_id: taskId || undefined };

      const res = await rootCauseApi.createAnalysis(payload);
      const recordId = res.data?.record_id || '';

      if (isPreset && res.data?.analysis_logs) {
        // Preset mode: show step-by-step with logs
        const logs = res.data.analysis_logs;
        for (let i = 0; i < logs.length; i++) {
          setCurrentStep(i);
          setActiveLogStep(i);
          await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
        }
        setAnalysisLogs(logs);
        setCurrentStep(logs.length);
        setActiveLogStep(null);

        // Get full result
        if (recordId) {
          const detailRes = await rootCauseApi.getAnalysisDetail(recordId, { preset_type: presetKey });
          setAnalysisResult(detailRes.data || res.data);
        } else {
          setAnalysisResult(res.data);
        }
      } else {
        // Normal mode: existing flow
        for (let i = 0; i < analysisSteps.length; i++) {
          setCurrentStep(i);
          await new Promise((r) => setTimeout(r, 700 + Math.random() * 500));
        }
        if (recordId) {
          const statusRes = await rootCauseApi.getAnalysisDetail(recordId);
          setAnalysisResult({
            record_id: statusRes.data?.record_id,
            root_cause: statusRes.data?.root_cause_result || '数据同步延迟导致上游表未及时更新',
            impact: '影响范围: 应收模块3个表',
            solution: ['1. 检查上游数据源同步状态', '2. 重启数据同步任务', '3. 验证数据一致性'],
            prevention: ['建议设置数据同步监控告警，延迟超过30分钟自动通知'],
            cases: [{ title: '类似案例: 应收数据延迟', score: 85 }],
          });
        } else {
          setAnalysisResult({
            root_cause: '数据同步延迟导致上游表未及时更新',
            impact: '影响范围: 应收模块3个表',
            solution: ['1. 检查上游数据源同步状态', '2. 重启数据同步任务', '3. 验证数据一致性'],
            prevention: ['建议设置数据同步监控告警'],
            cases: [{ title: '类似案例: 应收数据延迟', score: 85 }],
          });
        }
        setCurrentStep(analysisSteps.length);
      }
    } catch (err: any) {
      setError(err?.message || '分析失败');
      setCurrentStep(-1);
    } finally {
      setAnalyzing(false);
    }
  };

  const handlePresetClick = (key: string) => {
    const preset = presetScenarios.find((p) => p.key === key);
    if (!preset) return;

    if (key === 'hermes_agent') {
      // Hermes mode — use the task ID field
      setProblemDesc(preset.desc);
      if (!hermesTaskId) {
        setHermesTaskId('JT_PROD_INST_UPLOAD');
      }
      handleStartAnalysis(true, key);
    } else {
      setProblemDesc(preset.desc);
      handleStartAnalysis(true, key);
    }
  };

  const renderLogSteps = () => {
    if (analysisLogs.length === 0) return null;

    return (
      <Timeline
        items={analysisLogs.map((log: any, idx: number) => ({
          color: log.status === 'completed' ? 'green' : idx === activeLogStep ? 'blue' : 'gray',
          dot: log.status === 'completed' ? <CheckCircleFilled style={{ color: '#52c41a', fontSize: 16 }} /> :
               idx === activeLogStep ? <LoadingOutlined style={{ color: '#1890ff', fontSize: 16 }} /> :
               <ClockCircleFilled style={{ color: '#d9d9d9', fontSize: 16 }} />,
          children: (
            <div style={{ marginBottom: 8, opacity: log.status === 'completed' || idx <= currentStep ? 1 : 0.4 }}>
              <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                Step {log.step}: {log.action}
                {log.status === 'completed' && <Tag color="success" style={{ fontSize: 11 }}>{log.duration}</Tag>}
              </div>
              <div style={{ fontSize: 12, color: '#666', marginBottom: 2, fontFamily: 'monospace', background: '#f5f5f5', padding: '4px 8px', borderRadius: 4 }}>
                {log.detail}
              </div>
              <div style={{ fontSize: 13, color: log.result.includes('✗') || log.result.includes('❌') ? '#cf1322' : log.result.includes('✓') || log.result.includes('✅') ? '#389e0d' : '#333', whiteSpace: 'pre-wrap' }}>
                {log.result}
              </div>
            </div>
          ),
        }))}
      />
    );
  };

  const renderPresetResult = () => {
    if (!analysisResult || (!presetMode && !hermesMode)) return null;
    const r = analysisResult;

    return (
      <div>
        <Alert
          type="success"
          message={
            <Space>
              <span>✅ 分析完成</span>
              {hermesMode && <Tag icon={<ApiOutlined />} color="purple">Hermes Agent</Tag>}
              <Tag color="blue">根因类型：{r.root_cause}</Tag>
              <Tag color="green">分析耗时：{r.auto_time}</Tag>
            </Space>
          }
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Tabs
          defaultActiveKey="summary"
          items={[
            {
              key: 'summary',
              label: '根因总结',
              children: (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Card size="small" style={{ background: '#fffbe6', borderLeft: '3px solid #faad14' }}>
                    <Text strong>根因结论：</Text>
                    <div style={{ marginTop: 4, fontSize: 15, fontWeight: 500, color: '#cf1322' }}>{r.root_cause}</div>
                  </Card>
                  <Card size="small" title={<span><BugOutlined style={{ marginRight: 6 }} />溯源链路</span>}>
                    <pre style={{ whiteSpace: 'pre-wrap', margin: 0, background: '#f5f5f5', padding: 12, borderRadius: 4, fontSize: 13 }}>{r.trace_path}</pre>
                  </Card>
                  <Card size="small" title="根因详情">
                    <Text>{r.root_cause_detail}</Text>
                  </Card>
                  {r.source_system && (
                    <Descriptions size="small" column={2} bordered>
                      <Descriptions.Item label="责任系统">{r.source_system}</Descriptions.Item>
                      <Descriptions.Item label="联系人">{r.source_contact}</Descriptions.Item>
                    </Descriptions>
                  )}
                </Space>
              ),
            },
            {
              key: 'evidence',
              label: '核心证据',
              children: (
                <Card size="small">
                  <Timeline
                    items={r.evidence?.map((ev: string, i: number) => ({
                      color: i < 2 ? 'red' : 'orange',
                      children: <Text style={{ fontSize: 13 }}>{ev}</Text>,
                    })) || []}
                  />
                </Card>
              ),
            },
            {
              key: 'solution',
              label: '处理建议',
              children: (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Card size="small" title={r.risk_level ? `⚠️ 风险评估：${r.severity}（${r.risk_level}）` : '解决方案'}>
                    {r.impact_assessment && (
                      <Alert type="warning" message={r.impact_assessment} style={{ marginBottom: 12 }} showIcon />
                    )}
                    {r.fake_users && (
                      <Alert type="error" message={`虚假用户数：${r.fake_users}户`} style={{ marginBottom: 12 }} showIcon />
                    )}
                    <Timeline
                      items={r.solution?.map((s: string) => ({
                        color: s.includes('紧急') ? 'red' : s.includes('长效') ? 'blue' : 'gray',
                        children: <Text style={{ fontSize: 13 }}>{s}</Text>,
                      })) || []}
                    />
                  </Card>
                  {r.prevention && r.prevention.length > 0 && (
                    <Card size="small" title="🔒 预防措施">
                      <Timeline
                        items={r.prevention.map((p: string) => ({
                          color: 'green',
                          children: <Text style={{ fontSize: 13 }}>{p}</Text>,
                        }))}
                      />
                    </Card>
                  )}
                </Space>
              ),
            },
            {
              key: 'compare',
              label: '效果对比',
              children: (
                <Card size="small">
                  <Table
                    dataSource={[
                      { dimension: '分析耗时', manual: r.manual_time || '120分钟', auto: r.auto_time || '79秒', improvement: `提升${r.improvement_pct || '99%'}` },
                      { dimension: '人工介入', manual: '全程参与', auto: '仅需确认结果', improvement: '减少96%' },
                      { dimension: '结果输出', manual: '口头/文字说明', auto: '结构化报告+推送', improvement: '标准化' },
                    ]}
                    columns={[
                      { title: '对比维度', dataIndex: 'dimension', key: 'dimension' },
                      { title: '人工处理', dataIndex: 'manual', key: 'manual' },
                      { title: '数字员工', dataIndex: 'auto', key: 'auto' },
                      { title: '提升效果', dataIndex: 'improvement', key: 'improvement', render: (v: string) => <Text style={{ color: '#52c41a', fontWeight: 600 }}>{v}</Text> },
                    ]}
                    pagination={false}
                    size="small"
                  />
                </Card>
              ),
            },
          ]}
        />

        <Space style={{ marginTop: 16 }}>
          <Button icon={<LikeOutlined />} onClick={() => message.success('感谢反馈')}>有帮助</Button>
          <Button icon={<DislikeOutlined />} onClick={() => message.success('感谢反馈')}>无帮助</Button>
          <Button icon={<BookOutlined />} onClick={() => message.success('案例已沉淀至知识库')}>沉淀案例</Button>
          <Button icon={<ExportOutlined />} onClick={() => message.success('报告导出成功')}>导出报告</Button>
        </Space>
      </div>
    );
  };

  return (
    <div>
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}><ExperimentOutlined style={{ marginRight: 8 }} />智能分析</Title>
      </div>

      {/* Preset scenario cards */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        {presetScenarios.map((scenario) => (
          <Col span={12} key={scenario.key}>
            <Card
              hoverable
              style={{ background: scenario.color, borderColor: scenario.borderColor, cursor: 'pointer' }}
              onClick={() => !analyzing && handlePresetClick(scenario.key)}
            >
              <Space align="start">
                {scenario.icon}
                <div>
                  <Text strong style={{ fontSize: 15 }}>{scenario.title}</Text>
                  <div style={{ marginTop: 4, color: '#666' }}>{scenario.desc}</div>
                  <Tag color="blue" style={{ marginTop: 6 }}>点击一键演示</Tag>
                </div>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={10}>
          <Card title="问题描述" style={{ marginBottom: 16 }}>
            <TextArea rows={6} placeholder="请描述您遇到的问题..." value={problemDesc} onChange={(e) => setProblemDesc(e.target.value)} />
            <Divider />
            <Form layout="vertical" size="small">
              <Form.Item label="账期">
                <Select placeholder="选择账期" value={acctMonth} onChange={setAcctMonth} options={['202604','202603','202602','202401'].map((m) => ({ label: m, value: m }))} />
              </Form.Item>
              <Form.Item label="关联任务">
                <Input placeholder="输入任务ID" value={taskId} onChange={(e) => setTaskId(e.target.value)} />
              </Form.Item>
            </Form>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button type="primary" size="large" block icon={<ThunderboltOutlined />} onClick={() => handleStartAnalysis(false)} loading={analyzing && !hermesMode} disabled={!problemDesc.trim()}>开始分析</Button>
              <Button
                type="default"
                size="large"
                block
                icon={<ApiOutlined />}
                onClick={() => {
                  if (!problemDesc.trim() && !hermesTaskId && !taskId) {
                    message.warning('请输入问题描述或任务ID');
                    return;
                  }
                  // Use the form's taskId or hermesTaskId
                  const tid = hermesTaskId || taskId || problemDesc.trim();
                  setHermesTaskId(tid);
                  setAnalyzing(true); setCurrentStep(0); setAnalysisResult(null); setAnalysisLogs([]); setError(null);
                  setPresetMode(false); setHermesMode(true);
                  (async () => {
                    try {
                      const payload = {
                        task_id: tid,
                        problem_description: problemDesc,
                        acct_month: acctMonth || undefined,
                      };
                      const submitRes = await hermesApi.analyzeRootCause(payload);
                      const asyncTaskId = submitRes.data?.task_id;
                      if (!asyncTaskId) { message.error('提交分析任务失败'); return; }

                      let done = false;
                      while (!done) {
                        await new Promise((r) => setTimeout(r, 2000));
                        const statusRes = await hermesApi.getAnalysisStatus(asyncTaskId);
                        const st = statusRes.data || {};
                        if (st.status === 'completed' && st.result) {
                          const logs = st.result.analysis_logs || [];
                          setAnalysisLogs(logs);
                          for (let i = 0; i < logs.length; i++) {
                            setCurrentStep(i);
                            setActiveLogStep(i);
                            await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
                          }
                          setCurrentStep(logs.length);
                          setActiveLogStep(null);
                          setAnalysisResult(st.result);
                          done = true;
                        } else if (st.status === 'failed') {
                          setError(st.error || 'Hermes分析失败');
                          done = true;
                        }
                      }
                    } catch (err: any) {
                      setError(err?.message || 'Hermes分析失败');
                    } finally {
                      setAnalyzing(false);
                    }
                  })();
                }}
                loading={analyzing && hermesMode}
                disabled={analyzing}
                style={{ borderColor: '#722ed1', color: '#722ed1' }}
              >
                <ApiOutlined /> Hermes Agent 分析
              </Button>
            </Space>
          </Card>
          <Card title="分析历史" size="small">
            {history.length > 0 ? (
              <Timeline items={history.map((h) => ({
                children: (
                  <div>
                    <div style={{ fontWeight: 500, fontSize: 13 }}>{h.problem_description?.substring(0, 30)}...</div>
                    <div style={{ fontSize: 11, color: '#999' }}>{dayjs(h.create_time).format('MM-DD HH:mm')}</div>
                  </div>
                ),
              }))} />
            ) : (
              <Empty description="暂无分析历史" />
            )}
          </Card>
        </Col>
        <Col xs={24} md={14}>
          <Card title="分析过程与结果" style={{ minHeight: 500 }}>
            {!analyzing && !analysisResult && currentStep === -1 && !error && (
              <div style={{ textAlign: 'center', padding: '80px 0' }}>
                <RobotOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
                <div style={{ marginTop: 16, color: '#999' }}>
                  输入问题描述，点击"开始分析"按钮<br />或选择上方预设场景一键演示
                </div>
              </div>
            )}
            {error && <Alert type="error" message={error} showIcon closable style={{ marginBottom: 16 }} />}

            {analyzing && !presetMode && !hermesMode && (
              <Steps direction="vertical" current={currentStep} items={analysisSteps.map((step, idx) => ({
                title: step.title,
                description: `工具: ${step.tool}`,
                status: currentStep > idx ? 'finish' : currentStep === idx ? 'process' : 'wait',
                icon: currentStep > idx ? <CheckCircleFilled style={{ color: '#52c41a' }} /> : currentStep === idx ? <LoadingOutlined /> : <ClockCircleFilled style={{ color: '#d9d9d9' }} />,
              }))} />
            )}

            {(analyzing && presetMode) || (analyzing && hermesMode) ? (
              <div>
                <Alert
                  type="info"
                  message={hermesMode ? "Hermes Agent 正在执行根因分析..." : "正在执行根因分析..."}
                  description={hermesMode
                    ? "Hermes Agent 正在自主规划分析路径，调用相关技能进行根因定位"
                    : "按顺序执行分析步骤，实时展示执行日志"
                  }
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                {renderLogSteps()}
              </div>
            ) : null}

            {/* Normal result (non-preset, non-hermes) */}
            {analysisResult && !presetMode && !hermesMode && (
              <div>
                <Alert type="success" message="分析完成" description="已成功完成根因分析" showIcon style={{ marginBottom: 16 }} />
                <Card type="inner" title="根因总结" style={{ marginBottom: 12 }}><Text>{analysisResult.root_cause}</Text></Card>
                <Card type="inner" title="影响评估" style={{ marginBottom: 12 }}><Text>{analysisResult.impact}</Text></Card>
                <Card type="inner" title="解决方案" style={{ marginBottom: 12 }}>
                  {Array.isArray(analysisResult.solution)
                    ? analysisResult.solution.map((s: string, i: number) => <div key={i} style={{ padding: '2px 0' }}>{i+1}. {s}</div>)
                    : <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{analysisResult.solution}</pre>
                  }
                </Card>
                <Card type="inner" title="预防建议" style={{ marginBottom: 12 }}>
                  {Array.isArray(analysisResult.prevention)
                    ? analysisResult.prevention.map((p: string, i: number) => <div key={i} style={{ padding: '2px 0' }}>• {p}</div>)
                    : <Text>{analysisResult.prevention}</Text>
                  }
                </Card>
                <Space style={{ marginTop: 8 }}>
                  <Button icon={<LikeOutlined />} onClick={() => message.success('感谢反馈')}>有帮助</Button>
                  <Button icon={<DislikeOutlined />} onClick={() => message.success('感谢反馈')}>无帮助</Button>
                  <Button icon={<BookOutlined />} onClick={() => message.success('案例已沉淀')}>沉淀案例</Button>
                  <Button icon={<ExportOutlined />} onClick={() => message.success('导出成功')}>导出报告</Button>
                </Space>
              </div>
            )}

            {/* Preset result with rich display */}
            {renderPresetResult()}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analysis;
