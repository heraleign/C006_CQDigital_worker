import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Input, Modal, Form, Select, Tag, message, Spin, Alert, Empty, Rate, Badge, Space, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, StarFilled, BulbOutlined, RobotOutlined, UserOutlined, AppstoreOutlined } from '@ant-design/icons';
import { Typography } from 'antd';
import MetricCard from '@/components/MetricCard';
import { rootCauseApi } from '@/services/rootCause';
import type { ProblemCase } from '@/types';

const { TextArea } = Input;
const { Title } = Typography;

const CaseLibrary: React.FC = () => {
  const [cases, setCases] = useState<ProblemCase[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCase, setEditingCase] = useState<ProblemCase | null>(null);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const params: any = { page, page_size: 12 };
      if (searchText) params.keywords = searchText;
      const res = await rootCauseApi.getCases(params);
      setCases(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [page]);

  const handleCreate = () => { setEditingCase(null); form.resetFields(); setModalVisible(true); };
  const handleEdit = (c: ProblemCase) => { setEditingCase(c); form.setFieldsValue(c); setModalVisible(true); };
  const handleDelete = async (case_id: string) => {
    try { await rootCauseApi.deleteCase(case_id); message.success('删除成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '删除失败'); }
  };
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingCase) { await rootCauseApi.updateCase(editingCase.case_id, values); message.success('更新成功'); }
      else { await rootCauseApi.createCase(values); message.success('创建成功'); }
      setModalVisible(false); fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><AppstoreOutlined style={{ marginRight: 8 }} />案例库</Title></div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} md={6}><MetricCard title="案例总数" value={total} icon={<BulbOutlined />} color="#722ed1" /></Col>
        <Col xs={12} md={6}><MetricCard title="AI生成数" value={cases.filter((c) => c.effectiveness_score > 0).length} icon={<RobotOutlined />} color="#1677ff" /></Col>
        <Col xs={12} md={6}><MetricCard title="人工录入数" value={cases.length - cases.filter((c) => c.effectiveness_score > 0).length} icon={<UserOutlined />} color="#52c41a" /></Col>
        <Col xs={12} md={6}><MetricCard title="平均有效性评分" value={cases.length > 0 ? (cases.reduce((s, c) => s + (c.effectiveness_score || 0), 0) / cases.length).toFixed(1) : 0} icon={<StarFilled />} color="#faad14" /></Col>
      </Row>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Input.Search placeholder="搜索案例(关键词/问题特征)" value={searchText} onChange={(e) => setSearchText(e.target.value)} onSearch={() => { setPage(1); fetchData(); }} style={{ width: 360 }} enterButton />
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新增案例</Button>
      </div>
      <Spin spinning={loading}>
        {cases.length > 0 ? (
          <Row gutter={[16, 16]}>
            {cases.map((c) => (
              <Col xs={24} sm={12} md={8} key={c.case_id}>
                <Card size="small" title={<div style={{ fontWeight: 600, fontSize: 14 }}>{c.problem_title}</div>}
                  extra={<Badge count={c.use_count || 0} style={{ backgroundColor: '#1677ff' }} />}
                  actions={[<Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(c)}>编辑</Button>,
                    <Popconfirm title="确认删除?" onConfirm={() => handleDelete(c.case_id)}><Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button></Popconfirm>]}>
                  <Tag>{c.problem_type}</Tag>
                  <div style={{ fontSize: 12, color: '#666', margin: '8px 0', height: 40, overflow: 'hidden' }}>{c.problem_feature?.substring(0, 80)}...</div>
                  <div style={{ fontSize: 12 }}><strong>根因:</strong> {c.root_cause?.substring(0, 40)}...</div>
                  <div style={{ fontSize: 12 }}><strong>方案:</strong> {c.solution?.substring(0, 40)}...</div>
                  {c.keywords?.split(',').map((k) => <Tag key={k} style={{ fontSize: 10, marginTop: 4 }}>{k.trim()}</Tag>)}
                  <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Rate disabled value={Math.round((c.effectiveness_score || 0) / 20)} count={5} style={{ fontSize: 14 }} />
                    <span style={{ fontSize: 11, color: '#999' }}>{c.effectiveness_score || 0}%</span>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        ) : <Empty description="暂无案例数据" />}
      </Spin>
      <Modal title={editingCase ? '编辑案例' : '新增案例'} open={modalVisible} onOk={handleSubmit} onCancel={() => setModalVisible(false)} width={700} destroyOnClose>
        <Form form={form} layout="vertical">
          <Form.Item name="problem_type" label="问题类型" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="problem_title" label="问题标题" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="problem_feature" label="问题特征"><TextArea rows={3} /></Form.Item>
          <Form.Item name="root_cause" label="根因" rules={[{ required: true }]}><TextArea rows={3} /></Form.Item>
          <Form.Item name="solution" label="解决方案" rules={[{ required: true }]}><TextArea rows={3} /></Form.Item>
          <Form.Item name="keywords" label="关键词"><Input placeholder="逗号分隔" /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CaseLibrary;
