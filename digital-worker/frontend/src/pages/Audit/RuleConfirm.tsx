import React, { useState, useEffect } from 'react';
import { Tabs, Table, Card, Button, Space, Tag, Modal, Form, Select, Input, message, Spin, Alert, Empty, Row, Col, Descriptions, Typography, Popconfirm } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, EditOutlined, PlusOutlined, CheckCircleFilled } from '@ant-design/icons';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import { auditApi } from '@/services/audit';
import type { RuleConfig, AuditTask } from '@/types';

const { Title } = Typography;

const RuleConfirm: React.FC = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [pendingRules, setPendingRules] = useState<any[]>([]);
  const [confirmedRules, setConfirmedRules] = useState<RuleConfig[]>([]);
  const [tasks, setTasks] = useState<AuditTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  const [taskForm] = Form.useForm();
  const [confirmLoading, setConfirmLoading] = useState<string | null>(null);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: 1, page_size: 50 };
      // Fetch all tabs data on mount so counts aren't 0
      const [pendingRes, confirmedRes, tasksRes] = await Promise.all([
        auditApi.getRules({ ...params, status: 'pending' }),
        auditApi.getRules({ ...params, status: 'confirmed' }),
        auditApi.getTasks(params),
      ]);
      const pendingItems = pendingRes.data?.items || [];
      const confirmedItems = confirmedRes.data?.items || [];
      setPendingRules(pendingItems);
      setConfirmedRules(confirmedItems);
      setTasks(tasksRes.data?.items || []);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAllData(); }, []);

  const handleConfirm = async (ruleId: string) => {
    setConfirmLoading(ruleId);
    try { await auditApi.confirmRule(ruleId); message.success('确认成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '操作失败'); }
    finally { setConfirmLoading(null); }
  };

  const handleConfirmWithEdit = async (ruleId: string) => {
    setConfirmLoading(ruleId);
    try { await auditApi.confirmRule(ruleId, { modified: true }); message.success('修改确认成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '操作失败'); }
    finally { setConfirmLoading(null); }
  };

  const handleReject = async (ruleId: string) => {
    try { await auditApi.rejectRule(ruleId); message.success('已拒绝'); fetchData(); }
    catch (err: any) { message.error(err?.message || '操作失败'); }
  };

  const handleBatchConfirm = async () => {
    const ids = pendingRules.map((r) => r.rule_id);
    if (ids.length === 0) { message.warning('无待确认规则'); return; }
    try { await auditApi.batchConfirmRules(ids); message.success('批量确认成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '批量确认失败'); }
  };

  const handleCreateTask = async () => {
    try {
      const values = await taskForm.validateFields();
      await auditApi.createTask(values);
      message.success('任务创建成功');
      setTaskModalVisible(false);
      taskForm.resetFields();
      fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><CheckCircleOutlined style={{ marginRight: 8 }} />规则确认</Title></div>
      <Tabs activeKey={activeTab} onChange={setActiveTab}
        items={[
          { key: 'pending', label: '待确认规则(' + pendingRules.length + ')',
            children: <Spin spinning={loading}>
              {pendingRules.length > 0 && (
                <div style={{ marginBottom: 16, textAlign: 'right' }}>
                  <Popconfirm title="确认全部规则?" onConfirm={handleBatchConfirm}>
                    <Button type="primary" ghost>批量确认</Button>
                  </Popconfirm>
                </div>
              )}
              {pendingRules.length > 0 ? <Row gutter={[16, 16]}>
                {pendingRules.map((rule: any) => (
                  <Col span={12} key={rule.rule_id}>
                    <Card size="small" actions={[
                      <Button type="link" icon={<EditOutlined />} loading={confirmLoading === rule.rule_id} onClick={() => handleConfirmWithEdit(rule.rule_id)}>修改后确认</Button>,
                      <Button type="link" style={{ color: '#52c41a' }} icon={<CheckCircleFilled />} loading={confirmLoading === rule.rule_id} onClick={() => handleConfirm(rule.rule_id)}>直接确认</Button>,
                      <Button type="link" danger icon={<CloseCircleOutlined />} onClick={() => handleReject(rule.rule_id)}>拒绝</Button>,
                    ]}>
                      <Descriptions column={2} size="small">
                        <Descriptions.Item label="规则名称">{rule.rule_name}</Descriptions.Item>
                        <Descriptions.Item label="规则类型">{rule.rule_type}</Descriptions.Item>
                        <Descriptions.Item label="告警级别"><StatusTag status={rule.alert_level || 'medium'} /></Descriptions.Item>
                        <Descriptions.Item label="阈值">{rule.threshold_lower ?? 0} ~ {rule.threshold_upper ?? 100}</Descriptions.Item>
                      </Descriptions>
                    </Card>
                  </Col>
                ))}
              </Row> : <Empty description="暂无待确认规则" />}
            </Spin>
          },
          { key: 'confirmed', label: '已确认规则(' + confirmedRules.length + ')',
            children: <Spin spinning={loading}>
              <Table dataSource={confirmedRules} rowKey="rule_id"
                columns={[
                  { title: '规则ID', dataIndex: 'rule_id', key: 'rule_id', width: 100 },
                  { title: '规则名称', dataIndex: 'rule_name', key: 'rule_name' },
                  { title: '规则类型', dataIndex: 'rule_type', key: 'rule_type', width: 100 },
                  { title: '上限', dataIndex: 'threshold_upper', key: 'threshold_upper', width: 80 },
                  { title: '下限', dataIndex: 'threshold_lower', key: 'threshold_lower', width: 80 },
                  { title: '告警级别', dataIndex: 'alert_level', key: 'alert_level', width: 100, render: (v: string) => <StatusTag status={v} /> },
                  { title: '状态', dataIndex: 'status_cd', key: 'status_cd', width: 80, render: (v: string) => <StatusTag status={v} /> },
                  { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 170, render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm') },
                ]}
                pagination={{ pageSize: 10, showTotal: (t) => '共 ' + t + ' 条' }}
                scroll={{ x: 800 }} locale={{ emptyText: <Empty description="暂无已确认规则" /> }} />
            </Spin>
          },
          { key: 'tasks', label: '稽核任务(' + tasks.length + ')',
            children: <Spin spinning={loading}>
              <div style={{ marginBottom: 16, textAlign: 'right' }}>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { taskForm.resetFields(); setTaskModalVisible(true); }}>创建任务</Button>
              </div>
              <Table dataSource={tasks} rowKey="task_id"
                columns={[
                  { title: '任务ID', dataIndex: 'task_id', key: 'task_id', width: 100 },
                  { title: '任务名称', dataIndex: 'task_name', key: 'task_name' },
                  { title: '调度类型', dataIndex: 'schedule_type', key: 'schedule_type', width: 100 },
                  { title: '最后运行状态', dataIndex: 'last_run_status', key: 'last_run_status', width: 120, render: (v: string) => <StatusTag status={v || 'pending'} /> },
                  { title: '状态', dataIndex: 'status_cd', key: 'status_cd', width: 80, render: (v: string) => <StatusTag status={v} /> },
                ]}
                pagination={{ pageSize: 10, showTotal: (t) => '共 ' + t + ' 条' }}
                locale={{ emptyText: <Empty description="暂无稽核任务" /> }} />
            </Spin>
          },
        ]}
      />
      <Modal title="创建稽核任务" open={taskModalVisible} onOk={handleCreateTask} onCancel={() => setTaskModalVisible(false)} width={500} destroyOnClose>
        <Form form={taskForm} layout="vertical">
          <Form.Item name="task_name" label="任务名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="schedule_type" label="调度类型" rules={[{ required: true }]}>
            <Select options={[{ label: '每日', value: 'daily' }, { label: '每周', value: 'weekly' }, { label: '每月', value: 'monthly' }]} />
          </Form.Item>
          <Form.Item name="rule_ids" label="关联规则">
            <Select mode="multiple" placeholder="选择关联规则"
              options={[...pendingRules, ...confirmedRules].map((r) => ({ label: r.rule_name, value: r.rule_id }))} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RuleConfirm;
