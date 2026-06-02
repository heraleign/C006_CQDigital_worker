import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, message, Space, Popconfirm, Select } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { monthlyApi } from '@/services/monthly';

interface Milestone {
  milestone_id: string;
  stage_id: string;
  stage_name: string;
  name: string;
  sort_order: number;
}

interface StageOption {
  stage_id: string;
  name: string;
}

const MilestoneConfigTab: React.FC = () => {
  const [data, setData] = useState<Milestone[]>([]);
  const [stages, setStages] = useState<StageOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Milestone | null>(null);
  const [filterStageId, setFilterStageId] = useState<string | undefined>(undefined);
  const [form] = Form.useForm();

  const fetchStages = useCallback(async () => {
    try {
      const res = await monthlyApi.getStages();
      const items = res?.data?.items || res?.data || [];
      setStages(items);
    } catch {
      // ignore
    }
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await monthlyApi.getConfigMilestones({ stage_id: filterStageId });
      setData(res?.data?.items || res?.data || []);
    } catch {
      message.error('获取里程碑数据失败');
    } finally {
      setLoading(false);
    }
  }, [filterStageId]);

  useEffect(() => {
    fetchStages();
  }, [fetchStages]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAdd = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const handleEdit = (record: Milestone) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleDelete = async (record: Milestone) => {
    try {
      await monthlyApi.deleteConfigMilestone(record.milestone_id);
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
        await monthlyApi.updateConfigMilestone(editing.milestone_id, values);
      } else {
        await monthlyApi.createConfigMilestone(values);
      }
      message.success(editing ? '修改成功' : '新增成功');
      setModalOpen(false);
      fetchData();
    } catch {
      message.error('保存失败');
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Select
          placeholder="筛选所属阶段"
          allowClear
          style={{ width: 220 }}
          value={filterStageId}
          onChange={setFilterStageId}
          options={stages.map((s) => ({ label: s.name, value: s.stage_id }))}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增里程碑
        </Button>
      </div>
      <Table
        dataSource={data}
        rowKey="milestone_id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        columns={[
          { title: '所属阶段', dataIndex: 'stage_name', width: 120 },
          { title: '名称', dataIndex: 'name' },
          { title: '排序', dataIndex: 'sort_order', width: 80, align: 'center' },
          {
            title: '操作',
            width: 150,
            align: 'center',
            render: (_: any, record: Milestone) => (
              <Space>
                <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
                <Popconfirm
                  title="确认删除？"
                  description="该里程碑下的所有作业计划及任务将被级联删除。"
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
        title={editing ? '编辑里程碑' : '新增里程碑'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleSave}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="stage_id"
            label="所属阶段"
            rules={[{ required: true, message: '请选择所属阶段' }]}
          >
            <Select placeholder="请选择" options={stages.map((s) => ({ label: s.name, value: s.stage_id }))} />
          </Form.Item>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入名称' }, { max: 100, message: '最长100字' }]}
          >
            <Input placeholder="如：前置作业-1号任务" />
          </Form.Item>
          <Form.Item
            name="sort_order"
            label="排序"
            initialValue={0}
            rules={[{ required: true, message: '请输入排序' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default MilestoneConfigTab;
