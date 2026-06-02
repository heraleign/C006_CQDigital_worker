import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Select, message, Spin, Alert, Empty, Space, Typography } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, BulbOutlined, RiseOutlined, ClockCircleOutlined } from '@ant-design/icons';
import StatusTag from '@/components/StatusTag';
import MetricCard from '@/components/MetricCard';
import { rootCauseApi } from '@/services/rootCause';
import type { Suggestion } from '@/types';

const { Title } = Typography;

const Suggestions: React.FC = () => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterPriority, setFilterPriority] = useState<string | undefined>(undefined);
  const [filterStatus, setFilterStatus] = useState<string | undefined>(undefined);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const params: any = { page, page_size: 20 };
      if (filterPriority) params.priority = filterPriority;
      if (filterStatus) params.status = filterStatus;
      const res = await rootCauseApi.getSuggestions(params);
      setSuggestions(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [page, filterPriority, filterStatus]);

  const handleAdopt = async (id: string) => {
    try { await rootCauseApi.adoptSuggestion(id); message.success('建议已采纳'); fetchData(); }
    catch (err: any) { message.error(err?.message || '操作失败'); }
  };
  const handleIgnore = async (id: string) => {
    try { await rootCauseApi.ignoreSuggestion(id); message.success('建议已忽略'); fetchData(); }
    catch (err: any) { message.error(err?.message || '操作失败'); }
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><BulbOutlined style={{ marginRight: 8 }} />改进建议</Title></div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} md={6}><MetricCard title="建议总数" value={total} icon={<BulbOutlined />} color="#722ed1" /></Col>
        <Col xs={12} md={6}><MetricCard title="待处理" value={suggestions.filter((s) => s.status === 'pending').length} icon={<ClockCircleOutlined />} color="#faad14" /></Col>
        <Col xs={12} md={6}><MetricCard title="已采纳" value={suggestions.filter((s) => s.status === 'adopted').length} icon={<CheckCircleOutlined />} color="#52c41a" /></Col>
        <Col xs={12} md={6}><MetricCard title="已忽略" value={suggestions.filter((s) => s.status === 'ignored').length} icon={<CloseCircleOutlined />} color="#d9d9d9" /></Col>
      </Row>
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Select placeholder="优先级" allowClear style={{ width: 120 }} value={filterPriority} onChange={setFilterPriority}
            options={[{ label: '高', value: 'high' }, { label: '中', value: 'medium' }, { label: '低', value: 'low' }]} />
          <Select placeholder="状态" allowClear style={{ width: 120 }} value={filterStatus} onChange={setFilterStatus}
            options={[{ label: '待处理', value: 'pending' }, { label: '已采纳', value: 'adopted' }, { label: '已忽略', value: 'ignored' }]} />
        </Space>
      </div>
      <Spin spinning={loading}>
        {suggestions.length > 0 ? (
          <Row gutter={[16, 16]}>
            {suggestions.map((s) => (
              <Col xs={24} key={s.id}>
                <Card size="small"
                  actions={s.status === 'pending' ? [
                    <Button type="primary" size="small" icon={<CheckCircleOutlined />} onClick={() => handleAdopt(s.id)}>采纳</Button>,
                    <Button size="small" icon={<CloseCircleOutlined />} onClick={() => handleIgnore(s.id)}>忽略</Button>,
                  ] : undefined}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space><StatusTag status={s.priority} /><StatusTag status={s.status} /><span style={{ fontWeight: 600 }}>{s.title}</span></Space>
                  </div>
                  <div style={{ marginTop: 8, color: '#666' }}>{s.content}</div>
                  {s.expected_benefit && <div style={{ marginTop: 4, fontSize: 12, color: '#52c41a' }}><RiseOutlined /> 预期收益: {s.expected_benefit}</div>}
                </Card>
              </Col>
            ))}
          </Row>
        ) : <Empty description="暂无改进建议" />}
      </Spin>
    </div>
  );
};

export default Suggestions;
