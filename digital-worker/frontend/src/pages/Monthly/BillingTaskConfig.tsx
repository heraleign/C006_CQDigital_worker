import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Space, Select, Modal, Form, Input,
  DatePicker, Tag, message, Popconfirm, Typography, Row, Col, Upload, Tooltip,
} from 'antd';
import {
  PlusOutlined, UploadOutlined, EditOutlined, DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { monthlyApi } from '@/services/monthly';

const { Title, Text } = Typography;
const { Option } = Select;

interface BillingTask {
  task_id: number;
  cycle_id: string;
  task_code: string;
  task_name: string;
  work_type: string;
  planned_start: string;
  planned_end: string;
  duration_minutes: number;
  dependency_codes: string | null;
  assignee: string | null;
  status: string;
  actual_start: string | null;
  actual_end: string | null;
  remark: string | null;
}

interface BillingCycle {
  cycle_id: string;
  cycle_name: string;
  status: string;
}

const WORK_TYPES = ['前置作业', '用户作业', '实收作业', '应收作业'];
const STATUS_OPTIONS = ['未开始', '进行中', '已完成', '异常'];

const STATUS_COLORS: Record<string, string> = {
  '未开始': 'default',
  '进行中': 'processing',
  '已完成': 'success',
  '异常': 'error',
};

const WORK_TYPE_COLORS: Record<string, string> = {
  '前置作业': 'blue',
  '用户作业': 'orange',
  '实收作业': 'green',
  '应收作业': 'purple',
};

const BillingTaskConfig: React.FC = () => {
  const [cycles, setCycles] = useState<BillingCycle[]>([]);
  const [selectedCycle, setSelectedCycle] = useState('202605');
  const [tasks, setTasks] = useState<BillingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<BillingTask | null>(null);
  const [form] = Form.useForm();
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [importTasks, setImportTasks] = useState<any[]>([]);
  const [importLoading, setImportLoading] = useState(false);

  const fetchCycles = useCallback(async () => {
    try {
      const res = await monthlyApi.getBillingCycles();
      const data = res?.data || res || [];
      setCycles(data);
      const active = data.find((c: BillingCycle) => c.status === 'active');
      if (active) setSelectedCycle(active.cycle_id);
    } catch {
      setCycles([
        { cycle_id: '202601', cycle_name: '2026年1月', status: 'closed' },
        { cycle_id: '202605', cycle_name: '2026年5月', status: 'active' },
      ]);
      setSelectedCycle('202605');
    }
  }, []);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const res = await monthlyApi.getBillingTasks(selectedCycle, page, pageSize);
      const d = res?.data || res || { items: [], total: 0 };
      setTasks(d.items || []);
      setTotal(d.total || 0);
    } catch {
      message.error('获取任务列表失败');
    } finally {
      setLoading(false);
    }
  }, [selectedCycle, page, pageSize]);

  useEffect(() => { fetchCycles(); }, [fetchCycles]);
  useEffect(() => { if (selectedCycle) fetchTasks(); }, [selectedCycle, fetchTasks]);

  const handleAdd = () => {
    setEditingTask(null);
    form.resetFields();
    form.setFieldsValue({ work_type: '前置作业', status: '未开始' });
    setModalOpen(true);
  };

  const handleEdit = (task: BillingTask) => {
    setEditingTask(task);
    form.setFieldsValue({
      ...task,
      planned_start: task.planned_start ? dayjs(task.planned_start) : null,
      planned_end: task.planned_end ? dayjs(task.planned_end) : null,
      dependency_codes: task.dependency_codes ? task.dependency_codes.split(',').map((s) => s.trim()) : [],
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        ...values,
        planned_start: values.planned_start?.format('YYYY-MM-DD HH:mm:ss'),
        planned_end: values.planned_end?.format('YYYY-MM-DD HH:mm:ss'),
        dependency_codes: values.dependency_codes?.join(',') || null,
      };
      if (editingTask) {
        await monthlyApi.updateBillingTask(editingTask.task_id, payload);
        message.success('更新成功');
      } else {
        await monthlyApi.createBillingTask(payload);
        message.success('创建成功');
      }
      setModalOpen(false);
      form.resetFields();
      setEditingTask(null);
      fetchTasks();
    } catch (err: any) {
      if (err?.message) message.error(err.message);
    }
  };

  const handleDelete = async (taskId: number) => {
    try {
      await monthlyApi.deleteBillingTask(taskId);
      message.success('删除成功');
      fetchTasks();
    } catch {
      message.error('删除失败');
    }
  };

  const handleImport = async () => {
    if (importTasks.length === 0) {
      message.warning('请先添加导入数据');
      return;
    }
    setImportLoading(true);
    try {
      const res = await monthlyApi.importBillingTasks(selectedCycle, importTasks);
      const data = res?.data || res || {};
      message.success(`成功导入 ${data.imported_count || importTasks.length} 条任务`);
      setImportModalOpen(false);
      setImportTasks([]);
      fetchTasks();
    } catch {
      message.error('导入失败');
    } finally {
      setImportLoading(false);
    }
  };

  const columns = [
    {
      title: '编码',
      dataIndex: 'task_code',
      key: 'task_code',
      width: 140,
      render: (v: string) => <Text code>{v}</Text>,
    },
    {
      title: '任务名称',
      dataIndex: 'task_name',
      key: 'task_name',
      width: 220,
      ellipsis: true,
    },
    {
      title: '作业类型',
      dataIndex: 'work_type',
      key: 'work_type',
      width: 100,
      render: (v: string) => <Tag color={WORK_TYPE_COLORS[v]}>{v}</Tag>,
    },
    {
      title: '计划开始',
      dataIndex: 'planned_start',
      key: 'planned_start',
      width: 150,
      render: (v: string) => v ? dayjs(v).format('MM-DD HH:mm') : '-',
    },
    {
      title: '计划结束',
      dataIndex: 'planned_end',
      key: 'planned_end',
      width: 150,
      render: (v: string) => v ? dayjs(v).format('MM-DD HH:mm') : '-',
    },
    {
      title: '耗时(分)',
      dataIndex: 'duration_minutes',
      key: 'duration_minutes',
      width: 80,
      align: 'right' as const,
    },
    {
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 80,
      render: (v: string | null) => v || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (v: string) => <Tag color={STATUS_COLORS[v]}>{v}</Tag>,
    },
    {
      title: '依赖',
      dataIndex: 'dependency_codes',
      key: 'dependency_codes',
      width: 150,
      ellipsis: true,
      render: (v: string | null) =>
        v ? v.split(',').map((d) => <Tag key={d} style={{ marginBottom: 2 }}>{d.trim()}</Tag>) : <Tag>无</Tag>,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: BillingTask) => (
        <Space>
          <Tooltip title="编辑">
            <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          </Tooltip>
          <Popconfirm title="确认删除此任务？" onConfirm={() => handleDelete(record.task_id)} okText="确认" cancelText="取消">
            <Tooltip title="删除">
              <Button type="link" size="small" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space size="middle">
              <Title level={4} style={{ margin: 0 }}>月账任务配置</Title>
              <Select value={selectedCycle} onChange={(v) => { setSelectedCycle(v); setPage(1); }} style={{ width: 160 }}>
                {cycles.map((c) => (
                  <Option key={c.cycle_id} value={c.cycle_id}>
                    {c.cycle_name} {c.status === 'active' ? '(当前)' : ''}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={fetchTasks}>刷新</Button>
              <Button icon={<PlusOutlined />} type="primary" onClick={handleAdd}>添加任务</Button>
              <Button icon={<UploadOutlined />} onClick={() => setImportModalOpen(true)}>Excel导入</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Task Table */}
      <Card>
        <Table
          dataSource={tasks}
          columns={columns}
          rowKey="task_id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            onChange: (p) => setPage(p),
            showTotal: (t) => `共 ${t} 条`,
            showSizeChanger: false,
          }}
          size="small"
          scroll={{ x: 1300 }}
        />
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingTask ? '编辑任务' : '添加任务'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); form.resetFields(); setEditingTask(null); }}
        okText="保存"
        cancelText="取消"
        width={600}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="task_code" label="任务编码" rules={[{ required: true, message: '请输入任务编码' }]}>
                <Input placeholder="如 PRE_END_001" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="work_type" label="作业类型" rules={[{ required: true, message: '请选择作业类型' }]}>
                <Select>
                  {WORK_TYPES.map((wt) => <Option key={wt} value={wt}>{wt}</Option>)}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="task_name" label="任务名称" rules={[{ required: true, message: '请输入任务名称' }]}>
            <Input placeholder="请输入任务名称" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="planned_start" label="计划开始时间" rules={[{ required: true, message: '请选择' }]}>
                <DatePicker showTime format="YYYY-MM-DD HH:mm" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="planned_end" label="计划结束时间">
                <DatePicker showTime format="YYYY-MM-DD HH:mm" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="duration_minutes" label="预计耗时(分)">
                <Input type="number" placeholder="0" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="assignee" label="负责人">
                <Input placeholder="负责人姓名" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="status" label="状态">
                <Select>
                  {STATUS_OPTIONS.map((s) => <Option key={s} value={s}>{s}</Option>)}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="dependency_codes" label="前置依赖任务">
            <Select
              mode="multiple"
              showSearch
              placeholder="搜索并选择前置任务"
              filterOption={(input, option) =>
                (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
              }
              options={tasks
                .filter((t) => !editingTask || t.task_id !== editingTask.task_id)
                .map((t) => ({
                  label: `${t.task_name}（${t.task_code}）`,
                  value: t.task_code,
                }))}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Import Modal */}
      <Modal
        title="Excel 批量导入任务"
        open={importModalOpen}
        onCancel={() => { setImportModalOpen(false); setImportTasks([]); }}
        footer={[
          <Button key="cancel" onClick={() => { setImportModalOpen(false); setImportTasks([]); }}>取消</Button>,
          <Button key="import" type="primary" loading={importLoading} onClick={handleImport}>
            确认导入 ({importTasks.length} 条)
          </Button>,
        ]}
        width={600}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Upload.Dragger
            accept=".xlsx,.xls,.csv"
            showUploadList={false}
            beforeUpload={(file) => {
              const reader = new FileReader();
              reader.onload = (e) => {
                const text = e.target?.result as string;
                // Parse CSV-like content (simple parser for demo)
                const lines = text.split('\n').filter(Boolean);
                if (lines.length < 2) {
                  message.error('文件为空或格式不正确');
                  return;
                }
                const headers = lines[0].split(',').map((h) => h.trim());
                const parsed: any[] = [];
                for (let i = 1; i < lines.length; i++) {
                  const vals = lines[i].split(',').map((v) => v.trim());
                  const row: any = {};
                  headers.forEach((h, idx) => { row[h] = vals[idx] || ''; });
                  if (row.task_code) parsed.push(row);
                }
                if (parsed.length === 0) {
                  message.error('未找到有效数据，请确保包含 task_code 列');
                  return;
                }
                setImportTasks(parsed);
                message.success(`解析到 ${parsed.length} 条任务数据`);
              };
              reader.readAsText(file);
              return false;
            }}
          >
            <p><UploadOutlined style={{ fontSize: 32, color: '#1677ff' }} /></p>
            <p>点击或拖拽文件到此区域上传</p>
            <p style={{ color: '#888', fontSize: 12 }}>支持 .xlsx, .xls, .csv 格式</p>
          </Upload.Dragger>
        </div>
        {importTasks.length > 0 && (
          <div>
            <Text strong>预览（前5条）：</Text>
            <Table
              dataSource={importTasks.slice(0, 5)}
              columns={[
                { title: '编码', dataIndex: 'task_code', width: 130 },
                { title: '任务名', dataIndex: 'task_name', ellipsis: true },
                { title: '类型', dataIndex: 'work_type', width: 90 },
              ]}
              rowKey="task_code"
              size="small"
              pagination={false}
            />
            <Text type="secondary">共 {importTasks.length} 条待导入</Text>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BillingTaskConfig;
