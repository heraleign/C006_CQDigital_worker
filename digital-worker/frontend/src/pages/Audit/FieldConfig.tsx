import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Select, Input, Modal, Form, Radio, message, Spin, Alert, Empty, Popconfirm, Row, Col, Typography } from 'antd';
import { PlusOutlined, ImportOutlined, ExportOutlined, EditOutlined, DeleteOutlined, FieldBinaryOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import { auditApi } from '@/services/audit';
import type { FieldConfig } from '@/types';

const { Title } = Typography;

const FieldConfigPage: React.FC = () => {
  const [data, setData] = useState<FieldConfig[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState<FieldConfig | null>(null);
  const [form] = Form.useForm();

  // Cascading filter state
  const [datasources, setDatasources] = useState<any[]>([]);
  const [schemas, setSchemas] = useState<any[]>([]);
  const [tables, setTables] = useState<any[]>([]);
  const [filterDs, setFilterDs] = useState<string | undefined>(undefined);
  const [filterSchema, setFilterSchema] = useState<string | undefined>(undefined);
  const [filterTable, setFilterTable] = useState<string | undefined>(undefined);
  const [filterAuditType, setFilterAuditType] = useState<string | undefined>(undefined);
  const [filterStatus, setFilterStatus] = useState<string | undefined>(undefined);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { page, page_size: pageSize };
      if (filterDs) params.datasource_code = filterDs;
      if (filterSchema) params.schema_code = filterSchema;
      if (filterTable) params.table_code = filterTable;
      if (filterAuditType) params.audit_type = filterAuditType;
      if (filterStatus) params.status_cd = filterStatus;
      const res = await auditApi.getFields(params);
      setData(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  };

  const fetchCascades = async () => {
    try {
      const dsRes = await auditApi.getDatasources();
      setDatasources(Array.isArray(dsRes.data) ? dsRes.data : dsRes.data?.items || []);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchCascades(); }, []);

  useEffect(() => {
    if (filterDs) {
      auditApi.getSchemas(filterDs).then((res) => setSchemas(Array.isArray(res.data) ? res.data : res.data?.items || [])).catch(() => setSchemas([]));
      setFilterSchema(undefined); setFilterTable(undefined);
    } else { setSchemas([]); setFilterSchema(undefined); setFilterTable(undefined); }
  }, [filterDs]);

  useEffect(() => {
    if (filterDs && filterSchema) {
      auditApi.getTables(filterDs, filterSchema).then((res) => setTables(Array.isArray(res.data) ? res.data : res.data?.items || [])).catch(() => setTables([]));
      setFilterTable(undefined);
    } else { setTables([]); setFilterTable(undefined); }
  }, [filterSchema]);

  useEffect(() => { fetchData(); }, [page, pageSize, filterDs, filterSchema, filterTable, filterAuditType, filterStatus]);

  const handleCreate = () => { setEditingRecord(null); form.resetFields(); setModalVisible(true); };
  const handleEdit = (record: FieldConfig) => { setEditingRecord(record); form.setFieldsValue(record); setModalVisible(true); };
  const handleDelete = async (id: string) => {
    try { await auditApi.deleteField(id); message.success('删除成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '删除失败'); }
  };
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingRecord) { await auditApi.updateField(editingRecord.config_id, values); message.success('更新成功'); }
      else { await auditApi.createField(values); message.success('创建成功'); }
      setModalVisible(false); fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><FieldBinaryOutlined style={{ marginRight: 8 }} />指标配置</Title></div>
      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新建配置</Button>
          <Button icon={<ImportOutlined />}>批量导入</Button>
          <Button icon={<ExportOutlined />}>导出</Button>
        </Space>
        <Space wrap>
          <Select placeholder="数据源" allowClear style={{ width: 120 }} value={filterDs} onChange={setFilterDs}
            options={datasources.map((d: any) => ({ label: d.label || d.datasource_code || d.name, value: d.value || d.datasource_code || d.name }))} />
          <Select placeholder="库" allowClear style={{ width: 120 }} value={filterSchema} onChange={setFilterSchema} disabled={!filterDs}
            options={schemas.map((s: any) => ({ label: s.label || s.schema_code || s.name, value: s.value || s.schema_code || s.name }))} />
          <Select placeholder="表" allowClear style={{ width: 130 }} value={filterTable} onChange={setFilterTable} disabled={!filterSchema}
            options={tables.map((t: any) => ({ label: t.label || t.table_code || t.name, value: t.value || t.table_code || t.name }))} />
          <Select placeholder="稽核类型" allowClear style={{ width: 120 }} value={filterAuditType} onChange={setFilterAuditType}
            options={[{ label: '完整性', value: 'completeness' }, { label: '准确性', value: 'accuracy' }, { label: '一致性', value: 'consistency' }, { label: '及时性', value: 'timeliness' }]} />
          <Select placeholder="状态" allowClear style={{ width: 100 }} value={filterStatus} onChange={setFilterStatus}
            options={[{ label: '启用', value: 'active' }, { label: '停用', value: 'inactive' }]} />
        </Space>
      </Row>
      <Card><Spin spinning={loading}>
        <Table dataSource={data} rowKey="config_id"
          columns={[
            { title: '配置ID', dataIndex: 'config_id', key: 'config_id', width: 100 },
            { title: '数据源', dataIndex: 'datasource_code', key: 'datasource_code', width: 100 },
            { title: '库', dataIndex: 'schema_code', key: 'schema_code', width: 100 },
            { title: '表', dataIndex: 'table_code', key: 'table_code', width: 120 },
            { title: '字段', dataIndex: 'field_code', key: 'field_code', width: 100 },
            { title: '字段名', dataIndex: 'field_name', key: 'field_name', width: 120 },
            { title: '稽核类型', dataIndex: 'audit_type', key: 'audit_type', width: 100, render: (v: string) => <StatusTag status={v} /> },
            { title: '状态', dataIndex: 'status_cd', key: 'status_cd', width: 80, render: (v: string) => <StatusTag status={v} /> },
            { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 170, render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm') },
            { title: '操作', key: 'action', width: 130, render: (_: any, r: FieldConfig) => (
              <Space><Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(r)}>编辑</Button>
                <Popconfirm title="确认删除?" onConfirm={() => handleDelete(r.config_id)}>
                  <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button></Popconfirm></Space>
            )},
          ]}
          pagination={{ current: page, pageSize, total, onChange: (p, ps) => { setPage(p); setPageSize(ps); }, showSizeChanger: true, showTotal: (t) => '共 ' + t + ' 条' }}
          scroll={{ x: 1200 }} locale={{ emptyText: <Empty description="暂无数据" /> }} />
      </Spin></Card>
      <Modal title={editingRecord ? '编辑配置' : '新建配置'} open={modalVisible} onOk={handleSubmit} onCancel={() => setModalVisible(false)} width={600} destroyOnClose>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}><Form.Item name="datasource_code" label="数据源" rules={[{ required: true }]}>
              <Select options={[{ label: 'MySQL', value: 'mysql' }, { label: 'Oracle', value: 'oracle' }, { label: 'Hive', value: 'hive' }]} /></Form.Item></Col>
            <Col span={12}><Form.Item name="schema_code" label="库" rules={[{ required: true }]}>
              <Select options={[{ label: 'ods_db', value: 'ods_db' }, { label: 'dwd_db', value: 'dwd_db' }, { label: 'dws_db', value: 'dws_db' }]} /></Form.Item></Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}><Form.Item name="table_code" label="表" rules={[{ required: true }]}>
              <Select options={[{ label: 'receivable', value: 'receivable' }, { label: 'payment', value: 'payment' }]} /></Form.Item></Col>
            <Col span={12}><Form.Item name="field_code" label="字段"><Input /></Form.Item></Col>
          </Row>
          <Form.Item name="field_name" label="字段名"><Input /></Form.Item>
          <Form.Item name="audit_type" label="稽核类型" rules={[{ required: true }]}>
            <Radio.Group><Radio value="completeness">完整性</Radio><Radio value="accuracy">准确性</Radio><Radio value="consistency">一致性</Radio><Radio value="timeliness">及时性</Radio></Radio.Group></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FieldConfigPage;
