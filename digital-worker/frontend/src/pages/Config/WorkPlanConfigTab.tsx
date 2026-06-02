import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Modal, Form, Input, InputNumber, message, Space, Popconfirm,
  Select, Radio, Switch, Tag, Row, Col, Card,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { monthlyApi } from '@/services/monthly';

interface WorkPlan {
  plan_id: string;
  stage_id: string;
  stage_name: string;
  milestone_id: string;
  milestone_name: string;
  seq_no: number;
  name: string;
  time_point: string;
  task_mode: string;
  is_system_task: boolean;
  exec_template: string;
}

interface StageOption { stage_id: string; name: string; }
interface MilestoneOption { milestone_id: string; name: string; stage_id: string; }
interface ParsedTaskPreview {
  sort_order: number;
  task_type: string;
  content: string;
}

const WorkPlanConfigTab: React.FC = () => {
  const [data, setData] = useState<WorkPlan[]>([]);
  const [stages, setStages] = useState<StageOption[]>([]);
  const [milestones, setMilestones] = useState<MilestoneOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<WorkPlan | null>(null);
  const [filterStageId, setFilterStageId] = useState<string | undefined>(undefined);
  const [filterMilestoneId, setFilterMilestoneId] = useState<string | undefined>(undefined);
  const [parsedTasks, setParsedTasks] = useState<ParsedTaskPreview[]>([]);
  const [parsing, setParsing] = useState(false);
  const [form] = Form.useForm();

  const fetchStages = useCallback(async () => {
    try {
      const res = await monthlyApi.getStages();
      setStages(res?.data?.items || res?.items || res?.data || res || []);
    } catch { /* ignore */ }
  }, []);

  const fetchMilestones = useCallback(async (stageId?: string) => {
    try {
      const res = await monthlyApi.getMilestones({ stage_id: stageId });
      const items = res?.data?.items || res?.items || res?.data || res || [];
      setMilestones(items);
    } catch { /* ignore */ }
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await monthlyApi.getWorkPlans({
        stage_id: filterStageId,
        milestone_id: filterMilestoneId,
      });
      setData(res?.data?.items || res?.items || res?.data || res || []);
    } catch {
      message.error('获取作业计划数据失败');
    } finally {
      setLoading(false);
    }
  }, [filterStageId, filterMilestoneId]);

  useEffect(() => { fetchStages(); }, [fetchStages]);
  useEffect(() => { fetchMilestones(filterStageId); }, [filterStageId, fetchMilestones]);
  useEffect(() => { fetchData(); }, [fetchData]);

  const handleAdd = () => {
    setEditing(null);
    form.resetFields();
    setParsedTasks([]);
    setModalOpen(true);
  };

  const handleEdit = (record: WorkPlan) => {
    setEditing(record);
    form.setFieldsValue(record);
    setParsedTasks([]);
    setModalOpen(true);
  };

  const handleDelete = async (record: WorkPlan) => {
    try {
      await monthlyApi.deleteWorkPlan(record.plan_id);
      message.success('删除成功');
      fetchData();
    } catch {
      message.error('删除失败');
    }
  };

  const handleParseTemplate = async () => {
    const template = form.getFieldValue('exec_template');
    if (!template) {
      message.warning('请先输入执行模板');
      return;
    }
    setParsing(true);
    try {
      const res = await monthlyApi.parseTemplate({ template });
      const tasks = res?.data?.tasks || res?.tasks || [];
      setParsedTasks(tasks);
      message.success(`解析成功，共 ${tasks.length} 个任务`);
    } catch {
      message.error('解析失败');
    } finally {
      setParsing(false);
    }
  };

  const handleSave = async (autoGenerate = false) => {
    const values = await form.validateFields();
    try {
      if (editing) {
        await monthlyApi.updateWorkPlan(editing.plan_id, { ...values, auto_generate: autoGenerate });
      } else {
        await monthlyApi.createWorkPlan({ ...values, auto_generate: autoGenerate });
      }
      message.success(editing ? '修改成功' : '新增成功');
      setModalOpen(false);
      fetchData();
    } catch {
      message.error('保存失败');
    }
  };

  const filteredMilestones = milestones.filter(
    (m) => !filterStageId || m.stage_id === filterStageId
  );

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', gap: 12 }}>
        <Space>
          <Select
            placeholder="筛选阶段"
            allowClear
            style={{ width: 180 }}
            value={filterStageId}
            onChange={(v) => { setFilterStageId(v); setFilterMilestoneId(undefined); }}
            options={stages.map((s) => ({ label: s.name, value: s.stage_id }))}
          />
          <Select
            placeholder="筛选里程碑"
            allowClear
            style={{ width: 200 }}
            value={filterMilestoneId}
            onChange={setFilterMilestoneId}
            options={filteredMilestones.map((m) => ({ label: m.name, value: m.milestone_id }))}
          />
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增作业计划
        </Button>
      </div>
      <Table
        dataSource={data}
        rowKey="plan_id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        columns={[
          { title: '序号', dataIndex: 'seq_no', width: 60, align: 'center' },
          { title: '计划名称', dataIndex: 'name' },
          { title: '时间点', dataIndex: 'time_point', width: 110, render: (v: string) => v || '-' },
          {
            title: '任务方式',
            dataIndex: 'task_mode',
            width: 100,
            render: (v: string) => <Tag color={v === '数字员工' ? 'blue' : 'orange'}>{v}</Tag>,
          },
          {
            title: '系统任务',
            dataIndex: 'is_system_task',
            width: 90,
            align: 'center',
            render: (v: boolean) => <Switch checked={v} disabled size="small" />,
          },
          { title: '所属阶段', dataIndex: 'stage_name', width: 120 },
          { title: '所属里程碑', dataIndex: 'milestone_name', width: 160 },
          {
            title: '操作',
            width: 180,
            align: 'center',
            render: (_: any, record: WorkPlan) => (
              <Space>
                <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
                <Popconfirm
                  title="确认删除？"
                  description="该作业计划下的所有任务将被级联删除。"
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
        title={editing ? '编辑作业计划' : '新增作业计划'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
        destroyOnClose
        width={680}
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="stage_id" label="所属阶段" rules={[{ required: true, message: '请选择阶段' }]}>
                <Select
                  placeholder="请选择"
                  options={stages.map((s) => ({ label: s.name, value: s.stage_id }))}
                  onChange={() => form.setFieldValue('milestone_id', undefined)}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="milestone_id" label="所属里程碑" rules={[{ required: true, message: '请选择里程碑' }]}>
                <Select
                  placeholder="请选择"
                  options={milestones
                    .filter((m) => m.stage_id === form.getFieldValue('stage_id'))
                    .map((m) => ({ label: m.name, value: m.milestone_id }))}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="seq_no" label="序号" initialValue={1} rules={[{ required: true }]}>
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={16}>
              <Form.Item name="name" label="计划名称" rules={[{ required: true, message: '请输入名称' }, { max: 200 }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="time_point" label="时间点">
            <Input placeholder="如：1日10:00" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="task_mode" label="任务方式" initialValue="人工">
                <Radio.Group>
                  <Radio value="人工">人工</Radio>
                  <Radio value="数字员工">数字员工</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_system_task" label="是否系统任务" valuePropName="checked" initialValue={false}>
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="exec_template" label="执行模板">
            <Input.TextArea rows={5} placeholder="输入模板文本，点击下方按钮解析任务..." />
          </Form.Item>
          <Button icon={<ThunderboltOutlined />} loading={parsing} onClick={handleParseTemplate} style={{ marginBottom: 12 }}>
            解析任务预览
          </Button>
          {parsedTasks.length > 0 && (
            <Card size="small" title="解析结果预览" style={{ marginBottom: 16 }}>
              <Table
                dataSource={parsedTasks}
                rowKey="sort_order"
                size="small"
                pagination={false}
                columns={[
                  { title: '排序', dataIndex: 'sort_order', width: 60 },
                  {
                    title: '任务类型',
                    dataIndex: 'task_type',
                    width: 110,
                    render: (v: string) => {
                      const colors: Record<string, string> = { TDP_TASK: 'blue', PUBLISH_MSG: 'green', MANUAL_OP: 'orange', SQL_SCRIPT: 'purple' };
                      return <Tag color={colors[v] || 'default'}>{v}</Tag>;
                    },
                  },
                  { title: '内容', dataIndex: 'content', ellipsis: true },
                ]}
              />
            </Card>
          )}
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button onClick={() => setModalOpen(false)}>取消</Button>
            <Button onClick={() => handleSave(false)}>仅保存计划</Button>
            <Button type="primary" onClick={() => handleSave(true)}>
              保存并自动生成任务
            </Button>
          </Space>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkPlanConfigTab;
