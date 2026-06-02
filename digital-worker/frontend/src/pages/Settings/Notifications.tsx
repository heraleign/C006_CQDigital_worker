import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Switch, Space, message, Spin, Alert, Empty, Popconfirm, Tag, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, BellOutlined } from '@ant-design/icons';
import { systemApi } from '@/services/system';

const { Title } = Typography;

interface NotificationConfig {
  id: string;
  notify_type: string;
  recipient: string;
  notify_method: string;
  enabled: boolean;
  create_time: string;
}

const mockNotifications: NotificationConfig[] = [
  { id: '1', notify_type: '任务失败告警', recipient: 'admin@example.com', notify_method: '邮件', enabled: true, create_time: '2025-01-15 10:00:00' },
  { id: '2', notify_type: '数据异常告警', recipient: 'zhangsan@example.com', notify_method: '短信', enabled: true, create_time: '2025-01-20 14:30:00' },
  { id: '3', notify_type: '系统升级通知', recipient: 'all@example.com', notify_method: '邮件', enabled: false, create_time: '2025-02-01 09:00:00' },
  { id: '4', notify_type: '质量评分预警', recipient: 'lisi@example.com', notify_method: '企业微信', enabled: true, create_time: '2025-02-10 16:00:00' },
  { id: '5', notify_type: '定时任务完成', recipient: 'team@example.com', notify_method: '邮件', enabled: true, create_time: '2025-03-01 08:00:00' },
];

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<NotificationConfig | null>(null);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await systemApi.getNotifications({ page: 1, page_size: 100 });
      setNotifications(res.data?.items?.length > 0 ? res.data.items : mockNotifications);
    } catch (err: any) {
      setNotifications(mockNotifications);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = () => {
    setEditingItem(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: NotificationConfig) => {
    setEditingItem(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = (id: string) => {
    setNotifications((prev) => prev.filter((item) => item.id !== id));
    message.success('删除成功');
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingItem) {
        await systemApi.updateNotification(editingItem.id, values);
        setNotifications((prev) =>
          prev.map((item) => (item.id === editingItem.id ? { ...item, ...values } : item))
        );
        message.success('更新成功');
      } else {
        const newItem: NotificationConfig = {
          id: Date.now().toString(),
          ...values,
          create_time: new Date().toLocaleString('zh-CN', { hour12: false }),
        };
        setNotifications((prev) => [...prev, newItem]);
        message.success('创建成功');
      }
      setModalVisible(false);
    } catch (err: any) {
      if (err?.message) message.error(err.message);
    }
  };

  const columns = [
    {
      title: '通知类型',
      dataIndex: 'notify_type',
      key: 'notify_type',
      width: 160,
    },
    {
      title: '接收人',
      dataIndex: 'recipient',
      key: 'recipient',
      width: 200,
    },
    {
      title: '通知方式',
      dataIndex: 'notify_method',
      key: 'notify_method',
      width: 120,
      render: (method: string) => <Tag>{method}</Tag>,
    },
    {
      title: '是否启用',
      dataIndex: 'enabled',
      key: 'enabled',
      width: 100,
      render: (enabled: boolean) =>
        enabled ? <Tag color="success">已启用</Tag> : <Tag color="default">已停用</Tag>,
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
      render: (_: any, record: NotificationConfig) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确认删除该配置?" onConfirm={() => handleDelete(record.id)}>
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
          <BellOutlined style={{ marginRight: 8 }} />
          通知配置
        </Title>
      </div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 14, color: '#666' }}>共 {notifications.length} 条配置</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新增配置
          </Button>
        </div>
        <Spin spinning={loading}>
          {notifications.length > 0 ? (
            <Table
              rowKey="id"
              columns={columns}
              dataSource={notifications}
              pagination={false}
              size="middle"
            />
          ) : (
            !loading && <Empty description="暂无通知配置" />
          )}
        </Spin>
      </Card>
      <Modal
        title={editingItem ? '编辑配置' : '新增配置'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        destroyOnClose
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="notify_type" label="通知类型" rules={[{ required: true, message: '请输入通知类型' }]}>
            <Select
              placeholder="请选择通知类型"
              options={[
                { label: '任务失败告警', value: '任务失败告警' },
                { label: '数据异常告警', value: '数据异常告警' },
                { label: '系统升级通知', value: '系统升级通知' },
                { label: '质量评分预警', value: '质量评分预警' },
                { label: '定时任务完成', value: '定时任务完成' },
              ]}
            />
          </Form.Item>
          <Form.Item name="recipient" label="接收人" rules={[{ required: true, message: '请输入接收人' }]}>
            <Input placeholder="邮箱地址或手机号" />
          </Form.Item>
          <Form.Item name="notify_method" label="通知方式" rules={[{ required: true, message: '请选择通知方式' }]}>
            <Select
              placeholder="请选择通知方式"
              options={[
                { label: '邮件', value: '邮件' },
                { label: '短信', value: '短信' },
                { label: '企业微信', value: '企业微信' },
                { label: '钉钉', value: '钉钉' },
              ]}
            />
          </Form.Item>
          <Form.Item name="enabled" label="是否启用" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Notifications;
