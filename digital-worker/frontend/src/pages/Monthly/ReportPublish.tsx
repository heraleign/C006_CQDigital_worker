import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Space, Tag, Modal, Form, Input, Select, Descriptions, message, Spin, Alert, Empty, Typography, Popconfirm } from 'antd';
import { SendOutlined, DownloadOutlined, EyeOutlined, CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined, PlusOutlined, ReloadOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import MetricCard from '@/components/MetricCard';
import { monthlyApi } from '@/services/monthly';
import type { ReportPublish as ReportPublishType } from '@/types';

const { Title } = Typography;

const ReportPublish: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reports, setReports] = useState<any[]>([]);
  const [detailVisible, setDetailVisible] = useState(false);
  const [scheduleVisible, setScheduleVisible] = useState(false);
  const [exceptionVisible, setExceptionVisible] = useState(false);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const res = await monthlyApi.getReports({ page: 1, page_size: 100 });
      setReports(res.data?.items || (Array.isArray(res.data) ? res.data : []));
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const handlePublish = async (report: any) => {
    try {
      await monthlyApi.publishReport(report.report_id);
      message.success('发布成功');
      fetchData();
    } catch (err: any) { message.error(err?.message || '发布失败'); }
  };

  const handleRepublish = async (report: any) => {
    try {
      await monthlyApi.publishReport(report.report_id, { republish: true });
      message.success('已重新发布');
      fetchData();
    } catch (err: any) { message.error(err?.message || '重新发布失败'); }
  };

  const handleSchedule = async () => {
    try {
      const values = await form.validateFields();
      await monthlyApi.scheduleReport({ ...values, report_name: values.report_name, plan_time: values.plan_time, platform: values.platform });
      message.success('发布计划已创建');
      setScheduleVisible(false);
      form.resetFields();
      fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  const stats = {
    total: reports.length,
    published: reports.filter((r) => r.status === 'published' || r.status === 'completed').length,
    pending: reports.filter((r) => r.status === 'pending' || r.status === 'draft' || r.status === 'scheduled').length,
    failed: reports.filter((r) => r.status === 'failed').length,
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  const columns = [
    { title: '报表类别', dataIndex: 'category', key: 'category', width: 100, render: (v: string) => v ? <Tag>{v}</Tag> : '-' },
    { title: '名称', dataIndex: 'report_name', key: 'report_name' },
    { title: '平台', dataIndex: 'platform', key: 'platform', width: 90, render: (v: string) => v || '-' },
    { title: '计划时间', dataIndex: 'plan_time', key: 'plan_time', width: 150, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-' },
    { title: '实际发布', dataIndex: 'publish_time', key: 'publish_time', width: 150, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-' },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: (v: string) => {
      const m: Record<string, { label: string; color: string }> = {
        published: { label: '已发布', color: '#52c41a' }, completed: { label: '已完成', color: '#52c41a' },
        scheduled: { label: '已计划', color: '#1677ff' }, draft: { label: '草稿', color: '#d9d9d9' },
        pending: { label: '待发布', color: '#faad14' }, failed: { label: '失败', color: '#ff4d4f' },
        generating: { label: '生成中', color: '#1677ff' },
      };
      const s = m[v] || { label: v, color: '#1677ff' };
      return <Tag color={s.color}>{s.label}</Tag>;
    }},
    { title: '操作', key: 'action', width: 200, render: (_: any, r: any) => (
      <Space size="small">
        <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => { setSelectedReport(r); setDetailVisible(true); }}>详情</Button>
        {(r.status === 'published' || r.status === 'completed')
          ? <Button type="link" size="small" icon={<SendOutlined />} onClick={() => handleRepublish(r)}>重新发布</Button>
          : <Button type="link" size="small" icon={<SendOutlined />} style={{ color: '#52c41a' }} onClick={() => handlePublish(r)}>发布</Button>
        }
        {r.status === 'failed' && (
          <Button type="link" size="small" icon={<ExclamationCircleOutlined />} onClick={() => { setSelectedReport(r); setExceptionVisible(true); }}>异常</Button>
        )}
      </Space>
    )},
  ];

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><SendOutlined style={{ marginRight: 8 }} />报表发布</Title></div>
      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData}>刷新</Button>
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setScheduleVisible(true); }}>新建发布计划</Button>
      </Row>
      <Spin spinning={loading}>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={12} md={6}><MetricCard title="报表总数" value={stats.total} icon={<SendOutlined />} color="#1677ff" /></Col>
          <Col xs={12} md={6}><MetricCard title="已发布" value={stats.published} icon={<CheckCircleOutlined />} color="#52c41a" /></Col>
          <Col xs={12} md={6}><MetricCard title="待发布" value={stats.pending} icon={<ClockCircleOutlined />} color="#faad14" /></Col>
          <Col xs={12} md={6}><MetricCard title="发布异常" value={stats.failed} icon={<CloseCircleOutlined />} color="#ff4d4f" /></Col>
        </Row>
        <Card title="报表列表">
          <Table dataSource={reports} rowKey="report_id" columns={columns}
            pagination={{ pageSize: 20, showTotal: (t) => '共 ' + t + ' 条' }}
            locale={{ emptyText: <Empty description="暂无报表数据" /> }} />
        </Card>
      </Spin>

      <Modal title="报表详情" open={detailVisible} onCancel={() => setDetailVisible(false)} footer={null} width={640} destroyOnClose>
        {selectedReport && (
          <div>
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="报表名称">{selectedReport.report_name}</Descriptions.Item>
              <Descriptions.Item label="报表类别">{selectedReport.category || '-'}</Descriptions.Item>
              <Descriptions.Item label="平台">{selectedReport.platform || '-'}</Descriptions.Item>
              <Descriptions.Item label="状态"><StatusTag status={selectedReport.status} /></Descriptions.Item>
              <Descriptions.Item label="计划时间">{selectedReport.plan_time ? dayjs(selectedReport.plan_time).format('YYYY-MM-DD HH:mm') : '-'}</Descriptions.Item>
              <Descriptions.Item label="实际发布">{selectedReport.publish_time ? dayjs(selectedReport.publish_time).format('YYYY-MM-DD HH:mm') : '-'}</Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>

      <Modal title="新建发布计划" open={scheduleVisible} onOk={handleSchedule} onCancel={() => { setScheduleVisible(false); form.resetFields(); }} width={520} destroyOnClose>
        <Form form={form} layout="vertical">
          <Form.Item name="report_name" label="报表名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category" label="报表类别"><Select options={[{ label: '月度报表', value: 'monthly' }, { label: '季度报表', value: 'quarterly' }, { label: '年度报表', value: 'annual' }]} /></Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="platform" label="发布平台"><Select options={[{ label: '邮件', value: 'email' }, { label: '企业微信', value: 'wecom' }, { label: '钉钉', value: 'dingtalk' }, { label: '系统内', value: 'internal' }]} /></Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="描述"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>

      <Modal title="异常详情" open={exceptionVisible} onCancel={() => setExceptionVisible(false)} footer={<Button onClick={() => setExceptionVisible(false)}>关闭</Button>} width={520} destroyOnClose>
        {selectedReport && (
          <div>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="报表">{selectedReport.report_name}</Descriptions.Item>
              <Descriptions.Item label="失败时间">{selectedReport.publish_time ? dayjs(selectedReport.publish_time).format('YYYY-MM-DD HH:mm') : '-'}</Descriptions.Item>
              <Descriptions.Item label="失败原因">{selectedReport.fail_reason || '发布目标平台连接超时'}</Descriptions.Item>
              <Descriptions.Item label="建议">请检查网络连接和目标平台状态后重试，或联系系统管理员</Descriptions.Item>
            </Descriptions>
            <div style={{ marginTop: 16, textAlign: 'right' }}>
              <Button type="primary" icon={<ReloadOutlined />} onClick={() => { handleRepublish(selectedReport); setExceptionVisible(false); }}>重新发布</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ReportPublish;
