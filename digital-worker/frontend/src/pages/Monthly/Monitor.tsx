import React, { useState, useEffect, useCallback } from 'react';
import { Row, Col, Card, Select, Switch, Button, Progress, Steps, Table, Tag, message, Spin, Alert, Empty, Space, Typography, Statistic } from 'antd';
import { ReloadOutlined, ExportOutlined, BarChartOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import ProgressTimeline from '@/components/ProgressTimeline';
import { monthlyApi } from '@/services/monthly';
import type { MonthlyProgress, Milestone, TaskMonitor } from '@/types';

const { Title } = Typography;

const milestoneNames = ['1号批次', '应收宽表', '应收稽核', 'SAP上传', '实收宽表', '实收稽核', '报表批次', '报表发布'];

const Monitor: React.FC = () => {
  const [acctMonth, setAcctMonth] = useState(dayjs().format('YYYYMM'));
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [progress, setProgress] = useState<MonthlyProgress | null>(null);
  const [milestones, setMilestones] = useState<any[]>([]);
  const [runningTasks, setRunningTasks] = useState<TaskMonitor[]>([]);
  const [tasks, setTasks] = useState<TaskMonitor[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [stageFilter, setStageFilter] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { acct_month: acctMonth };
      const [progRes, mileRes, runRes, taskRes] = await Promise.all([
        monthlyApi.getProgress(params),
        monthlyApi.getMilestones(params),
        monthlyApi.getRunningTasks(params),
        monthlyApi.getTasks({ ...params, page, page_size: 10, stage: stageFilter }),
      ]);
      setProgress(progRes.data);
      const mileItems = Array.isArray(mileRes.data) ? mileRes.data : (mileRes.data?.items || []);
      setMilestones(mileItems.length > 0 ? mileItems : milestoneNames.map((name, idx) => ({
        milestone_id: 'm' + idx, milestone_name: name,
        status: idx === 0 ? 'running' : 'pending',
        target_time: dayjs().add(idx, 'day').format('YYYY-MM-DD HH:mm'),
        actual_time: idx < 2 ? dayjs().format('YYYY-MM-DD HH:mm') : undefined,
        delay_minutes: idx === 1 ? 15 : 0,
      })));
      setRunningTasks(Array.isArray(runRes.data) ? runRes.data : (runRes.data?.items || []));
      setTasks(taskRes.data?.items || []);
      setTotal(taskRes.data?.total || 0);
    } catch (err: any) {
      setError(err?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, [acctMonth, page, stageFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;
    const t = setInterval(fetchData, 30000);
    return () => clearInterval(t);
  }, [autoRefresh, fetchData]);

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  const pct = progress?.progress_pct || 0;
  const completed = progress?.completed_tasks || 0;
  const totalTasks = progress?.total_tasks || 0;

  const pieOption = {
    tooltip: { trigger: 'item' as const, formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie' as const,
      radius: ['45%', '70%'],
      center: ['50%', '55%'],
      label: { show: true, formatter: '{b}\n{d}%' },
      data: [
        { value: completed, name: '已完成', itemStyle: { color: '#52c41a' } },
        { value: Math.max(0, totalTasks - completed), name: '未完成', itemStyle: { color: '#d9d9d9' } },
      ],
    }],
  };

  const stageOptions = [
    { label: '全部', value: '' },
    { label: '数据准备', value: 'data_prep' },
    { label: '应收处理', value: 'receivable' },
    { label: '实收处理', value: 'received' },
    { label: '稽核校验', value: 'audit' },
    { label: '报表生成', value: 'report' },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>
          <BarChartOutlined style={{ marginRight: 8 }} />进度监控
        </Title>
      </div>

      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Space wrap>
          <span>账期:</span>
          <Select value={acctMonth} onChange={setAcctMonth} style={{ width: 120 }}
            options={Array.from({ length: 12 }, (_, i) => dayjs().subtract(i, 'month').format('YYYYMM')).map((m) => ({ label: m, value: m }))} />
          <span style={{ marginLeft: 16 }}>自动刷新:</span>
          <Switch checked={autoRefresh} onChange={setAutoRefresh} />
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData}>手动刷新</Button>
          <Button icon={<ExportOutlined />}>导出日报</Button>
        </Space>
      </Row>

      <Spin spinning={loading}>
        <Card style={{ marginBottom: 16 }}>
          <Row align="middle" gutter={[16, 16]}>
            <Col xs={24} md={6}>
              <Statistic
                title={progress?.status === 'completed' ? '已完成' : progress?.status === 'running' ? '执行中' : '待开始'}
                value={pct} suffix="%" valueStyle={{ color: pct >= 100 ? '#52c41a' : '#1677ff' }}
              />
            </Col>
            <Col xs={24} md={12}>
              <Progress percent={Math.round(pct)} size="default" strokeColor={{
                '0%': '#1677ff',
                '100%': '#52c41a',
              }} />
              <div style={{ marginTop: 8, color: '#666', fontSize: 13 }}>
                整体进度 {completed}/{totalTasks} 预计完成: {progress?.estimated_completion || '计算中...'}
              </div>
            </Col>
            <Col xs={24} md={6}>
              <Space direction="vertical" size={2}>
                <span style={{ fontSize: 13, color: '#666' }}>完成: <strong>{completed}</strong> / {totalTasks}</span>
                <span style={{ fontSize: 13, color: '#666' }}>预计完成: {progress?.estimated_completion || '-'}</span>
              </Space>
            </Col>
          </Row>
        </Card>

        <Card title="里程碑" size="small" style={{ marginBottom: 16 }}>
          <ProgressTimeline
            milestones={milestones.map((m) => ({ name: m.milestone_name, status: m.status, time: m.actual_time || m.target_time || '' }))}
            current={milestones.findIndex((m) => m.status === 'running' || m.status === 'processing')}
          />
        </Card>

        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} md={10}>
            <Card title="任务完成分布" size="small">
              <ReactECharts option={pieOption} style={{ height: 260 }} />
            </Card>
          </Col>
          <Col xs={24} md={14}>
            <Card title="运行中任务" size="small">
              <Table dataSource={runningTasks} rowKey={(r) => r.task_id || r.task_code}
                pagination={false} size="small"
                columns={[
                  { title: '任务名', dataIndex: 'task_name', key: 'task_name' },
                  { title: '状态', dataIndex: 'status', key: 'status', width: 90,
                    render: (v: string) => <StatusTag status={v} /> },
                  { title: '耗时', dataIndex: 'duration', key: 'duration', width: 80,
                    render: (v: number) => v != null ? v + 'min' : '-' },
                  { title: '进度', dataIndex: 'progress_pct', key: 'progress_pct', width: 140,
                    render: (v: number) => <Progress percent={v || 0} size="small" /> },
                ]}
                locale={{ emptyText: <Empty description="无运行中任务" /> }} />
            </Card>
          </Col>
        </Row>

        <Card title="阶段任务列表" size="small">
          <div style={{ marginBottom: 16 }}>
            <Space wrap>
              <span>阶段筛选:</span>
              {stageOptions.map((opt) => (
                <Tag key={opt.value} color={stageFilter === opt.value || (!stageFilter && opt.value === '') ? '#1677ff' : undefined}
                  style={{ cursor: 'pointer' }} onClick={() => setStageFilter(opt.value || undefined)}>
                  {opt.label}
                </Tag>
              ))}
            </Space>
          </div>
          <Table dataSource={tasks} rowKey={(r) => r.task_id || r.task_code}
            columns={[
              { title: '任务名', dataIndex: 'task_name', key: 'task_name' },
              { title: '阶段', dataIndex: 'stage', key: 'stage', width: 100,
                render: (v: string) => <Tag>{v || '-'}</Tag> },
              { title: '状态', dataIndex: 'status', key: 'status', width: 90,
                render: (v: string) => <StatusTag status={v} /> },
              { title: '开始时间', dataIndex: 'start_time', key: 'start_time', width: 150,
                render: (v: string) => v ? dayjs(v).format('MM-DD HH:mm') : '-' },
              { title: '耗时', dataIndex: 'duration', key: 'duration', width: 70,
                render: (v: number) => v != null ? v + 'min' : '-' },
              { title: '进度', dataIndex: 'progress_pct', key: 'progress_pct', width: 120,
                render: (v: number) => <Progress percent={v || 0} size="small" /> },
            ]}
            pagination={{
              current: page, pageSize: 10, total,
              onChange: (p) => setPage(p),
              showSizeChanger: true,
              showTotal: (t) => '共 ' + t + ' 条',
            }}
            scroll={{ x: 700 }}
            locale={{ emptyText: <Empty description="暂无任务" /> }} />
        </Card>
      </Spin>
    </div>
  );
};

export default Monitor;
