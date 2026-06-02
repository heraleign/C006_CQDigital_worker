import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Space, Segmented, Modal, Form, Input, Select, InputNumber, Tag, message, Spin, Alert, Empty, Typography, Row, Col, Tooltip } from 'antd';
import { PlusOutlined, ImportOutlined, CheckCircleOutlined, ThunderboltOutlined, DeploymentUnitOutlined, UnorderedListOutlined, BarsOutlined, ApartmentOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import StatusTag from '@/components/StatusTag';
import { monthlyApi } from '@/services/monthly';
import type { OrchestrationTask } from '@/types';

const { Title, Text } = Typography;

const TaskOrchestration: React.FC = () => {
  const [viewMode, setViewMode] = useState<string | number>('list');
  const [tasks, setTasks] = useState<OrchestrationTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState<OrchestrationTask | null>(null);
  const [addForm] = Form.useForm();

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await monthlyApi.getOrchestration({ page: 1, page_size: 100 });
      const items = res.data?.items || (Array.isArray(res.data) ? res.data : []);
      setTasks(items.length > 0 ? items : mockTasks);
    } catch (err: any) { setError(err?.message || '加载失败'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSave = async () => {
    try {
      const values = await addForm.validateFields();
      if (editingTask) { await monthlyApi.updateTask(editingTask.task_id, values); message.success('更新成功'); }
      else { await monthlyApi.createTask(values); message.success('创建成功'); }
      setAddModalVisible(false); addForm.resetFields(); setEditingTask(null); fetchData();
    } catch (err: any) { if (err?.message) message.error(err.message); }
  };

  const handleDelete = async (id: string) => {
    try { await monthlyApi.deleteTask(id); message.success('删除成功'); fetchData(); }
    catch (err: any) { message.error(err?.message || '删除失败'); }
  };

  const handleValidateDeps = () => {
    const visited = new Set<string>(); const inStack = new Set<string>(); let hasCycle = false;
    const dfs = (nodeId: string) => {
      if (inStack.has(nodeId)) { hasCycle = true; return; }
      if (visited.has(nodeId)) return;
      visited.add(nodeId); inStack.add(nodeId);
      const task = tasks.find((t) => t.task_id === nodeId || t.task_code === nodeId);
      if (task?.dependencies) task.dependencies.forEach(dfs);
      inStack.delete(nodeId);
    };
    tasks.forEach((t) => dfs(t.task_id || t.task_code));
    message[hasCycle ? 'error' : 'success'](hasCycle ? '存在循环依赖' : '依赖校验通过');
  };

  const handleGeneratePlan = () => { message.success('执行计划已生成'); setViewMode('gantt'); };

  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  const listColumns = [
    { title: '阶段', dataIndex: 'stage', key: 'stage', width: 100, render: (v: string) => {
      const m: Record<string, string> = { data_prep: 'blue', receivable: 'purple', received: 'cyan', audit: 'orange', report: 'green' };
      return <Tag color={m[v] || 'default'}>{v || '-'}</Tag>;
    }},
    { title: '序号', dataIndex: 'task_code', key: 'task_code', width: 80 },
    { title: '任务名', dataIndex: 'task_name', key: 'task_name' },
    { title: '平台', dataIndex: 'platform', key: 'platform', width: 90, render: (v: string) => v || '-' },
    { title: '上游依赖', dataIndex: 'dependencies', key: 'dependencies', width: 180, render: (v: string[]) =>
      v?.length ? v.map((d) => <Tag key={d} style={{ marginBottom: 2 }}>{d}</Tag>) : <Tag>无</Tag>
    },
    { title: '耗时预估', dataIndex: 'estimated_duration', key: 'estimated_duration', width: 90, render: (v: number) => v != null ? v + 'min' : '-' },
    { title: '操作', key: 'action', width: 120, render: (_: any, r: OrchestrationTask) => (
      <Space>
        <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditingTask(r); addForm.setFieldsValue(r); setAddModalVisible(true); }} />
        <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.task_id)} />
      </Space>
    )},
  ];

  const ganttData = tasks.filter((t) => t.estimated_duration).map((t, idx) => ({ task: t.task_name, stage: t.stage, duration: t.estimated_duration || 60, code: t.task_code || '' }));
  const ganttOption = {
    tooltip: { trigger: 'axis' as const, axisPointer: { type: 'shadow' as const }, formatter: (params: any) => { const d = ganttData[params[0]?.dataIndex]; return d ? d.task + '<br/>阶段: ' + (d.stage || '-') + '<br/>耗时: ' + d.duration + 'min' : ''; } },
    grid: { left: 160, right: 40, bottom: 30, top: 20 },
    xAxis: { type: 'value' as const, name: '耗时(min)', nameLocation: 'middle' as const, nameGap: 25 },
    yAxis: { type: 'category' as const, data: ganttData.map((d) => d.task).reverse(), axisLabel: { fontSize: 11 } },
    series: [{ type: 'bar' as const, data: ganttData.map((d) => d.duration).reverse(), barWidth: 16, itemStyle: { color: (p: any) => ['#1677ff','#52c41a','#faad14','#ff4d4f','#722ed1','#13c2c2','#eb2f96','#fa8c16'][p.dataIndex % 8], borderRadius: [0, 4, 4, 0] }, label: { show: true, position: 'right' as const, formatter: (p: any) => p.value + 'min' } }],
  };

  const dagNodes = tasks.map((t, idx) => ({ id: t.task_code || t.task_id, name: t.task_name, category: idx % 3, symbolSize: 45 }));
  const dagEdges: any[] = [];
  tasks.forEach((t) => { if (t.dependencies) t.dependencies.forEach((dep) => { const s = tasks.find((x) => x.task_code === dep || x.task_id === dep)?.task_code || dep; dagEdges.push({ source: s, target: t.task_code || t.task_id }); }); });
  const dagOption = {
    tooltip: { formatter: (params: any) => params.data?.name || params.name },
    series: [{
      type: 'graph' as const, layout: 'force' as const, force: { repulsion: 350, edgeLength: [80, 150], layoutAnimation: true }, roam: true, draggable: true,
      data: dagNodes.map((n) => ({ ...n, label: { show: true, position: 'bottom' as const, fontSize: 10 }, itemStyle: { color: ['#1677ff', '#52c41a', '#faad14'][n.category] } })),
      edges: dagEdges.map((e) => ({ ...e, lineStyle: { color: '#aaa', width: 1.5, curveness: 0.2 } })),
      categories: [{ name: '数据准备' }, { name: '应收处理' }, { name: '实收处理' }],
      lineStyle: { color: 'source', curveness: 0.3 },
      emphasis: { focus: 'adjacency' as const, lineStyle: { width: 3 } },
    }],
  };

  return (
    <div>
      <div className="page-header"><Title level={4} style={{ margin: 0 }}><DeploymentUnitOutlined style={{ marginRight: 8 }} />任务编排</Title></div>
      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingTask(null); addForm.resetFields(); setAddModalVisible(true); }}>新增</Button>
          <Button icon={<ImportOutlined />}>批量导入</Button>
          <Button icon={<CheckCircleOutlined />} onClick={handleValidateDeps}>校验依赖</Button>
          <Button type="primary" ghost icon={<ThunderboltOutlined />} onClick={handleGeneratePlan}>生成执行计划</Button>
        </Space>
        <Segmented value={viewMode} onChange={setViewMode}
          options={[
            { label: <span><UnorderedListOutlined /> 列表</span>, value: 'list' },
            { label: <span><BarsOutlined /> 甘特图</span>, value: 'gantt' },
            { label: <span><ApartmentOutlined /> DAG图</span>, value: 'dag' },
          ]} />
      </Row>
      <Spin spinning={loading}>
        {viewMode === 'list' && <Card><Table dataSource={tasks} rowKey={(r) => r.task_id || r.task_code} columns={listColumns} pagination={false} scroll={{ x: 900 }} locale={{ emptyText: <Empty description="暂无编排任务" /> }} /></Card>}
        {viewMode === 'gantt' && <Card title="任务甘特图">{ganttData.length > 0 ? <ReactECharts option={ganttOption} style={{ height: Math.max(300, ganttData.length * 45) }} /> : <Empty description="暂无甘特图数据" />}</Card>}
        {viewMode === 'dag' && <Card title="DAG依赖关系图">{dagNodes.length > 0 ? <ReactECharts option={dagOption} style={{ height: 520 }} /> : <Empty description="暂无DAG数据" />}</Card>}
      </Spin>
      <Modal title={editingTask ? '编辑任务' : '新增任务'} open={addModalVisible} onOk={handleSave} onCancel={() => { setAddModalVisible(false); addForm.resetFields(); setEditingTask(null); }} width={520} destroyOnClose>
        <Form form={addForm} layout="vertical">
          <Form.Item name="task_name" label="任务名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Row gutter={16}>
            <Col span={12}><Form.Item name="task_code" label="任务编号" rules={[{ required: true }]}><Input placeholder="如: T001" /></Form.Item></Col>
            <Col span={12}><Form.Item name="stage" label="阶段" rules={[{ required: true }]}><Select options={[{ label: '数据准备', value: 'data_prep' }, { label: '应收处理', value: 'receivable' }, { label: '实收处理', value: 'received' }, { label: '稽核校验', value: 'audit' }, { label: '报表生成', value: 'report' }]} /></Form.Item></Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}><Form.Item name="platform" label="平台"><Select options={[{ label: 'MySQL', value: 'mysql' }, { label: 'Hadoop', value: 'hadoop' }, { label: 'Oracle', value: 'oracle' }]} /></Form.Item></Col>
            <Col span={12}><Form.Item name="estimated_duration" label="耗时预估(分钟)"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
          </Row>
          <Form.Item name="dependencies" label="上游依赖"><Select mode="multiple" placeholder="选择依赖任务" options={tasks.filter((t) => t.task_id !== editingTask?.task_id).map((t) => ({ label: t.task_name, value: t.task_code || t.task_id }))} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

const mockTasks: OrchestrationTask[] = [
  { task_id: '1', task_code: 'T001', task_name: '数据抽取-应收', stage: 'data_prep', dependencies: [], estimated_duration: 30 },
  { task_id: '2', task_code: 'T002', task_name: '数据抽取-实收', stage: 'data_prep', dependencies: [], estimated_duration: 25 },
  { task_id: '3', task_code: 'T003', task_name: '应收宽表加工', stage: 'receivable', dependencies: ['T001'], estimated_duration: 45 },
  { task_id: '4', task_code: 'T004', task_name: '应收稽核计算', stage: 'audit', dependencies: ['T003'], estimated_duration: 20 },
  { task_id: '5', task_code: 'T005', task_name: 'SAP数据上传', stage: 'receivable', dependencies: ['T004'], estimated_duration: 15 },
  { task_id: '6', task_code: 'T006', task_name: '实收宽表加工', stage: 'received', dependencies: ['T002'], estimated_duration: 40 },
  { task_id: '7', task_code: 'T007', task_name: '实收稽核计算', stage: 'audit', dependencies: ['T006'], estimated_duration: 20 },
  { task_id: '8', task_code: 'T008', task_name: '报表批次生成', stage: 'report', dependencies: ['T005', 'T007'], estimated_duration: 35 },
  { task_id: '9', task_code: 'T009', task_name: '报表发布', stage: 'report', dependencies: ['T008'], estimated_duration: 10 },
];

export default TaskOrchestration;
