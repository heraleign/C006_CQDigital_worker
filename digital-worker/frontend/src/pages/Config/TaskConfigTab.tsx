import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Modal, Form, Input, InputNumber, message, Space, Popconfirm, Select, Tag, Tooltip,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { monthlyApi } from '@/services/monthly';

interface TaskItem {
  task_id: string;
  stage_id: string;
  stage_name: string;
  milestone_id: string;
  milestone_name: string;
  plan_id: string;
  plan_name: string;
  task_type: string;
  content: string;
  sort_order: number;
}

interface StageOption { stage_id: string; name: string; }
interface MilestoneOption { milestone_id: string; name: string; stage_id: string; }
interface PlanOption { plan_id: string; name: string; milestone_id: string; }

const TASK_TYPE_OPTIONS = [
  { label: 'TDP任务', value: 'TDP_TASK', color: 'blue' },
  { label: '发布消息', value: 'PUBLISH_MSG', color: 'green' },
  { label: '人工操作', value: 'MANUAL_OP', color: 'orange' },
  { label: 'SQL脚本', value: 'SQL_SCRIPT', color: 'purple' },
];

const TaskConfigTab: React.FC = () => {
  const [data, setData] = useState<TaskItem[]>([]);
  const [stages, setStages] = useState<StageOption[]>([]);
  const [milestones, setMilestones] = useState<MilestoneOption[]>([]);
  const [plans, setPlans] = useState<PlanOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<TaskItem | null>(null);
  const [filterStageId, setFilterStageId] = useState<string | undefined>(undefined);
  const [filterMilestoneId, setFilterMilestoneId] = useState<string | undefined>(undefined);
  const [filterPlanId, setFilterPlanId] = useState<string | undefined>(undefined);
  const [form] = Form.useForm();

  const fetchStages = useCallback(async () => {
    try {
      const res = await monthlyApi.getStages();
      setStages(res?.data?.items || res?.items || res?.data || res || []);
    } catch { /* ignore */ }
  }, []);

  const fetchMilestones = useCallback(async (stageId?: string) => {
    try {
      const res = await monthlyApi.getConfigMilestones({ stage_id: stageId });
      const items = res?.data?.items || res?.items || res?.data || res || [];
      setMilestones(items);
    } catch { /* ignore */ }
  }, []);

  const fetchPlans = useCallback(async (milestoneId?: string) => {
    try {
      const res = await monthlyApi.getConfigWorkPlans({ milestone_id: milestoneId });
      const items = res?.data?.items || res?.items || res?.data || res || [];
      setPlans(items.map((i: any) => ({ plan_id: i.plan_id, name: i.name, milestone_id: i.milestone_id })));
    } catch { /* ignore */ }
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await monthlyApi.getConfigTasks({
        stage_id: filterStageId,
        milestone_id: filterMilestoneId,
        plan_id: filterPlanId,
      });
      setData(res?.data?.items || res?.items || res?.data || res || []);
    } catch {
      message.error('获取任务数据失败');
    } finally {
      setLoading(false);
    }
  }, [filterStageId, filterMilestoneId, filterPlanId]);

  useEffect(() => { fetchStages(); }, [fetchStages]);
  useEffect(() => { fetchMilestones(filterStageId); }, [filterStageId, fetchMilestones]);
  useEffect(() => { fetchPlans(filterMilestoneId); }, [filterMilestoneId, fetchPlans]);
  useEffect(() => { fetchData(); }, [fetchData]);

  const handleAdd = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const handleEdit = (record: TaskItem) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleDelete = async (record: TaskItem) => {
    try {
      await monthlyApi.deleteConfigTask(record.task_id);
      message.success('删除成功');
      fetchData();
    } catch {
      message.error('删除失败');
    }
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    try {
      if (editing) {
        await monthlyApi.updateConfigTask(editing.task_id, values);
      } else {
        await monthlyApi.createConfigTask(values);
      }
      message.success(editing ? '修改成功' : '新增成功');
      setModalOpen(false);
      fetchData();
    } catch {
      message.error('保存失败');
    }
  };

  const filteredMilestones = milestones.filter((m) => !filterStageId || m.stage_id === filterStageId);
  const filteredPlans = plans.filter((p) => !filterMilestoneId || p.milestone_id === filterMilestoneId);

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', gap: 12 }}>
        <Space>
          <Select
            placeholder="筛选阶段"
            allowClear
            style={{ width: 160 }}
            value={filterStageId}
            onChange={(v) => { setFilterStageId(v); setFilterMilestoneId(undefined); setFilterPlanId(undefined); }}
            options={stages.map((s) => ({ label: s.name, value: s.stage_id }))}
          />
          <Select
            placeholder="筛选里程碑"
            allowClear
            style={{ width: 180 }}
            value={filterMilestoneId}
            onChange={(v) => { setFilterMilestoneId(v); setFilterPlanId(undefined); }}
            options={filteredMilestones.map((m) => ({ label: m.name, value: m.milestone_id }))}
          />
          <Select
            placeholder="筛选作业计划"
            allowClear
            style={{ width: 200 }}
            value={filterPlanId}
            onChange={setFilterPlanId}
            options={filteredPlans.map((p) => ({ label: p.name, value: p.plan_id }))}
          />
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增任务
        </Button>
      </div>
      <Table
        dataSource={data}
        rowKey="task_id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        columns={[
          { title: '排序', dataIndex: 'sort_order', width: 60, align: 'center' },
          {
            title: '任务类型',
            dataIndex: 'task_type',
            width: 110,
            render: (v: string) => {
              const cfg = TASK_TYPE_OPTIONS.find((t) => t.value === v);
              return <Tag color={cfg?.color || 'default'}>{cfg?.label || v}</Tag>;
            },
          },
          {
            title: '内容',
            dataIndex: 'content',
            render: (v: string) => (
              <Tooltip title={v}>
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'block', maxWidth: 400 }}>{v}</span>
              </Tooltip>
            ),
          },
          { title: '所属阶段', dataIndex: 'stage_name', width: 120 },
          { title: '所属里程碑', dataIndex: 'milestone_name', width: 160 },
          { title: '所属计划', dataIndex: 'plan_name', width: 160 },
          {
            title: '操作',
            width: 150,
            align: 'center',
            render: (_: any, record: TaskItem) => (
              <Space>
                <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
                <Popconfirm
                  title="确认删除？"
                  onConfirm={() => handleDelete(record)}
                  okText="删除"
                  okButtonProps={{ danger: true }}
                >
                  <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />
      <Modal
        title={editing ? '编辑任务' : '新增任务'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleSave}
        destroyOnClose
        width={560}
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="stage_id" label="所属阶段" rules={[{ required: true, message: '请选择阶段' }]}>
            <Select
              placeholder="请选择"
              options={stages.map((s) => ({ label: s.name, value: s.stage_id }))}
              onChange={() => { form.setFieldValue('milestone_id', undefined); form.setFieldValue('plan_id', undefined); }}
            />
          </Form.Item>
          <Form.Item name="milestone_id" label="所属里程碑" rules={[{ required: true, message: '请选择里程碑' }]}>
            <Select
              placeholder="请选择"
              options={milestones.filter((m) => m.stage_id === form.getFieldValue('stage_id')).map((m) => ({ label: m.name, value: m.milestone_id }))}
              onChange={() => form.setFieldValue('plan_id', undefined)}
            />
          </Form.Item>
          <Form.Item name="plan_id" label="所属作业计划" rules={[{ required: true, message: '请选择作业计划' }]}>
            <Select
              placeholder="请选择"
              options={plans.filter((p) => p.milestone_id === form.getFieldValue('milestone_id')).map((p) => ({ label: p.name, value: p.plan_id }))}
            />
          </Form.Item>
          <Form.Item name="task_type" label="任务类型" rules={[{ required: true, message: '请选择任务类型' }]}>
            <Select placeholder="请选择" options={TASK_TYPE_OPTIONS.map((t) => ({ label: t.label, value: t.value }))} />
          </Form.Item>
          <Form.Item name="content" label="内容" rules={[{ required: true, message: '请输入内容' }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="sort_order" label="排序" initialValue={0} rules={[{ required: true, message: '请输入排序' }]}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TaskConfigTab;
