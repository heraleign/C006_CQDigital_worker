import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Switch, Space, message, Spin, Alert, Empty, Popconfirm, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ToolOutlined } from '@ant-design/icons';
import StatusTag from '@/components/StatusTag';
import { systemApi } from '@/services/system';
import type { ToolItem } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const Tools: React.FC = () => {
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTool, setEditingTool] = useState<ToolItem | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await systemApi.getTools({ page: 1, page_size: 100 });
      setTools(res.data?.items || []);
    } catch (err: any) {
      setError(err?.message || '加载工具列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = () => {
    setEditingTool(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: ToolItem) => {
    setEditingTool(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (tool_id: string) => {
    try {
      await systemApi.deleteTool(tool_id);
      message.success('删除成功');
      fetchData();
    } catch (err: any) {
      message.error(err?.message || '删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      if (editingTool) {
        await systemApi.updateTool(editingTool.tool_id, values);
        message.success('更新成功');
      } else {
        await systemApi.createTool(values);
        message.success('注册成功');
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
      title: '工具编码',
      dataIndex: 'tool_code',
      key: 'tool_code',
      width: 140,
    },
    {
      title: '工具名称',
      dataIndex: 'tool_name',
      key: 'tool_name',
      width: 160,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
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
      render: (_: any, record: ToolItem) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确认删除该工具?" onConfirm={() => handleDelete(record.tool_id)}>
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
          <ToolOutlined style={{ marginRight: 8 }} />
          工具注册
        </Title>
      </div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 14, color: '#666' }}>共 {tools.length} 个工具</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            注册工具
          </Button>
        </div>
        <Spin spinning={loading}>
          {tools.length > 0 ? (
            <Table
              rowKey="tool_id"
              columns={columns}
              dataSource={tools}
              pagination={false}
              size="middle"
            />
          ) : (
            !loading && <Empty description="暂无工具数据" />
          )}
        </Spin>
      </Card>
      <Modal
        title={editingTool ? '编辑工具' : '注册工具'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        destroyOnClose
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="tool_name" label="工具名称" rules={[{ required: true, message: '请输入工具名称' }]}>
            <Input placeholder="请输入工具名称" />
          </Form.Item>
          <Form.Item name="tool_code" label="工具编码" rules={[{ required: true, message: '请输入工具编码' }]}>
            <Input placeholder="请输入工具编码，如 analyze_tool" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="请输入工具描述" />
          </Form.Item>
          <Form.Item name="status" label="状态" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Tools;
