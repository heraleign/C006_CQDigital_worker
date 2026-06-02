import React, { useState, useEffect, useCallback } from 'react';
import { Row, Col, Card, Table, Select, DatePicker, Space, Spin, Alert, Empty, Typography, Button, Tooltip, Modal, Timeline, Tabs, Descriptions, message, Tag } from 'antd';
import {
  CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined, WarningOutlined, EyeOutlined,
  BugOutlined, RobotOutlined, CheckCircleFilled, CloseCircleFilled, ClockCircleFilled,
  LoadingOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import MetricCard from '@/components/MetricCard';
import StatusTag from '@/components/StatusTag';
import { auditApi } from '@/services/audit';
import { rootCauseApi } from '@/services/rootCause';
import { useAssistantStore } from '@/stores/useAssistantStore';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const ResultView: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [distribution, setDistribution] = useState<any[]>([]);
  const [details, setDetails] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [acctMonth, setAcctMonth] = useState(dayjs().format('YYYYMM'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { setVisible, sendMessage, setTaskContext } = useAssistantStore();
  const [showDiagnoseModal, setShowDiagnoseModal] = useState(false);
  const [selectedAnomaly, setSelectedAnomaly] = useState<any>(null);
  const [diagnoseStep, setDiagnoseStep] = useState(-1);
  const [diagnoseLogs, setDiagnoseLogs] = useState<any[]>([]);
  const [diagnoseResult, setDiagnoseResult] = useState<any>(null);
  const [diagnosingModalLoading, setDiagnosingModalLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { acct_month: acctMonth };
      const [statRes, trendRes, distRes, detailRes] = await Promise.all([
        auditApi.getResultStats(params),
        auditApi.getResultTrend({ ...params, days: 30 }),
        auditApi.getResultDistribution(params),
        auditApi.getResultDetails({ ...params, page, page_size: 10 }),
      ]);
      setStats(statRes.data);
      setTrend(Array.isArray(trendRes.data) ? trendRes.data : (trendRes.data?.items || []));
      setDistribution(Array.isArray(distRes.data) ? distRes.data : (distRes.data?.items || []));
      setDetails(detailRes.data?.items || []);
      setTotal(detailRes.data?.total || 0);
    } catch (err: any) {
      setError(err?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, [acctMonth, page]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleDiagnose = async (record: any) => {
    setSelectedAnomaly(record);
    setShowDiagnoseModal(true);
    setDiagnoseStep(0);
    setDiagnoseLogs([]);
    setDiagnoseResult(null);
    setDiagnosingModalLoading(true);

    const desc = `指标异常波动：${record.field_name || record.metric_name}检测值${record.check_value}，偏差率${record.deviation_rate}%，超出阈值${record.threshold || '±20%'}`;

    try {
      const res = await rootCauseApi.createAnalysis({
        problem_description: desc,
        task_id: record.task_id,
        acct_month: acctMonth,
        preset_type: 'metric_anomaly',
      });

      const logs = res.data?.analysis_logs || [];
      setDiagnoseLogs(logs);

      for (let i = 0; i < logs.length; i++) {
        setDiagnoseStep(i);
        await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
      }

      setDiagnoseStep(logs.length);

      if (res.data?.root_cause_result) {
        setDiagnoseResult(res.data);
      } else {
        const detailRes = await rootCauseApi.getAnalysisDetail(res.data?.record_id || '', { preset_type: 'metric_anomaly' });
        setDiagnoseResult(detailRes.data || res.data);
      }
    } catch (err: any) {
      message.error(err?.message || '分析失败');
    } finally {
      setDiagnosingModalLoading(false);
    }
  };

  const handleAiConsult = (record: any) => {
    setTaskContext({
      task_name: record.task_name || record.task_id,
      task_id: record.task_id,
      status: record.check_result,
    });
    setVisible(true);
    const question = `帮我分析这条稽核异常：${record.rule_name || '规则'}检测字段${record.field_name || '未知'}，值为${record.check_value || '未知'}，偏差率${record.deviation_rate || 0}%`;
    setTimeout(() => sendMessage(question), 300);
  };

  const handleCloseDiagnoseModal = () => {
    setShowDiagnoseModal(false);
    setSelectedAnomaly(null);
    setDiagnoseStep(-1);
    setDiagnoseLogs([]);
    setDiagnoseResult(null);
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  const trendOption = {
    tooltip: { trigger: 'axis' as const },
    legend: { data: ['通过', '异常', '告警'] },
    grid: { left: 50, right: 20, bottom: 30, top: 40 },
    xAxis: { type: 'category' as const, data: trend.map((t: any) => t.date || t.acct_date) },
    yAxis: { type: 'value' as const },
    series: [
      {
        name: '通过', type: 'line', smooth: true,
        data: trend.map((t: any) => t.passed || t.success || t.normal || 0),
        itemStyle: { color: '#52c41a' },
        areaStyle: { color: 'rgba(82,196,26,0.15)' },
      },
      {
        name: '异常', type: 'line', smooth: true,
        data: trend.map((t: any) => t.failed || t.anomaly || 0),
        itemStyle: { color: '#ff4d4f' },
        areaStyle: { color: 'rgba(255,77,79,0.15)' },
      },
      {
        name: '告警', type: 'line', smooth: true,
        data: trend.map((t: any) => t.alert || t.alert_count || 0),
        itemStyle: { color: '#faad14' },
        areaStyle: { color: 'rgba(250,173,20,0.15)' },
      },
    ],
  };

  const barOption = {
    tooltip: { trigger: 'axis' as const, axisPointer: { type: 'shadow' as const } },
    grid: { left: 50, right: 30, bottom: 30, top: 20 },
    xAxis: { type: 'category' as const, axisLabel: { fontWeight: 'bold' as const } },
    yAxis: { type: 'value' as const },
    series: [{
      type: 'bar' as const,
      barWidth: '50%',
      label: { show: true, position: 'top' as const, fontWeight: 'bold' as const },
      itemStyle: { borderRadius: [6, 6, 0, 0] },
      data: (distribution.length > 0 ? distribution : [
        { name: '严重', value: 5 }, { name: '高', value: 12 },
        { name: '中', value: 28 }, { name: '低', value: 15 },
      ]).map((d: any) => ({
        name: d.name || d.alert_level,
        value: d.value || d.count,
        itemStyle: { color:
          (d.name || d.alert_level) === '严重' || (d.name || d.alert_level) === 'high' ? '#ff4d4f' :
          (d.name || d.alert_level) === '高' || (d.name || d.alert_level) === 'medium' ? '#fa8c16' :
          (d.name || d.alert_level) === '中' || (d.name || d.alert_level) === 'warning' ? '#faad14' :
          '#1677ff'
        },
      })),
    }],
  };

  return (
    <div>
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>
          <EyeOutlined style={{ marginRight: 8 }} />稽核结果
        </Title>
      </div>

      <Space style={{ marginBottom: 16 }}>
        <span>账期:</span>
        <Select value={acctMonth} onChange={(v) => { setAcctMonth(v); setPage(1); }}
          options={Array.from({ length: 6 }, (_, i) => dayjs().subtract(i, 'month').format('YYYYMM')).map((m) => ({ label: m, value: m }))}
          style={{ width: 120 }} />
        <RangePicker picker="date" />
      </Space>

      <Spin spinning={loading}>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={12} md={6}>
            <MetricCard title="稽核执行次数" value={stats?.total_checks || stats?.total_executions || stats?.total || 0}
              icon={<ClockCircleOutlined />} color="#1677ff" />
          </Col>
          <Col xs={12} md={6}>
            <MetricCard title="成功率"
              value={stats?.pass_rate != null ? stats.pass_rate : stats?.success_rate != null ? (stats.success_rate * 100).toFixed(1) : 0}
              icon={<CheckCircleOutlined />} color="#52c41a" suffix="%"
              trend={(stats?.pass_rate || 0) >= 90 ? 'up' : 'down'}
              trendValue={((stats?.pass_rate || 0) - 85).toFixed(1) + '%'} />
          </Col>
          <Col xs={12} md={6}>
            <MetricCard title="异常数" value={stats?.failed || stats?.anomaly_count || 0}
              icon={<CloseCircleOutlined />} color="#ff4d4f" />
          </Col>
          <Col xs={12} md={6}>
            <MetricCard title="待处理数" value={stats?.warning || stats?.pending_count || 0}
              icon={<WarningOutlined />} color="#faad14" />
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} md={14}>
            <Card title="近30天稽核趋势" size="small">
              {trend.length > 0 ? (
                <ReactECharts option={trendOption} style={{ height: 300 }} />
              ) : (
                <Empty description="暂无趋势数据" />
              )}
            </Card>
          </Col>
          <Col xs={24} md={10}>
            <Card title="告警级别分布" size="small">
              <ReactECharts option={barOption} style={{ height: 300 }} />
            </Card>
          </Col>
        </Row>

        <Card title="异常明细" size="small">
          <Table dataSource={details} rowKey={(r) => r.execution_id || r.id}
            columns={[
              { title: '账期', dataIndex: 'acct_date', key: 'acct_date', width: 100, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD') : '-' },
              { title: '任务', dataIndex: 'task_id', key: 'task_id', width: 120, render: (v: string, r: any) => r.task_name || v },
              { title: '规则', dataIndex: 'rule_name', key: 'rule_name', width: 120 },
              { title: '字段', dataIndex: 'field_name', key: 'field_name', width: 100 },
              { title: '检测值', dataIndex: 'check_value', key: 'check_value', width: 90 },
              { title: '偏差率', dataIndex: 'deviation_rate', key: 'deviation_rate', width: 90,
                render: (v: number) => v != null ? (
                  <span style={{ color: Math.abs(v) > 10 ? '#ff4d4f' : '#52c41a' }}>
                    {typeof v === 'number' ? v.toFixed(2) + '%' : v}
                  </span>
                ) : '-',
              },
              { title: '结果', dataIndex: 'check_result', key: 'check_result', width: 90,
                render: (v: string) => <StatusTag status={v || 'pending'} /> },
              {
                title: '操作',
                key: 'action',
                width: 140,
                fixed: 'right' as const,
                render: (_: any, record: any) => {
                  const isFluctuation = record.anomaly_type === 'fluctuation';
                  return (
                    <Tooltip title={isFluctuation ? '对数据波动进行根因诊断分析' : '通过AI助手查询异常详情'}>
                      <Button
                        type={isFluctuation ? 'primary' : 'default'}
                        size="small"
                        danger={isFluctuation}
                        icon={isFluctuation ? <BugOutlined /> : <RobotOutlined />}
                        onClick={() => isFluctuation ? handleDiagnose(record) : handleAiConsult(record)}
                      >
                        {isFluctuation ? '根因诊断' : 'AI咨询'}
                      </Button>
                    </Tooltip>
                  );
                },
              },
            ]}
            pagination={{
              current: page, pageSize: 10, total,
              onChange: (p) => setPage(p),
              showSizeChanger: true,
              showTotal: (t) => '共 ' + t + ' 条',
            }}
            scroll={{ x: 1000 }}
            locale={{ emptyText: <Empty description="暂无异常数据" /> }}
          />
        </Card>
      </Spin>

      <Modal
        title={
          <Space>
            <BugOutlined style={{ color: '#ff4d4f' }} />
            <span>数据波动根因诊断：{selectedAnomaly?.field_name || selectedAnomaly?.rule_name}</span>
            {selectedAnomaly?.deviation_rate != null && (
              <Tag color="red">偏差率 {selectedAnomaly.deviation_rate}%</Tag>
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
    </div>
  );
};

export default ResultView;
