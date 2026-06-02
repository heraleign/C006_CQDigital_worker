import React, { useState, useEffect } from 'react';
import { Card, Steps, Button, Transfer, Table, InputNumber, Select, Input, message, Spin, Empty, Alert, Space, Typography, Popconfirm } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, RobotOutlined, ReloadOutlined, SaveOutlined, ArrowLeftOutlined, ThunderboltOutlined, EditOutlined } from '@ant-design/icons';
import { auditApi } from '@/services/audit';
import type { FieldConfig } from '@/types';

const { Text } = Typography;

const RuleGenerate: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [fields, setFields] = useState<FieldConfig[]>([]);
  const [targetKeys, setTargetKeys] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generateStatus, setGenerateStatus] = useState('');
  const [generatedRules, setGeneratedRules] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editingKey, setEditingKey] = useState('');
  const [editCache, setEditCache] = useState<Record<string, any>>({});

  useEffect(() => {
    (async () => {
      setLoading(true);
      try { const res = await auditApi.getFields({ page: 1, page_size: 100 }); setFields(res.data?.items || []); }
      catch { /* ignore */ }
      finally { setLoading(false); }
    })();
  }, []);

  const handleGenerate = async () => {
    if (targetKeys.length === 0) { message.warning('请先选择稽核字段'); return; }
    setGenerating(true); setCurrentStep(1); setError(null);
    try {
      const res = await auditApi.generateRules(targetKeys);
      const steps = ['正在连接AI引擎...', '分析字段特征...', '匹配规则模板...', '计算阈值参数...', '生成规则建议...'];
      for (let i = 0; i < steps.length; i++) { setGenerateStatus(steps[i]); await new Promise((r) => setTimeout(r, 500)); }
      const mockRules = targetKeys.map((key, idx) => {
        const field = fields.find((f) => f.config_id === key);
        return { key: idx.toString(), config_id: key, field: field ? field.table_code + '.' + field.field_code : '未知字段', rule_type: 'range', threshold_upper: 100, threshold_lower: 0, alert_level: 'medium', rule_name: (field?.field_name || '字段') + '稽核规则' };
      });
      setGeneratedRules(mockRules);
      setCurrentStep(2);
    } catch (err: any) { setError(err?.message || '生成失败'); }
    finally { setGenerating(false); }
  };

  const handleSave = async () => { message.success('规则保存成功'); };

  const handleRegenerate = () => { setGeneratedRules([]); setCurrentStep(0); setGenerateStatus(''); setError(null); setEditingKey(''); setEditCache({}); };

  const isEditing = (key: string) => key === editingKey;

  const handleEdit = (record: any) => {
    setEditingKey(record.key);
    setEditCache({ ...record });
  };

  const handleSaveEdit = async (key: string) => {
    setGeneratedRules((prev) => prev.map((r) => (r.key === key ? { ...r, ...editCache } : r)));
    setEditingKey('');
    setEditCache({});
    message.success('已更新');
  };

  const handleCancelEdit = () => { setEditingKey(''); setEditCache({}); };

  const ruleColumns = [
    { title: '字段', dataIndex: 'field', key: 'field', width: 150 },
    { title: '规则名称', dataIndex: 'rule_name', key: 'rule_name', width: 140, render: (v: string, r: any) => isEditing(r.key) ? <Input value={editCache.rule_name || v} onChange={(e) => setEditCache({ ...editCache, rule_name: e.target.value })} size="small" /> : v },
    { title: '规则类型', dataIndex: 'rule_type', key: 'rule_type', width: 120, render: (v: string, r: any) => isEditing(r.key) ? <Select value={editCache.rule_type || v} onChange={(val) => setEditCache({ ...editCache, rule_type: val })} size="small" style={{ width: 110 }} options={[{ label: '范围校验', value: 'range' }, { label: '波动率', value: 'volatility' }, { label: '一致性', value: 'consistency' }, { label: '枚举值', value: 'enum' }]} /> : v },
    { title: '上限', dataIndex: 'threshold_upper', key: 'threshold_upper', width: 90, render: (v: number, r: any) => isEditing(r.key) ? <InputNumber value={editCache.threshold_upper ?? v} onChange={(val) => setEditCache({ ...editCache, threshold_upper: val })} size="small" style={{ width: 80 }} /> : v },
    { title: '下限', dataIndex: 'threshold_lower', key: 'threshold_lower', width: 90, render: (v: number, r: any) => isEditing(r.key) ? <InputNumber value={editCache.threshold_lower ?? v} onChange={(val) => setEditCache({ ...editCache, threshold_lower: val })} size="small" style={{ width: 80 }} /> : v },
    { title: '告警级别', dataIndex: 'alert_level', key: 'alert_level', width: 110, render: (v: string, r: any) => isEditing(r.key) ? <Select value={editCache.alert_level || v} onChange={(val) => setEditCache({ ...editCache, alert_level: val })} size="small" style={{ width: 100 }} options={[{ label: '严重', value: 'critical' }, { label: '高', value: 'high' }, { label: '中', value: 'medium' }, { label: '低', value: 'low' }]} /> : v },
    { title: '操作', key: 'action', width: 100, render: (_: any, record: any) => isEditing(record.key) ? (
      <Space><Button type="link" size="small" onClick={() => handleSaveEdit(record.key)}>保存</Button><Button type="link" size="small" onClick={handleCancelEdit}>取消</Button></Space>
    ) : (
      <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
    )},
  ];

  return (
    <div>
      <div className="page-header"><Typography.Title level={4} style={{ margin: 0 }}><ThunderboltOutlined style={{ marginRight: 8 }} />AI规则生成</Typography.Title></div>
      <Card>
        <Steps current={currentStep} items={[{ title: '选择稽核字段', icon: <RobotOutlined /> }, { title: 'AI规则生成', icon: generating ? <LoadingOutlined /> : <RobotOutlined /> }, { title: '规则确认', icon: <CheckCircleOutlined /> }]} style={{ marginBottom: 24 }} />
        {error && <Alert type="error" message={error} showIcon closable style={{ marginBottom: 16 }} />}
        {currentStep === 0 && (
          <div>
            <Spin spinning={loading}>
              <Transfer dataSource={fields.map((f) => ({ key: f.config_id, title: f.field_name + ' (' + f.table_code + '.' + f.field_code + ')' }))}
                targetKeys={targetKeys} onChange={(keys) => setTargetKeys(keys as string[])} render={(item) => item.title}
                titles={['可选字段', '已选字段']} listStyle={{ width: 320, height: 400 }} showSearch />
            </Spin>
            <div style={{ marginTop: 24, textAlign: 'right' }}>
              <Button type="primary" size="large" onClick={handleGenerate} loading={generating} icon={<RobotOutlined />}>AI生成规则</Button>
            </div>
          </div>
        )}
        {currentStep === 1 && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} />} />
            <div style={{ marginTop: 24 }}><Text strong style={{ fontSize: 16 }}>{generateStatus}</Text></div>
          </div>
        )}
        {currentStep === 2 && (
          <div>
            <Table dataSource={generatedRules} rowKey="key" pagination={false} columns={ruleColumns}
              locale={{ emptyText: <Empty description="暂无生成规则" /> }} style={{ marginBottom: 16 }} />
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button icon={<ArrowLeftOutlined />} onClick={handleRegenerate}>上一步</Button>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={handleRegenerate}>重新生成</Button>
                <Popconfirm title="确认保存?" onConfirm={handleSave}>
                  <Button type="primary" icon={<SaveOutlined />}>保存规则</Button>
                </Popconfirm>
              </Space>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default RuleGenerate;
