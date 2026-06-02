import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, message, Space, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { monthlyApi } from '@/services/monthly';

interface Stage {
  stage_id: string;
  name: string;
  sort_order: number;
}

const StageConfigTab: React.FC = () => {
  const [data, setData] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Stage | null>(null);
  const [form] = Form.useForm();

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await monthlyApi.getStages();
      setData(res?.data?.items || res?.data || []);
    } catch {
      message.error('获取阶段数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAdd = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const handleEdit = (record: Stage) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleDelete = async (record: Stage) => {
    try {
      await monthlyApi.deleteStage(record.stage_id);
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
        await monthlyApi.updateStage(editing.stage_id, values);
      } else {
        await monthlyApi.createStage(values);
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
      <div style={{ marginBottom: 16, textAlign: 'right' }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增阶段
        </Button>
      </div>
      <Table
        dataSource={data}
        rowKey="stage_id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        columns={[
          { title: '排序', dataIndex: 'sort_order', width: 80, align: 'center' },
          { title: '名称', dataIndex: 'name' },
          {
            title: '操作',
            width: 150,
            align: 'center',
            render: (_: any, record: Stage) => (
              <Space>
                <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
                  编辑
                </Button>
                <Popconfirm
                  title="确认删除？"
                  description="该阶段下的所有里程碑及关联数据将被级联删除。"
                  onConfirm={() => handleDelete(record)}
                  okText="删除"
                  okButtonProps={{ danger: true }}
                >
                  <Button size="small" danger icon={<DeleteOutlined />}>
                    删除
                  </Button>
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />
      <Modal
        title={editing ? '编辑阶段' : '新增阶段'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleSave}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入名称' }, { max: 100, message: '最长100字' }]}
          >
            <Input placeholder="如：用户作业" />
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

export default StageConfigTab;
