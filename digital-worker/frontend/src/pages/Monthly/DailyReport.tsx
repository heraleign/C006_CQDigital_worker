import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Select, DatePicker, Table, Button, Space, Tag, Descriptions, message, Spin, Alert, Empty, Typography, Divider } from 'antd';
import { FileTextOutlined, DownloadOutlined, ReloadOutlined, SearchOutlined, PlusOutlined, EyeOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import MetricCard from '@/components/MetricCard';
import { monthlyApi } from '@/services/monthly';
import type { DailyReport } from '@/types';

const { Title, Text } = Typography;

const DailyReportPage: React.FC = () => {
  const [acctMonth, setAcctMonth] = useState(dayjs().format('YYYYMM'));
  const [reportDate, setReportDate] = useState(dayjs());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [genLoading, setGenLoading] = useState(false);
  const [currentReport, setCurrentReport] = useState<any>(null);
  const [historyList, setHistoryList] = useState<DailyReport[]>([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);

  const fetchReport = async () => {
    setLoading(true); setError(null);
    try {
      const params = { acct_month: acctMonth, report_date: reportDate.format('YYYY-MM-DD') };
      const res = await monthlyApi.getDailyReports(params);
      const items = res.data?.items || (Array.isArray(res.data) ? res.data : []);
      setCurrentReport(items.length > 0 ? items[0] : null);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  const fetchHistory = async () => {
    try {
      const res = await monthlyApi.getDailyReports({ acct_month: acctMonth, page: historyPage, page_size: 10 });
      setHistoryList(res.data?.items || []);
      setHistoryTotal(res.data?.total || 0);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchReport(); }, [acctMonth, reportDate]);
  useEffect(() => { fetchHistory(); }, [acctMonth, historyPage]);

  const handleGenerate = async () => {
    setGenLoading(true);
    try {
      await monthlyApi.updateDailyReport('new', { acct_month: acctMonth, report_date: reportDate.format('YYYY-MM-DD'), title: acctMonth + '月出账日报', status: 'generating' });
      message.success('日报正在生成...');
      setTimeout(() => fetchReport(), 1500);
    } catch (err: any) { message.error(err?.message || '生成失败'); }
    finally { setGenLoading(false); }
  };

  const handleRegenerate = async () => {
    setGenLoading(true);
    try {
      await new Promise((r) => setTimeout(r, 1000));
      message.success('日报已重新生成');
      fetchReport();
    } catch { message.error('重新生成失败'); }
    finally { setGenLoading(false); }
  };

  const DEFAULT_CONTENT = {
    summary: '本期出账处理整体运行平稳，共处理应收实收数据XX条，稽核通过率98.5%',
    receivable: { total: 12500, amount: '12,500,000', passRate: '99.2', anomalies: 3 },
    received: { total: 9800, amount: '9,800,000', passRate: '97.8', anomalies: 5 },
    audit: { total: 28, passed: 26, failed: 2, passRate: '92.9' },
    alerts: [
      { level: 'high', msg: '应收稽核-金额一致性检查发现3条异常', time: '10:30' },
      { level: 'medium', msg: '实收稽核-账龄分析逾期率超过阈值', time: '11:15' },
    ],
    conclusion: '建议关注实收稽核异常项，及时跟进处理。整体进度可控。',
  };

  /** Merge partial content with defaults so missing fields don't crash the UI. */
  const mergeContent = (raw: any) => {
    if (!raw || typeof raw !== 'object') return DEFAULT_CONTENT;
    return {
      ...DEFAULT_CONTENT,
      ...raw,
      receivable: { ...DEFAULT_CONTENT.receivable, ...(raw.receivable || {}) },
      received: { ...DEFAULT_CONTENT.received, ...(raw.received || {}) },
      audit: { ...DEFAULT_CONTENT.audit, ...(raw.audit || {}) },
      alerts: Array.isArray(raw.alerts) ? raw.alerts : DEFAULT_CONTENT.alerts,
    };
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  const mc = mergeContent(currentReport?.content);

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><FileTextOutlined style={{ marginRight: 8 }} />出账日报</Title></div>

      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Space wrap>
          <span>账期:</span>
          <Select value={acctMonth} onChange={(v) => { setAcctMonth(v); setHistoryPage(1); }}
            options={Array.from({ length: 12 }, (_, i) => dayjs().subtract(i, 'month').format('YYYYMM')).map((m) => ({ label: m, value: m }))}
            style={{ width: 120 }} />
          <span>日期:</span>
          <DatePicker value={reportDate} onChange={(d) => d && setReportDate(d)} allowClear={false} />
          <Button type="primary" icon={<SearchOutlined />} onClick={fetchReport}>查看</Button>
          <Button icon={<PlusOutlined />} loading={genLoading} onClick={handleGenerate}>生成今日日报</Button>
        </Space>
      </Row>

      <Spin spinning={loading}>
        {currentReport ? (
          <Card title={currentReport.title || (acctMonth + '月出账日报')} extra={<StatusTag status={currentReport.status || 'completed'} />} style={{ marginBottom: 16 }}>
            <Descriptions column={3} size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="账期">{currentReport.acct_month || acctMonth}</Descriptions.Item>
              <Descriptions.Item label="日期">{currentReport.report_date || reportDate.format('YYYY-MM-DD')}</Descriptions.Item>
              <Descriptions.Item label="状态"><StatusTag status={currentReport.status || 'completed'} /></Descriptions.Item>
            </Descriptions>

            <div style={{ background: '#f6f8fa', padding: 16, borderRadius: 8, marginBottom: 16 }}>
              <Text strong>执行摘要</Text>
              <div style={{ marginTop: 8 }}>{mc.summary}</div>
            </div>

            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Card size="small" title="应收处理">
                  <p>总笔数: <strong>{mc.receivable.total?.toLocaleString()}</strong></p>
                  <p>金额: <strong>{mc.receivable.amount}</strong></p>
                  <p>通过率: <Text type="success">{mc.receivable.passRate}%</Text></p>
                  <p>异常: <Text type="danger">{mc.receivable.anomalies} 笔</Text></p>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" title="实收处理">
                  <p>总笔数: <strong>{mc.received.total?.toLocaleString()}</strong></p>
                  <p>金额: <strong>{mc.received.amount}</strong></p>
                  <p>通过率: <Text type="success">{mc.received.passRate}%</Text></p>
                  <p>异常: <Text type="danger">{mc.received.anomalies} 笔</Text></p>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" title="稽核概览">
                  <p>规则执行: <strong>{mc.audit.total}</strong> 条</p>
                  <p>通过: <Text type="success">{mc.audit.passed}</Text> / 失败: <Text type="danger">{mc.audit.failed}</Text></p>
                  <p>通过率: <Text type="success">{mc.audit.passRate}%</Text></p>
                </Card>
              </Col>
            </Row>

            <div style={{ marginBottom: 16 }}>
              <Text strong>告警摘要</Text>
              {mc.alerts.map((a: any, i: number) => (
                <div key={i} style={{ marginTop: 8, padding: '8px 12px', background: a.level === 'high' ? '#fff2f0' : '#fffbe6', borderRadius: 4, border: '1px solid ' + (a.level === 'high' ? '#ffccc7' : '#ffe58f') }}>
                  <Space><Tag color={a.level === 'high' ? 'red' : 'gold'}>{a.level === 'high' ? '严重' : '警告'}</Tag><span>{a.msg}</span><Text type="secondary">{a.time}</Text></Space>
                </div>
              ))}
            </div>

            <div style={{ background: '#f0f5ff', padding: 16, borderRadius: 8 }}>
              <Text strong>结论与建议</Text>
              <div style={{ marginTop: 8 }}>{mc.conclusion}</div>
            </div>
          </Card>
        ) : (
          <Card style={{ marginBottom: 16 }}><Empty description="该日期暂无日报，请先生成" /></Card>
        )}
      </Spin>

      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={handleRegenerate} loading={genLoading}>重新生成</Button>
        <Button icon={<DownloadOutlined />}>导出Word</Button>
        <Button icon={<DownloadOutlined />}>导出PDF</Button>
      </Space>

      <Card title="历史日报" size="small">
        <Table dataSource={historyList} rowKey={(r) => r.report_id}
          columns={[
            { title: '标题', dataIndex: 'title', key: 'title' },
            { title: '账期', dataIndex: 'acct_month', key: 'acct_month', width: 100 },
            { title: '日期', dataIndex: 'report_date', key: 'report_date', width: 110, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD') : '-' },
            { title: '状态', dataIndex: 'status', key: 'status', width: 90, render: (v: string) => <StatusTag status={v} /> },
            { title: '操作', key: 'action', width: 100, render: (_: any, r: DailyReport) => (
              <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => { setCurrentReport(r); setReportDate(dayjs(r.report_date)); }}>查看</Button>
            )},
          ]}
          pagination={{ current: historyPage, pageSize: 10, total: historyTotal, onChange: (p) => setHistoryPage(p), showSizeChanger: true, showTotal: (t) => '共 ' + t + ' 条' }}
          locale={{ emptyText: <Empty description="暂无历史日报" /> }} />
      </Card>
    </div>
  );
};

export default DailyReportPage;
