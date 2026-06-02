import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Space, Input, Modal, Form, Select, Tag, message, Spin, Alert, Empty, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, BookOutlined } from '@ant-design/icons';
import { Typography, Table, Tabs } from 'antd';
import dayjs from 'dayjs';
import { rootCauseApi } from '@/services/rootCause';
import type { KnowledgeDoc, AnalysisPath, LineageNode, LineageEdge } from '@/types';

const { TextArea } = Input;
const { Title } = Typography;

const KnowledgeBase: React.FC = () => {
  const [activeTab, setActiveTab] = useState('knowledge');
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lineageNodes, setLineageNodes] = useState<LineageNode[]>([]);
  const [lineageEdges, setLineageEdges] = useState<LineageEdge[]>([]);
  const [paths, setPaths] = useState<AnalysisPath[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDoc, setEditingDoc] = useState<KnowledgeDoc | null>(null);
  const [form] = Form.useForm();
  const [pathModalVisible, setPathModalVisible] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'knowledge') {
        const res = await rootCauseApi.getKnowledge({ page, page_size: 12 });
        setDocs(res.data?.items || []);
        setTotal(res.data?.total || 0);
      } else if (activeTab === 'lineage') {
        const res = await rootCauseApi.getLineage();
        setLineageNodes(res.data?.nodes || []);
        setLineageEdges(res.data?.edges || []);
      } else if (activeTab === 'paths') {
        const res = await rootCauseApi.getAnalysisPaths({ page: 1, page_size: 50 });
        setPaths(res.data?.items || []);
      }
    } catch (err: any) {
      setError(err?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [activeTab, page]);

  const handleCreate = () => { setEditingDoc(null); form.resetFields(); setModalVisible(true); };
  const handleEdit = (doc: KnowledgeDoc) => { setEditingDoc(doc); form.setFieldsValue(doc); setModalVisible(true); };
  const handleDelete = async (doc_id: string) => {
    try { await rootCauseApi.deleteKnowledge(doc_id); message.success('删除成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '删除失败'); }
  };
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingDoc) { await rootCauseApi.updateKnowledge(editingDoc.doc_id, values); message.success('更新成功'); }
      else { await rootCauseApi.createKnowledge(values); message.success('创建成功'); }
      setModalVisible(false); fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  const TABS = [
    {
      key: 'knowledge', label: '运维知识',
      children: (
        <div>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新增知识</Button>
          </div>
          <Spin spinning={loading}>
            {docs.length > 0 ? (
              <Row gutter={[16, 16]}>
                {docs.map((doc) => (
                  <Col xs={24} sm={12} md={8} key={doc.doc_id}>
                    <Card size="small" title={<span style={{ fontSize: 14 }}>{doc.title}</span>}
                      extra={<Space><Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(doc)} />
                        <Popconfirm title="确认删除?" onConfirm={() => handleDelete(doc.doc_id)}>
                          <Button type="link" size="small" danger icon={<DeleteOutlined />} /></Popconfirm></Space>}>
                      <Tag>{doc.category}</Tag>
                      <div style={{ marginTop: 8, fontSize: 12, color: '#666', height: 60, overflow: 'hidden' }}>{doc.content?.substring(0, 100)}...</div>
                      <div style={{ marginTop: 8 }}>{doc.tags?.map((t) => <Tag key={t} style={{ fontSize: 10 }}>{t}</Tag>)}</div>
                      <div style={{ marginTop: 8, fontSize: 11, color: '#999' }}>{dayjs(doc.create_time).format('YYYY-MM-DD')}</div>
                    </Card>
                  </Col>
                ))}
              </Row>
            ) : <Empty description="暂无知识文档" />}
          </Spin>
        </div>
      ),
    },
    {
      key: 'lineage', label: '血缘关系',
      children: (
        <div>
          <div style={{ marginBottom: 16 }}><Input.Search placeholder="搜索表名或字段名" style={{ width: 300 }} /></div>
          <Card>
            {lineageNodes.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, padding: 16 }}>
                {lineageNodes.map((n: LineageNode) => (
                  <div key={n.id} style={{ padding: '8px 16px', background: '#e6f4ff', border: '1px solid #91caff', borderRadius: 6, fontSize: 12 }}>{n.name}</div>
                ))}
              </div>
            ) : <Empty description="暂无血缘数据" />}
          </Card>
        </div>
      ),
    },
    {
      key: 'paths', label: '分析路径',
      children: (
        <div>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setPathModalVisible(true)}>新建路径</Button>
          </div>
          <Table dataSource={paths} columns={[
            { title: '路径ID', dataIndex: 'path_id', key: 'path_id', width: 100 },
            { title: '问题类型', dataIndex: 'problem_type', key: 'problem_type', width: 120 },
            { title: '步骤顺序', dataIndex: 'step_order', key: 'step_order', width: 80 },
            { title: '步骤名称', dataIndex: 'step_name', key: 'step_name' },
            { title: '工具编码', dataIndex: 'tool_code', key: 'tool_code', width: 100 },
          ]} rowKey="path_id" pagination={false} locale={{ emptyText: <Empty description="暂无分析路径" /> }} />
        </div>
      ),
    },
  ];

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><BookOutlined style={{ marginRight: 8 }} />知识库管理</Title></div>
      <Tabs activeKey={activeTab} onChange={setActiveTab} items={TABS} />
      <Modal title={editingDoc ? '编辑知识' : '新增知识'} open={modalVisible} onOk={handleSubmit} onCancel={() => setModalVisible(false)} width={600} destroyOnClose>
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="标题" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="category" label="分类"><Input /></Form.Item>
          <Form.Item name="content" label="内容" rules={[{ required: true }]}><TextArea rows={6} /></Form.Item>
          <Form.Item name="tags" label="标签"><Select mode="tags" placeholder="输入标签后回车" /></Form.Item>
        </Form>
      </Modal>
      <Modal title="新建分析路径" open={pathModalVisible} onCancel={() => setPathModalVisible(false)} footer={null} width={500} destroyOnClose>
        <Form layout="vertical">
          <Form.Item label="问题类型" required><Input placeholder="如: 数据延迟" /></Form.Item>
          <Form.Item label="步骤名称" required><Input placeholder="如: 日志分析" /></Form.Item>
          <Form.Item label="工具编码"><Input placeholder="如: log-analyzer" /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default KnowledgeBase;
