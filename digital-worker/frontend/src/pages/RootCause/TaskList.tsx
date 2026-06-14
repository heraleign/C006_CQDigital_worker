import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Select, Tag, Space, Spin, Alert, Empty, Typography, message, Modal, Tooltip, Badge, Timeline, Tabs, Descriptions } from 'antd';
import {
  BugOutlined, RobotOutlined, SearchOutlined, ReloadOutlined,
  CheckCircleFilled, CloseCircleFilled, ClockCircleFilled,
  MinusCircleFilled, LoadingOutlined, ApiOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { rootCauseApi } from '@/services/rootCause';
import { hermesApi } from '@/services/hermes';
import { useAssistantStore } from '@/stores/useAssistantStore';

const { Title, Text } = Typography;

const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  running: { color: '#1890ff', icon: <ClockCircleFilled />, label: '运行中' },
  completed: { color: '#52c41a', icon: <CheckCircleFilled />, label: '已完成' },
  failed: { color: '#ff4d4f', icon: <CloseCircleFilled />, label: '失败' },
  waiting: { color: '#faad14', icon: <MinusCircleFilled />, label: '等待中' },
  pending: { color: '#d9d9d9', icon: <MinusCircleFilled />, label: '待启动' },
  delayed: { color: '#fa8c16', icon: <ClockCircleFilled />, label: '延迟' },
};

const TaskList: React.FC = () => {
  const { setVisible, sendMessage, setTaskContext } = useAssistantStore();
  const [tasks, setTasks] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showDiagnoseModal, setShowDiagnoseModal] = useState(false);
  const [diagnoseTask, setDiagnoseTask] = useState<any>(null);
  const [diagnoseStep, setDiagnoseStep] = useState(-1);
  const [diagnoseLogs, setDiagnoseLogs] = useState<any[]>([]);
  const [diagnoseResult, setDiagnoseResult] = useState<any>(null);
  const [diagnosingModalLoading, setDiagnosingModalLoading] = useState(false);

  // Hermes diagnosis state
  const [showHermesModal, setShowHermesModal] = useState(false);
  const [hermesTask, setHermesTask] = useState<any>(null);
  const [hermesStep, setHermesStep] = useState(-1);
  const [hermesLogs, setHermesLogs] = useState<any[]>([]);
  const [hermesResult, setHermesResult] = useState<any>(null);
  const [hermesLoading, setHermesLoading] = useState(false);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { page, page_size: 15 };
      if (statusFilter) params.status = statusFilter;
      const res = await rootCauseApi.getTaskList(params);
      setTasks(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err: any) {
      setError(err?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const handleDiagnose = async (task: any) => {
    if (task.status === 'failed' || task.status === 'delayed' || task.status === 'waiting') {
      setDiagnoseTask(task);
      setShowDiagnoseModal(true);
      setDiagnoseStep(0);
      setDiagnoseLogs([]);
      setDiagnoseResult(null);
      setDiagnosingModalLoading(true);

      const desc = task.status === 'failed'
        ? `${task.task_name}（${task.task_id}）执行失败`
        : `${task.task_name}（${task.task_id}）状态为${statusConfig[task.status]?.label || task.status}，疑似延迟`;

      try {
        const res = await rootCauseApi.createAnalysis({
          problem_description: desc,
          task_id: task.task_id,
          acct_month: dayjs().format('YYYYMM'),
          preset_type: 'task_delay',
        });

        const logs = res.data?.analysis_logs || [];
        setDiagnoseLogs(logs);

        // Step through logs one by one
        for (let i = 0; i < logs.length; i++) {
          setDiagnoseStep(i);
          await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
        }

        setDiagnoseStep(logs.length);

        // Set result data
        if (res.data?.root_cause_result) {
          setDiagnoseResult(res.data);
        } else {
          // Fetch detail if needed
          const detailRes = await rootCauseApi.getAnalysisDetail(res.data?.record_id || '', { preset_type: 'task_delay' });
          setDiagnoseResult(detailRes.data || res.data);
        }
      } catch (err: any) {
        message.error(err?.message || '分析失败');
      } finally {
        setDiagnosingModalLoading(false);
      }
    } else {
      // Normal task: open AI assistant with task context
      setTaskContext({ task_name: task.task_name, task_id: task.task_id, status: task.status });
      setVisible(true);
      const question = `帮我分析一下任务「${task.task_name}」（${task.task_id}）的上游依赖和影响范围`;
      setTimeout(() => sendMessage(question), 300);
    }
  };

  const handleCloseDiagnoseModal = () => {
    setShowDiagnoseModal(false);
    setDiagnoseTask(null);
    setDiagnoseStep(-1);
    setDiagnoseLogs([]);
    setDiagnoseResult(null);
  };

  const handleHermesDiagnose = async (task: any) => {
    setHermesTask(task);
    setShowHermesModal(true);
    setHermesStep(0);
    setHermesLogs([]);
    setHermesResult(null);
    setHermesLoading(true);

    const desc = task.status === 'failed'
      ? `${task.task_name}（${task.task_id}）执行失败`
      : `${task.task_name}（${task.task_id}）状态为${statusConfig[task.status]?.label || task.status}，疑似延迟`;

    try {
      const submitRes = await hermesApi.analyzeRootCause({
        task_id: task.task_id,
        problem_description: desc,
        acct_month: dayjs().format('YYYYMM'),
      });
      const asyncTaskId = submitRes.data?.task_id;
      if (!asyncTaskId) { message.error('提交分析任务失败'); setHermesLoading(false); return; }

      // Poll until completed
      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, 2000));
        const statusRes = await hermesApi.getAnalysisStatus(asyncTaskId);
        const st = statusRes.data || {};
        if (st.status === 'completed' && st.result) {
          const logs = st.result.analysis_logs || [];
          setHermesLogs(logs);
          for (let i = 0; i < logs.length; i++) {
            setHermesStep(i);
            await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
          }
          setHermesStep(logs.length);
          setHermesResult(st.result);
          done = true;
        } else if (st.status === 'failed') {
          message.error(st.error || 'Hermes分析失败');
          done = true;
        }
      }
    } catch (err: any) {
      message.error(err?.message || 'Hermes分析失败');
    } finally {
      setHermesLoading(false);
    }
  };

  const handleCloseHermesModal = () => {
    setShowHermesModal(false);
    setHermesTask(null);
    setHermesStep(-1);
    setHermesLogs([]);
    setHermesResult(null);
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'task_name',
      key: 'task_name',
      width: 200,
      render: (v: string, r: any) => (
        <Space>
          <Badge status={r.status === 'failed' ? 'error' : r.status === 'completed' ? 'success' : r.status === 'running' ? 'processing' : 'warning'} />
          <Text strong>{v}</Text>
        </Space>
      ),
    },
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 140,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (v: string) => {
        const cfg = statusConfig[v] || { color: '#d9d9d9', icon: <MinusCircleFilled />, label: v };
        return <Tag icon={cfg.icon} color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: '所属模块',
      dataIndex: 'module',
      key: 'module',
      width: 120,
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 160,
      render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-',
    },
    {
      title: '耗时',
      dataIndex: 'duration',
      key: 'duration',
      width: 80,
      render: (v: string) => v || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      fixed: 'right' as const,
      render: (_: any, record: any) => {
        const isAbnormal = record.status === 'failed' || record.status === 'delayed' || record.status === 'waiting';
        return (
          <Space size="small">
            {isAbnormal ? (
              <>
                <Tooltip title="分析任务延迟/失败原因">
                  <Button
                    type="primary"
                    size="small"
                    danger
                    icon={<BugOutlined />}
                    loading={showDiagnoseModal && diagnoseTask?.task_id === record.task_id}
                    onClick={() => handleDiagnose(record)}
                  >
                    根因诊断
                  </Button>
                </Tooltip>
                <Tooltip title="使用 Hermes Agent 自主分析">
                  <Button
                    size="small"
                    icon={<ApiOutlined />}
                    style={{ borderColor: '#722ed1', color: '#722ed1' }}
                    loading={showHermesModal && hermesTask?.task_id === record.task_id}
                    onClick={() => handleHermesDiagnose(record)}
                  >
                    Hermes
                  </Button>
                </Tooltip>
              </>
            ) : (
              <Tooltip title="通过AI助手查询依赖与影响">
                <Button
                  type="default"
                  size="small"
                  icon={<RobotOutlined />}
                  onClick={() => handleDiagnose(record)}
                >
                  AI咨询
                </Button>
              </Tooltip>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>
          <SearchOutlined style={{ marginRight: 8 }} />任务列表
        </Title>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
        <Space wrap>
          <span>状态筛选:</span>
          <Select
            value={statusFilter}
            onChange={(v) => { setStatusFilter(v); setPage(1); }}
            style={{ width: 140 }}
            options={[
              { label: '全部', value: '' },
              { label: '运行中', value: 'running' },
              { label: '已完成', value: 'completed' },
              { label: '失败', value: 'failed' },
              { label: '等待中', value: 'waiting' },
              { label: '延迟', value: 'delayed' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchTasks}>刷新</Button>
        </Space>
        <Space>
          <Tag color="red">失败/延迟 — 根因诊断</Tag>
          <Tag color="purple">Hermes Agent 诊断</Tag>
          <Tag color="blue">正常 — AI助手咨询</Tag>
        </Space>
      </div>

      <Spin spinning={loading}>
        <Card>
          <Table
            dataSource={tasks}
            columns={columns}
            rowKey="task_id"
            pagination={{
              current: page,
              pageSize: 15,
              total,
              onChange: (p) => setPage(p),
              showSizeChanger: false,
              showTotal: (t) => `共 ${t} 个任务`,
            }}
            scroll={{ x: 900 }}
            locale={{ emptyText: <Empty description="暂无任务数据" /> }}
            size="middle"
          />
        </Card>
      </Spin>

      <Modal
        title={
          <Space>
            <BugOutlined style={{ color: '#ff4d4f' }} />
            <span>根因诊断：{diagnoseTask?.task_name}</span>
            {diagnoseTask && (
              <Tag color={diagnoseTask.status === 'failed' ? 'red' : 'orange'}>
                {statusConfig[diagnoseTask.status]?.label || diagnoseTask.status}
              </Tag>
            )}
          </Space>
        }
        open={showDiagnoseModal}
        onCancel={handleCloseDiagnoseModal}
        width={760}
        footer={
          diagnoseResult ? [
            <Button key="close" type="primary" onClick={handleCloseDiagnoseModal}>关闭</Button>,
          ] : null
        }
        destroyOnClose
      >
        {diagnosingModalLoading && diagnoseLogs.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16, color: '#999' }}>正在启动根因分析...</div>
          </div>
        )}

        {diagnoseLogs.length > 0 && !diagnoseResult && (
          <div>
            <Alert type="info" message="正在执行根因分析..." description="按顺序执行分析步骤，实时展示执行日志" showIcon style={{ marginBottom: 16 }} />
            <Timeline
              items={diagnoseLogs.map((log: any, idx: number) => ({
                color: log.status === 'completed' ? 'green' : idx === diagnoseStep ? 'blue' : 'gray',
                dot: log.status === 'completed' ? <CheckCircleFilled style={{ color: '#52c41a', fontSize: 16 }} /> :
                     idx === diagnoseStep ? <LoadingOutlined style={{ color: '#1890ff', fontSize: 16 }} /> :
                     <ClockCircleFilled style={{ color: '#d9d9d9', fontSize: 16 }} />,
                children: (
                  <div style={{ marginBottom: 8, opacity: log.status === 'completed' || idx <= diagnoseStep ? 1 : 0.4 }}>
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
          </div>
        )}

        {diagnoseResult && (
          <div>
            <Alert
              type="success"
              message={
                <Space>
                  <span>✅ 分析完成</span>
                  <Tag color="blue">根因类型：{diagnoseResult.root_cause_result || diagnoseResult.root_cause}</Tag>
                  <Tag color="green">分析耗时：{diagnoseResult.auto_time}</Tag>
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
                        <div style={{ marginTop: 4, fontSize: 15, fontWeight: 500, color: '#cf1322' }}>
                          {diagnoseResult.root_cause_result || diagnoseResult.root_cause}
                        </div>
                      </Card>
                      <Card size="small" title={<span><BugOutlined style={{ marginRight: 6 }} />溯源链路</span>}>
                        <pre style={{ whiteSpace: 'pre-wrap', margin: 0, background: '#f5f5f5', padding: 12, borderRadius: 4, fontSize: 13 }}>
                          {diagnoseResult.trace_path}
                        </pre>
                      </Card>
                      <Card size="small" title="根因详情">
                        <Text>{diagnoseResult.root_cause_detail}</Text>
                      </Card>
                      {(diagnoseResult.source_system || diagnoseResult.source_contact) && (
                        <Descriptions size="small" column={2} bordered>
                          {diagnoseResult.source_system && (
                            <Descriptions.Item label="责任系统">{diagnoseResult.source_system}</Descriptions.Item>
                          )}
                          {diagnoseResult.source_contact && (
                            <Descriptions.Item label="联系人">{diagnoseResult.source_contact}</Descriptions.Item>
                          )}
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
                        items={(diagnoseResult.evidence || []).map((ev: string, i: number) => ({
                          color: i < 2 ? 'red' : 'orange',
                          children: <Text style={{ fontSize: 13 }}>{ev}</Text>,
                        }))}
                      />
                    </Card>
                  ),
                },
                {
                  key: 'solution',
                  label: '处理建议',
                  children: (
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {diagnoseResult.impact_assessment && (
                        <Alert type="warning" message={diagnoseResult.impact_assessment} showIcon style={{ marginBottom: 8 }} />
                      )}
                      <Card size="small" title={diagnoseResult.risk_level ? `⚠️ 风险评估：${diagnoseResult.severity}（${diagnoseResult.risk_level}）` : '解决方案'}>
                        <Timeline
                          items={(diagnoseResult.solution || []).map((s: string) => ({
                            color: s.includes('紧急') ? 'red' : s.includes('长效') ? 'blue' : 'gray',
                            children: <Text style={{ fontSize: 13 }}>{s}</Text>,
                          }))}
                        />
                      </Card>
                      {diagnoseResult.prevention && diagnoseResult.prevention.length > 0 && (
                        <Card size="small" title="🔒 预防措施">
                          <Timeline
                            items={diagnoseResult.prevention.map((p: string) => ({
                              color: 'green',
                              children: <Text style={{ fontSize: 13 }}>{p}</Text>,
                            }))}
                          />
                        </Card>
                      )}
                    </Space>
                  ),
                },
              ]}
            />
          </div>
        )}
      </Modal>

      {/* ── Hermes Diagnosis Modal ──────────────────────────────── */}
      <Modal
        title={
          <Space>
            <ApiOutlined style={{ color: '#722ed1' }} />
            <span>Hermes Agent 诊断：{hermesTask?.task_name}</span>
            {hermesTask && (
              <Tag icon={<ApiOutlined />} color="purple">Hermes Agent</Tag>
            )}
          </Space>
        }
        open={showHermesModal}
        onCancel={handleCloseHermesModal}
        width={760}
        footer={
          hermesResult ? [
            <Button key="close" type="primary" onClick={handleCloseHermesModal}>关闭</Button>,
          ] : null
        }
        destroyOnClose
      >
        {hermesLoading && hermesLogs.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16, color: '#999' }}>Hermes Agent 正在自主规划分析路径...</div>
          </div>
        )}

        {hermesLogs.length > 0 && !hermesResult && (
          <div>
            <Alert
              type="info"
              message="Hermes Agent 正在执行根因分析..."
              description="Agent 正在自主调用技能进行分析，步骤实时更新"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Timeline
              items={hermesLogs.map((log: any, idx: number) => ({
                color: log.status === 'completed' ? 'green' : idx === hermesStep ? 'purple' : 'gray',
                dot: log.status === 'completed' ? <CheckCircleFilled style={{ color: '#52c41a', fontSize: 16 }} /> :
                     idx === hermesStep ? <LoadingOutlined style={{ color: '#722ed1', fontSize: 16 }} /> :
                     <ClockCircleFilled style={{ color: '#d9d9d9', fontSize: 16 }} />,
                children: (
                  <div style={{ marginBottom: 8, opacity: log.status === 'completed' || idx <= hermesStep ? 1 : 0.4 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                      Step {log.step}: {log.action}
                      {log.status === 'completed' && <Tag color="purple" style={{ fontSize: 11 }}>{log.duration}</Tag>}
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
          </div>
        )}

        {hermesResult && (
          <div>
            <Alert
              type="success"
              message={
                <Space>
                  <span>✅ Hermes Agent 分析完成</span>
                  <Tag icon={<ApiOutlined />} color="purple">Hermes Agent</Tag>
                  <Tag color="blue">根因类型：{hermesResult.root_cause_result || hermesResult.root_cause}</Tag>
                  <Tag color="green">分析耗时：{hermesResult.auto_time}</Tag>
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
                      <Card size="small" style={{ background: '#f9f0ff', borderLeft: '3px solid #722ed1' }}>
                        <Text strong>根因结论：</Text>
                        <div style={{ marginTop: 4, fontSize: 15, fontWeight: 500, color: '#cf1322' }}>
                          {hermesResult.root_cause_result || hermesResult.root_cause}
                        </div>
                      </Card>
                      <Card size="small" title={<span><BugOutlined style={{ marginRight: 6 }} />溯源链路</span>}>
                        <pre style={{ whiteSpace: 'pre-wrap', margin: 0, background: '#f5f5f5', padding: 12, borderRadius: 4, fontSize: 13 }}>
                          {hermesResult.trace_path}
                        </pre>
                      </Card>
                      <Card size="small" title="根因详情">
                        <Text>{hermesResult.root_cause_detail}</Text>
                      </Card>
                      {(hermesResult.source_system || hermesResult.source_contact) && (
                        <Descriptions size="small" column={2} bordered>
                          {hermesResult.source_system && (
                            <Descriptions.Item label="责任系统">{hermesResult.source_system}</Descriptions.Item>
                          )}
                          {hermesResult.source_contact && (
                            <Descriptions.Item label="联系人">{hermesResult.source_contact}</Descriptions.Item>
                          )}
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
                        items={(hermesResult.evidence || []).map((ev: string, i: number) => ({
                          color: i < 2 ? 'red' : 'orange',
                          children: <Text style={{ fontSize: 13 }}>{ev}</Text>,
                        }))}
                      />
                    </Card>
                  ),
                },
                {
                  key: 'solution',
                  label: '处理建议',
                  children: (
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {hermesResult.impact_assessment && (
                        <Alert type="warning" message={hermesResult.impact_assessment} showIcon style={{ marginBottom: 8 }} />
                      )}
                      <Card size="small" title={hermesResult.risk_level ? `⚠️ 风险评估：${hermesResult.severity}（${hermesResult.risk_level}）` : '解决方案'}>
                        <Timeline
                          items={(hermesResult.solution || []).map((s: string) => ({
                            color: s.includes('紧急') ? 'red' : s.includes('长效') ? 'blue' : 'gray',
                            children: <Text style={{ fontSize: 13 }}>{s}</Text>,
                          }))}
                        />
                      </Card>
                      {hermesResult.prevention && hermesResult.prevention.length > 0 && (
                        <Card size="small" title="🔒 预防措施">
                          <Timeline
                            items={hermesResult.prevention.map((p: string) => ({
                              color: 'green',
                              children: <Text style={{ fontSize: 13 }}>{p}</Text>,
                            }))}
                          />
                        </Card>
                      )}
                    </Space>
                  ),
                },
              ]}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TaskList;
