import React, { useState, useEffect, useMemo } from 'react';
import { Collapse, Table, Card, Button, Modal, Form, Input, Select, Switch, Space, message, Spin, Alert, Empty, Popconfirm, Typography, Tag, Badge, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ToolOutlined, ApiOutlined, SearchOutlined, CloudUploadOutlined } from '@ant-design/icons';
import StatusTag from '@/components/StatusTag';
import { systemApi } from '@/services/system';
import { hermesApi } from '@/services/hermes';
import type { ToolItem } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const categoryColors: Record<string, string> = {
  '数据质量稽核': 'blue',
  '根因分析': 'purple',
  '月账数字员工': 'green',
  '外部系统集成': 'orange',
};

const categoryOrder = ['数据质量稽核', '根因分析', '月账数字员工', '外部系统集成'];

const Tools: React.FC = () => {
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTool, setEditingTool] = useState<ToolItem | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  // ── Collapse state ──────────────────────────────────────────────
  const [expandedCategories, setExpandedCategories] = useState<string[]>(categoryOrder);

  // ── Filter state ─────────────────────────────────────────────────
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [filterKeyword, setFilterKeyword] = useState<string>('');
  const [filterPriority, setFilterPriority] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');

  const handleRegisterToggle = async (skillCode: string, currentlyRegistered: boolean) => {
    const hide = message.loading(currentlyRegistered ? `正在从 Hermes 注销 ${skillCode}...` : `正在注册 ${skillCode} 到 Hermes...`, 0);
    try {
      if (currentlyRegistered) {
        await hermesApi.unregisterSkill({ skill_code: skillCode });
        message.success(`已取消注册 ${skillCode}`);
      } else {
        const res = await hermesApi.registerSkill({ skill_code: skillCode });
        if (res.data?.success) {
          message.success(`✅ ${skillCode} 已注册到 Hermes`);
        } else {
          message.warning(`注册返回: ${res.data?.error || '未知'}`);
        }
      }
      fetchData();
    } catch (err: any) {
      message.error(`操作失败: ${err?.message || '连接错误'}`);
    } finally {
      hide();
    }
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await systemApi.getTools({ page: 1, page_size: 100 });
      setTools(res.data?.items || []);
    } catch (err: any) {
      setError(err?.message || '加载技能列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // ── Filtered & grouped data ──────────────────────────────────────
  const filteredTools = useMemo(() => {
    let result = [...tools];
    if (filterCategory) result = result.filter((t) => t.category === filterCategory);
    if (filterKeyword) {
      const kw = filterKeyword.toLowerCase();
      result = result.filter((t) =>
        t.tool_code.toLowerCase().includes(kw) ||
        t.tool_name.toLowerCase().includes(kw)
      );
    }
    if (filterPriority) result = result.filter((t) => t.priority === filterPriority);
    if (filterStatus) result = result.filter((t) => t.status === filterStatus);
    return result;
  }, [tools, filterCategory, filterKeyword, filterPriority, filterStatus]);

  const groupedTools = useMemo(() => {
    const groups: Record<string, ToolItem[]> = {};
    categoryOrder.forEach((cat) => { groups[cat] = []; });
    filteredTools.forEach((t) => {
      const cat = t.category || '其他';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(t);
    });
    return groups;
  }, [filteredTools]);

  // ── Filters summary ──────────────────────────────────────────────
  const hasActiveFilters = filterCategory || filterKeyword || filterPriority || filterStatus;

  const clearFilters = () => {
    setFilterCategory('');
    setFilterKeyword('');
    setFilterPriority('');
    setFilterStatus('');
  };

  // ── Modal handlers ───────────────────────────────────────────────
  const handleCreate = () => {
    setEditingTool(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: ToolItem) => {
    setEditingTool(record);
    form.setFieldsValue({
      ...record,
      // BUG FIX: Switch expects boolean, backend stores "active"/"inactive"
      status: record.status === 'active',
    });
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

      // BUG FIX: Convert Switch boolean back to string for the API
      const payload = {
        ...values,
        status: values.status ? 'active' : 'inactive',
      };

      if (editingTool) {
        await systemApi.updateTool(editingTool.tool_id, payload);
        message.success('更新成功');
      } else {
        await systemApi.createTool(payload);
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

  // ── Columns for the inner table ──────────────────────────────────
  const columns = [
    {
      title: '技能编码',
      dataIndex: 'tool_code',
      key: 'tool_code',
      width: 160,
      render: (v: string) => <Tag icon={<ApiOutlined />} style={{ fontFamily: 'monospace' }}>{v}</Tag>,
    },
    {
      title: '技能名称',
      dataIndex: 'tool_name',
      key: 'tool_name',
      width: 160,
    },
    {
      title: '方法',
      dataIndex: 'method',
      key: 'method',
      width: 70,
      render: (v: string) => {
        if (!v) return null;
        const color = v === 'POST' ? 'green' : v === 'GET' ? 'blue' : v === 'PUT' ? 'orange' : 'default';
        return <Tag color={color}>{v}</Tag>;
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 70,
      render: (v: string) => v ? <Tag color={v === 'P0' ? 'red' : v === 'P1' ? 'gold' : 'default'}>{v}</Tag> : null,
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
      width: 90,
      render: (v: string) => <StatusTag status={v} />,
    },
    {
      title: '操作',
      key: 'action',
      width: 320,
      render: (_: any, record: ToolItem) => (
        <Space size="small" style={{ whiteSpace: 'nowrap' }}>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CloudUploadOutlined />}
            style={{ color: record.hermes_registered ? '#cf1322' : '#722ed1' }}
            onClick={() => handleRegisterToggle(record.tool_code, !!record.hermes_registered)}
          >
            {record.hermes_registered ? '取消注册' : 'Hermes注册'}
          </Button>
          <Popconfirm title="确认删除该技能?" onConfirm={() => handleDelete(record.tool_id)}>
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

  const activeFilterCount = [filterCategory, filterPriority, filterStatus].filter(Boolean).length + (filterKeyword ? 1 : 0);

  return (
    <div>
      <div className="page-header" style={{ marginBottom: 16 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              <ToolOutlined style={{ marginRight: 8 }} />
              技能管理
              <Tag style={{ marginLeft: 12 }}>{tools.length} 个技能</Tag>
            </Title>
          </Col>
          <Col>
            <Space>
              {hasActiveFilters && (
                <Button size="small" onClick={clearFilters}>
                  清除筛选 ({activeFilterCount})
                </Button>
              )}
              <Button
                icon={<ApiOutlined />}
                style={{ borderColor: '#722ed1', color: '#722ed1' }}
                onClick={async () => {
                  try {
                    const res = await hermesApi.getProjectDefinition();
                    const data = res.data || {};
                    message.success(`项目定义已获取: ${data.project_name || 'CQ数据运维数字员工'}，共 ${data.total_skills || 0} 个技能`);
                  } catch (err: any) {
                    message.error(err?.message || '获取失败');
                  }
                }}
              >
                Hermes项目
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                添加技能
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* ── Filter bar ────────────────────────────────────────────── */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]} align="middle">
          <Col xs={24} sm={12} md={6}>
            <Input.Search
              placeholder="搜索编码或名称..."
              allowClear
              value={filterKeyword}
              onChange={(e) => setFilterKeyword(e.target.value)}
              prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
            />
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              placeholder="分类"
              allowClear
              style={{ width: '100%' }}
              value={filterCategory || undefined}
              onChange={(v) => setFilterCategory(v || '')}
              options={categoryOrder.map((c) => ({ label: c, value: c }))}
            />
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              placeholder="优先级"
              allowClear
              style={{ width: '100%' }}
              value={filterPriority || undefined}
              onChange={(v) => setFilterPriority(v || '')}
              options={[
                { label: <Tag color="red">P0</Tag>, value: 'P0' },
                { label: <Tag color="gold">P1</Tag>, value: 'P1' },
                { label: <Tag color="default">P2</Tag>, value: 'P2' },
              ]}
            />
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              placeholder="状态"
              allowClear
              style={{ width: '100%' }}
              value={filterStatus || undefined}
              onChange={(v) => setFilterStatus(v || '')}
              options={[
                { label: <span><Badge status="success" /> 启用</span>, value: 'active' },
                { label: <span><Badge status="error" /> 停用</span>, value: 'inactive' },
              ]}
            />
          </Col>
        </Row>
      </Card>

      {/* ── Collapsible category panels ───────────────────────────── */}
      <Spin spinning={loading}>
        {filteredTools.length > 0 ? (
          <Collapse
            ghost
            expandIconPosition="end"
            activeKey={expandedCategories}
            onChange={(keys) => setExpandedCategories(keys as string[])}
            items={categoryOrder
              .filter((cat) => (groupedTools[cat]?.length || 0) > 0)
              .map((cat) => ({
                key: cat,
                label: (
                  <Space>
                    <Badge color={categoryColors[cat] || 'default'} />
                    <span style={{ fontWeight: 600, fontSize: 15 }}>{cat}</span>
                    <Tag>{groupedTools[cat]?.length || 0} 个技能</Tag>
                  </Space>
                ),
                children: (
                  <Table
                    rowKey="tool_id"
                    columns={columns}
                    dataSource={groupedTools[cat]}
                    pagination={false}
                    size="small"
                    style={{ background: '#fff' }}
                  />
                ),
              }))}
          />
        ) : (
          !loading && (
            <Card>
              <Empty
                description={
                  hasActiveFilters
                    ? <span>没有匹配的技能 <a onClick={clearFilters}>清除筛选条件</a></span>
                    : '暂无技能数据'
                }
              />
            </Card>
          )
        )}
      </Spin>

      {/* ── Create/Edit modal ─────────────────────────────────────── */}
      <Modal
        title={editingTool ? '编辑技能' : '注册技能'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        destroyOnClose
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="tool_name" label="技能名称" rules={[{ required: true, message: '请输入技能名称' }]}>
            <Input placeholder="请输入技能名称" />
          </Form.Item>
          <Form.Item name="tool_code" label="技能编码" rules={[{ required: true, message: '请输入技能编码' }]}>
            <Input placeholder="请输入技能编码，如 dq/field/list" />
          </Form.Item>
          <Form.Item name="category" label="分类" rules={[{ required: true, message: '请选择分类' }]}>
            <Select
              placeholder="选择技能分类"
              options={categoryOrder.map((c) => ({ label: c, value: c }))}
            />
          </Form.Item>
          <Form.Item name="method" label="请求方法">
            <Select
              placeholder="选择HTTP方法"
              options={[
                { label: 'GET', value: 'GET' },
                { label: 'POST', value: 'POST' },
                { label: 'PUT', value: 'PUT' },
                { label: 'DELETE', value: 'DELETE' },
              ]}
            />
          </Form.Item>
          <Form.Item name="priority" label="优先级">
            <Select
              placeholder="选择优先级"
              options={[
                { label: 'P0 — 核心', value: 'P0' },
                { label: 'P1 — 重要', value: 'P1' },
                { label: 'P2 — 一般', value: 'P2' },
              ]}
            />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="请输入技能描述" />
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