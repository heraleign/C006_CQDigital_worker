import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Typography, Table, Badge, Space } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  BellOutlined,
  TrophyOutlined,
  PercentageOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import ReactEChartsCore from 'echarts-for-react';
import MetricCard from '@/components/MetricCard';
import StatusTag from '@/components/StatusTag';
import type { DashboardSummary, TrendItem, AuditAlert, ChatMessage, ChatSession } from '@/types';
import { dashboardApi } from '@/services/dashboard';

const { Title, Text } = Typography;

const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [alerts, setAlerts] = useState<AuditAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [summaryRes, trendsRes, alertsRes] = await Promise.all([
          dashboardApi.getSummary(),
          dashboardApi.getTrends(),
          dashboardApi.getRecentAlerts(),
        ]);
        setSummary(summaryRes.data || summaryRes);
        setTrends(trendsRes.data || trendsRes || []);
        setAlerts(alertsRes.data?.items || []);
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const trendOption = {
    tooltip: { trigger: 'axis' as const },
    legend: { data: ['收入稽核', '用户稽核', '产品稽核'], bottom: 0, icon: 'circle', itemWidth: 8 },
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category' as const,
      data: Array.from(new Set(trends.map((t) => t.date))),
      axisLabel: { fontSize: 11 },
    },
    yAxis: { type: 'value' as const, min: 70, max: 100, axisLabel: { fontSize: 11, formatter: '{value}%' } },
    series: ['收入稽核', '用户稽核', '产品稽核'].map((name) => ({
      name,
      type: 'line' as const,
      smooth: true,
      data: trends.filter((t) => t.category === name).map((t) => t.value),
      symbol: 'circle',
      symbolSize: 6,
    })),
  };

  const alertColumns = [
    {
      title: '告警级别',
      dataIndex: 'alert_level',
      key: 'alert_level',
      width: 80,
      render: (level: string) => <StatusTag status={level} type="alert" />,
    },
    {
      title: '告警标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '来源任务',
      dataIndex: 'source_task',
      key: 'source_task',
      width: 120,
    },
    {
      title: '时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
      render: (t: string) => t ? t.substring(11, 19) : '-',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>总览看板</Title>
      </div>

      {/* Summary cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={8} lg={4}>
          <MetricCard
            title="总任务数"
            value={summary?.total_tasks ?? 0}
            icon={<CheckCircleOutlined />}
            color="#1677ff"
          />
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <MetricCard
            title="运行中"
            value={summary?.running_tasks ?? 0}
            icon={<SyncOutlined />}
            color="#722ed1"
          />
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <MetricCard
            title="已完成"
            value={summary?.completed_tasks ?? 0}
            icon={<TrophyOutlined />}
            color="#52c41a"
          />
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <MetricCard
            title="失败"
            value={summary?.failed_tasks ?? 0}
            icon={<CloseCircleOutlined />}
            color="#ff4d4f"
          />
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <MetricCard
            title="告警数"
            value={summary?.alert_count ?? 0}
            icon={<BellOutlined />}
            color="#faad14"
          />
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <MetricCard
            title="质量评分"
            value={summary?.quality_score ?? 0}
            suffix="分"
            precision={1}
            icon={<PercentageOutlined />}
            color="#13c2c2"
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Quality trend chart */}
        <Col xs={24} lg={16}>
          <Card title="质量趋势" styles={{ body: { padding: '12px 12px 0' } }}>
            <ReactEChartsCore option={trendOption} style={{ height: 320 }} />
          </Card>
        </Col>

        {/* Recent alerts */}
        <Col xs={24} lg={8}>
          <Card title="最近告警" styles={{ body: { padding: 0 } }}>
            <Table
              dataSource={alerts.slice(0, 8)}
              columns={alertColumns}
              rowKey="alert_id"
              pagination={false}
              size="small"
              showHeader={false}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
