import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Space, message, Spin, Alert, Empty, Popconfirm, Tag, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, BookOutlined } from '@ant-design/icons';
import { rootCauseApi } from '@/services/rootCause';
import type { KnowledgeDoc } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const SettingsKnowledgeBase: React.FC = () => {
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDoc, setEditingDoc] = useState<KnowledgeDoc | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await rootCauseApi.getKnowledge({ page: 1, page_size: 100 });
      setDocs(res.data?.items || []);
    } catch (err: any) {
      setError(err?.message || '加载知识库失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = () => {
    setEditingDoc(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: KnowledgeDoc) => {
    setEditingDoc(record);
    form.setFieldsValue({ ...record, tags: record.tags?.join(', ') });
    setModalVisible(true);
  };

  const handleDelete = async (doc_id: string) => {
    try {
      await rootCauseApi.deleteKnowledge(doc_id);
      message.success('删除成功');
      fetchData();
    } catch (err: any) {
      message.error(err?.message || '删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const submitData = {
        ...values,
        tags: typeof values.tags === 'string'
          ? values.tags.split(',').map((t: string) => t.trim()).filter(Boolean)
          : values.tags,
      };
      setSubmitting(true);
      if (editingDoc) {
        await rootCauseApi.updateKnowledge(editingDoc.doc_id, submitData);
        message.success('更新成功');
      } else {
        await rootCauseApi.createKnowledge(submitData);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchData();
    } catch (err: any) {
      if (err?.message) message.error(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      title: '文档标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (cat: string) => <Tag color="blue">{cat}</Tag>,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: string[]) => (
        <Space size={4} wrap>
          {tags?.map((tag) => (
            <Tag key={tag} style={{ fontSize: 12 }}>{tag}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 170,
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      render: (_: any, record: KnowledgeDoc) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确认删除该文档?" onConfirm={() => handleDelete(record.doc_id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (error) {
    return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;
  }

  return (
    <div>
      <div className="page-header" style={{ marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          <BookOutlined style={{ marginRight: 8 }} />
          知识库
        </Title>
      </div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 14, color: '#666' }}>共 {docs.length} 篇文档</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新增文档
          </Button>
        </div>
        <Spin spinning={loading}>
          {docs.length > 0 ? (
            <Table
              rowKey="doc_id"
              columns={columns}
              dataSource={docs}
              pagination={false}
              size="middle"
            />
          ) : (
            !loading && <Empty description="暂无知识库文档" />
          )}
        </Spin>
      </Card>
      <Modal
        title={editingDoc ? '编辑文档' : '新增文档'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        destroyOnClose
        width={700}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="文档标题" rules={[{ required: true, message: '请输入文档标题' }]}>
            <Input placeholder="请输入文档标题" />
          </Form.Item>
          <Form.Item name="category" label="分类" rules={[{ required: true, message: '请选择分类' }]}>
            <Select
              placeholder="请选择分类"
              options={[
                { label: '运维规范', value: '运维规范' },
                { label: '故障处理', value: '故障处理' },
                { label: '配置指南', value: '配置指南' },
                { label: '最佳实践', value: '最佳实践' },
                { label: '常见问题', value: '常见问题' },
              ]}
            />
          </Form.Item>
          <Form.Item name="content" label="内容" rules={[{ required: true, message: '请输入文档内容' }]}>
            <TextArea rows={6} placeholder="请输入文档内容" />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Input placeholder="多个标签用逗号分隔" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SettingsKnowledgeBase;
