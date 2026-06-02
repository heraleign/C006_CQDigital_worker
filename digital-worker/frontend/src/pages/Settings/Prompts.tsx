import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Switch, Space, message, Spin, Alert, Empty, Popconfirm, Tag, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CodeOutlined } from '@ant-design/icons';
import StatusTag from '@/components/StatusTag';
import { systemApi } from '@/services/system';
import type { PromptTemplate } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const Prompts: React.FC = () => {
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<PromptTemplate | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await systemApi.getPrompts({ page: 1, page_size: 100 });
      setPrompts(res.data?.items || []);
    } catch (err: any) {
      setError(err?.message || '加载模板列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = () => {
    setEditingPrompt(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: PromptTemplate) => {
    setEditingPrompt(record);
    form.setFieldsValue({ ...record, status: record.status === 'active' });
    setModalVisible(true);
  };

  const handleDelete = async (prompt_id: string) => {
    try {
      await systemApi.deletePrompt(prompt_id);
      message.success('删除成功');
      fetchData();
    } catch (err: any) {
      message.error(err?.message || '删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const submitData = { ...values, status: values.status ? 'active' : 'inactive' };
      setSubmitting(true);
      if (editingPrompt) {
        await systemApi.updatePrompt(editingPrompt.prompt_id, submitData);
        message.success('更新成功');
      } else {
        await systemApi.createPrompt(submitData);
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
      title: '模板名称',
      dataIndex: 'prompt_name',
      key: 'prompt_name',
      width: 160,
    },
    {
      title: '模板类型',
      dataIndex: 'prompt_type',
      key: 'prompt_type',
      width: 120,
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (text: string) => text?.substring(0, 80) + (text?.length > 80 ? '...' : ''),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => <StatusTag status={status} />,
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      render: (_: any, record: PromptTemplate) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确认删除该模板?" onConfirm={() => handleDelete(record.prompt_id)}>
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
          <CodeOutlined style={{ marginRight: 8 }} />
          Prompt管理
        </Title>
      </div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 14, color: '#666' }}>共 {prompts.length} 个模板</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建模板
          </Button>
        </div>
        <Spin spinning={loading}>
          {prompts.length > 0 ? (
            <Table
              rowKey="prompt_id"
              columns={columns}
              dataSource={prompts}
              pagination={false}
              size="middle"
            />
          ) : (
            !loading && <Empty description="暂无模板数据" />
          )}
        </Spin>
      </Card>
      <Modal
        title={editingPrompt ? '编辑模板' : '新建模板'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        destroyOnClose
        width={700}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="prompt_name" label="模板名称" rules={[{ required: true, message: '请输入模板名称' }]}>
            <Input placeholder="请输入模板名称" />
          </Form.Item>
          <Form.Item name="prompt_type" label="模板类型" rules={[{ required: true, message: '请选择模板类型' }]}>
            <Select
              placeholder="请选择模板类型"
              options={[
                { label: '分析提示词', value: 'analysis' },
                { label: '诊断提示词', value: 'diagnosis' },
                { label: '报告提示词', value: 'report' },
                { label: '建议提示词', value: 'suggestion' },
              ]}
            />
          </Form.Item>
          <Form.Item name="content" label="模板内容" rules={[{ required: true, message: '请输入模板内容' }]}>
            <TextArea rows={6} placeholder="请输入Prompt模板内容" />
          </Form.Item>
          <Form.Item name="status" label="状态" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Prompts;
