import React, { useState, useEffect } from 'react';
import { Tabs, Table, Card, Button, Space, Tag, Modal, Form, Select, InputNumber, Input, message, Spin, Alert, Empty, Typography } from 'antd';
import { PlusOutlined, EditOutlined, CheckCircleOutlined, SwapOutlined, BellOutlined, CloseCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import { auditApi } from '@/services/audit';
import type { AuditAlert } from '@/types';

const { Title } = Typography;

const AlertManage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('importance');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importanceConfigs, setImportanceConfigs] = useState<any[]>([]);
  const [upgradeRules, setUpgradeRules] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<AuditAlert[]>([]);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingConfig, setEditingConfig] = useState<any>(null);
  const [editForm] = Form.useForm();
  const [ruleModalVisible, setRuleModalVisible] = useState(false);
  const [ruleForm] = Form.useForm();
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [importanceRes, upgradeRes, alertsRes] = await Promise.all([
        auditApi.getImportanceConfigs(),
        auditApi.getUpgradeRules(),
        auditApi.getAlerts({ page: 1, page_size: 50 }),
      ]);
      setImportanceConfigs(importanceRes.data?.items || (Array.isArray(importanceRes.data) ? importanceRes.data : []));
      setUpgradeRules(upgradeRes.data?.items || (Array.isArray(upgradeRes.data) ? upgradeRes.data : []));
      setAlerts(alertsRes.data?.items || []);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAllData(); }, []);

  const handleAlertAction = async (alertId: string, action: string) => {
    setActionLoading(alertId);
    try {
      await auditApi.handleAlert(alertId, { action });
      const actionText = action === 'confirm' ? '确认' : action === 'upgrade' ? '升级' : '解决';
      message.success(actionText + '成功');
      fetchData();
    } catch (err: any) { message.error(err?.message || '操作失败'); }
    finally { setActionLoading(null); }
  };

  const handleEditConfig = async () => {
    try {
      const values = await editForm.validateFields();
      if (editingConfig) {
        await auditApi.updateImportanceConfig(editingConfig.id || editingConfig.config_id, values);
        message.success('更新成功');
      }
      setEditModalVisible(false);
      fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  const handleCreateRule = async () => {
    try {
      const values = await ruleForm.validateFields();
      await auditApi.createUpgradeRule(values);
      message.success('创建成功');
      setRuleModalVisible(false);
      ruleForm.resetFields();
      fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><BellOutlined style={{ marginRight: 8 }} />告警管理</Title></div>
      <Tabs activeKey={activeTab} onChange={setActiveTab}
        items={[
          { key: 'importance', label: '告警规则',
            children: <Spin spinning={loading}>
              <Table dataSource={importanceConfigs} rowKey={(r) => r.id || r.config_id}
                columns={[
                  { title: '规则名称', dataIndex: 'task_name', key: 'task_name' },
                  { title: '级别', dataIndex: 'level', key: 'level', width: 100, render: (v: string) => <StatusTag status={v} /> },
                  { title: '自动升级', dataIndex: 'auto_upgrade', key: 'auto_upgrade', width: 100, render: (v: boolean) => v ? <Tag color="blue">启用</Tag> : <Tag>禁用</Tag> },
                  { title: '持续失败次数', dataIndex: 'max_failures', key: 'max_failures', width: 120 },
                  { title: '操作', key: 'action', width: 100, render: (_: any, r: any) => (
                    <Button type="link" size="small" icon={<EditOutlined />}
                      onClick={() => { setEditingConfig(r); editForm.setFieldsValue(r); setEditModalVisible(true); }}>编辑</Button>
                  )},
                ]} pagination={false} locale={{ emptyText: <Empty description="暂无配置" /> }} />
            </Spin>
          },
          { key: 'upgrade', label: '升级规则',
            children: <Spin spinning={loading}>
              <div style={{ marginBottom: 16, textAlign: 'right' }}>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { ruleForm.resetFields(); setRuleModalVisible(true); }}>新建规则</Button>
              </div>
              <Table dataSource={upgradeRules} rowKey={(r) => r.id || r.rule_id}
                columns={[
                  { title: '规则名称', dataIndex: 'rule_name', key: 'rule_name' },
                  { title: '触发条件', dataIndex: 'condition', key: 'condition' },
                  { title: '升级方式', dataIndex: 'upgrade_method', key: 'upgrade_method' },
                  { title: '目标级别', dataIndex: 'target_level', key: 'target_level', render: (v: string) => <StatusTag status={v} /> },
                  { title: '状态', dataIndex: 'status', key: 'status', render: (v: string) => <StatusTag status={v} /> },
                ]} locale={{ emptyText: <Empty description="暂无升级规则" /> }} />
            </Spin>
          },
          { key: 'alerts', label: '告警记录(' + alerts.length + ')',
            children: <Spin spinning={loading}>
              <Table dataSource={alerts} rowKey="alert_id"
                columns={[
                  { title: '告警级别', dataIndex: 'alert_level', key: 'alert_level', width: 100, render: (v: string) => <StatusTag status={v} /> },
                  { title: '标题', dataIndex: 'title', key: 'title' },
                  { title: '来源任务', dataIndex: 'source_task', key: 'source_task' },
                  { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: (v: string) => <StatusTag status={v} /> },
                  { title: '时间', dataIndex: 'create_time', key: 'create_time', width: 170, render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-' },
                  { title: '操作', key: 'action', width: 220, render: (_: any, r: AuditAlert) => (
                    <Space>
                      <Button type="link" size="small" icon={<CheckCircleOutlined />} loading={actionLoading === r.alert_id} onClick={() => handleAlertAction(r.alert_id, 'confirm')}>确认</Button>
                      <Button type="link" size="small" icon={<SwapOutlined />} loading={actionLoading === r.alert_id} onClick={() => handleAlertAction(r.alert_id, 'upgrade')}>升级</Button>
                      <Button type="link" size="small" icon={<CloseCircleOutlined />} style={{ color: '#52c41a' }} loading={actionLoading === r.alert_id} onClick={() => handleAlertAction(r.alert_id, 'resolve')}>解决</Button>
                    </Space>
                  )},
                ]} locale={{ emptyText: <Empty description="暂无告警记录" /> }} />
            </Spin>
          },
        ]}
      />

      <Modal title="编辑告警规则" open={editModalVisible} onOk={handleEditConfig} onCancel={() => setEditModalVisible(false)} destroyOnClose>
        <Form form={editForm} layout="vertical">
          <Form.Item name="level" label="级别">
            <Select options={[{ label: '严重', value: 'critical' }, { label: '高', value: 'high' }, { label: '中', value: 'medium' }, { label: '低', value: 'low' }]} />
          </Form.Item>
          <Form.Item name="max_failures" label="持续失败次数">
            <InputNumber min={1} max={10} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="新建升级规则" open={ruleModalVisible} onOk={handleCreateRule} onCancel={() => { setRuleModalVisible(false); ruleForm.resetFields(); }} destroyOnClose>
        <Form form={ruleForm} layout="vertical">
          <Form.Item name="rule_name" label="规则名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="condition" label="触发条件"><Input placeholder="如: 连续失败3次" /></Form.Item>
          <Form.Item name="target_level" label="目标级别">
            <Select options={[{ label: '严重', value: 'critical' }, { label: '高', value: 'high' }, { label: '中', value: 'medium' }]} />
          </Form.Item>
          <Form.Item name="upgrade_method" label="升级方式">
            <Select options={[{ label: '自动升级', value: 'auto' }, { label: '手动确认后升级', value: 'manual' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AlertManage;
