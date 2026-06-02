import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Switch, Space, message, Spin, Alert, Empty, Popconfirm, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, KeyOutlined, TeamOutlined } from '@ant-design/icons';
import StatusTag from '@/components/StatusTag';
import { systemApi } from '@/services/system';
import type { SysUser } from '@/types';

const { Title } = Typography;

const UserManage: React.FC = () => {
  const [users, setUsers] = useState<SysUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<SysUser | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await systemApi.getUsers({ page: 1, page_size: 100 });
      setUsers(res.data?.items || []);
    } catch (err: any) {
      setError(err?.message || '加载用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: SysUser) => {
    setEditingUser(record);
    form.setFieldsValue({ ...record, status: record.status === 'active' });
    setModalVisible(true);
  };

  const handleDelete = async (user_id: string) => {
    try {
      await systemApi.deleteUser(user_id);
      message.success('删除成功');
      fetchData();
    } catch (err: any) {
      message.error(err?.message || '删除失败');
    }
  };

  const handleResetPassword = (record: SysUser) => {
    Modal.confirm({
      title: '重置密码',
      content: `确认重置用户 "${record.username}" 的密码？重置后密码将发送至其注册邮箱。`,
      onOk: async () => {
        try {
          await systemApi.updateUser(record.user_id, { reset_password: true });
          message.success('密码已重置');
        } catch (err: any) {
          message.error(err?.message || '重置失败');
        }
      },
    });
  };

  const handleToggleStatus = async (record: SysUser) => {
    const newStatus = record.status === 'active' ? 'inactive' : 'active';
    try {
      await systemApi.updateUser(record.user_id, { status: newStatus });
      message.success(newStatus === 'active' ? '用户已启用' : '用户已禁用');
      fetchData();
    } catch (err: any) {
      message.error(err?.message || '操作失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const submitData = { ...values, status: values.status ? 'active' : 'inactive' };
      setSubmitting(true);
      if (editingUser) {
        await systemApi.updateUser(editingUser.user_id, submitData);
        message.success('更新成功');
      } else {
        await systemApi.createUser(submitData);
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
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120,
    },
    {
      title: '姓名',
      dataIndex: 'real_name',
      key: 'real_name',
      width: 120,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => <StatusTag status={status} />,
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
      width: 260,
      render: (_: any, record: SysUser) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" icon={<KeyOutlined />} onClick={() => handleResetPassword(record)}>
            重置密码
          </Button>
          <Popconfirm
            title={`确认${record.status === 'active' ? '禁用' : '启用'}该用户?`}
            onConfirm={() => handleToggleStatus(record)}
          >
            <Button type="link" size="small" danger={record.status === 'active'}>
              {record.status === 'active' ? '禁用' : '启用'}
            </Button>
          </Popconfirm>
          <Popconfirm title="确认删除该用户?" onConfirm={() => handleDelete(record.user_id)}>
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
          <TeamOutlined style={{ marginRight: 8 }} />
          用户管理
        </Title>
      </div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 14, color: '#666' }}>共 {users.length} 个用户</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新增用户
          </Button>
        </div>
        <Spin spinning={loading}>
          {users.length > 0 ? (
            <Table
              rowKey="user_id"
              columns={columns}
              dataSource={users}
              pagination={false}
              size="middle"
            />
          ) : (
            !loading && <Empty description="暂无用户数据" />
          )}
        </Spin>
      </Card>
      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        destroyOnClose
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item name="real_name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input placeholder="请输入真实姓名" />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email', message: '请输入有效邮箱' }]}>
            <Input placeholder="请输入邮箱地址" />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select
              placeholder="请选择角色"
              options={[
                { label: '管理员', value: 'admin' },
                { label: '运维人员', value: 'operator' },
                { label: '审计人员', value: 'auditor' },
                { label: '普通用户', value: 'user' },
              ]}
            />
          </Form.Item>
          <Form.Item name="status" label="状态" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManage;
