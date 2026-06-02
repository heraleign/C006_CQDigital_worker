import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card, Select, Button, Space, Tag, Modal, message, Spin,
  Typography, Row, Col, Statistic, Badge, Divider, Tabs, Table, Drawer,
} from 'antd';
import {
  ReloadOutlined, SendOutlined,
  CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined,
  LoadingOutlined, FileTextOutlined, WarningOutlined, ExportOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { monthlyApi } from '@/services/monthly';
import type { EChartsOption } from 'echarts';

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
  start_date: string;
  end_date: string;
  status: string;
}

const WORK_TYPE_ORDER = ['前置作业', '用户作业', '实收作业', '应收作业', '集团作业'];
const WORK_TYPE_COLORS = ['#e6f7ff', '#fff7e6', '#f6ffed', '#fff0f6', '#f0f5ff'];

const STATUS_CONFIG: Record<string, { color: string; icon: React.ReactNode }> = {
  '未开始': { color: '#d9d9d9', icon: <ClockCircleOutlined /> },
  '进行中': { color: '#1890ff', icon: <LoadingOutlined /> },
  '已完成': { color: '#52c41a', icon: <CheckCircleOutlined /> },
  '异常': { color: '#ff4d4f', icon: <CloseCircleOutlined /> },
};

/** Assign tasks to vertical tracks within a swimlane to minimize overlap */
function assignTracks(tasks: BillingTask[]): number[][] {
  if (tasks.length === 0) return [];
  const sorted = [...tasks].sort((a, b) => dayjs(a.planned_start).valueOf() - dayjs(b.planned_start).valueOf());
  // Each track is an array of task indices
  const tracks: number[][] = [];
  const trackEnds: number[] = [];

  sorted.forEach((task, idx) => {
    const start = dayjs(task.planned_start).valueOf();
    // Find first track that's free at this start time
    let placed = false;
    for (let t = 0; t < tracks.length; t++) {
      if (start >= trackEnds[t] + 60000) { // 1 min gap
        tracks[t].push(idx);
        trackEnds[t] = dayjs(task.planned_end).valueOf();
        placed = true;
        break;
      }
    }
    if (!placed) {
      tracks.push([idx]);
      trackEnds.push(dayjs(task.planned_end).valueOf());
    }
  });
  return tracks;
}

const BillingProgress: React.FC = () => {
  const [cycles, setCycles] = useState<BillingCycle[]>([]);
  const [selectedCycle, setSelectedCycle] = useState('202605');
  const [tasks, setTasks] = useState<BillingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [briefModalOpen, setBriefModalOpen] = useState(false);
  const [briefContent, setBriefContent] = useState('');
  const [briefLoading, setBriefLoading] = useState(false);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<BillingTask | null>(null);
  const [selectedLane, setSelectedLane] = useState<string>(WORK_TYPE_ORDER[0]);
  const [abnormalDrawerOpen, setAbnormalDrawerOpen] = useState(false);

  const ganttDataRef = useRef<{
    taskLookup: (BillingTask | null)[];
  }>({ taskLookup: [] });
  const chartRef = useRef<any>(null);

  const fetchCycles = useCallback(async () => {
    try {
      const res = await monthlyApi.getBillingCycles();
      const data = res?.data || res || [];
      setCycles(data);
      if (data.length > 0) {
        const active = data.find((c: BillingCycle) => c.status === 'active');
        setSelectedCycle(active?.cycle_id || data[0].cycle_id);
      }
    } catch {
      setCycles([
        { cycle_id: '202601', cycle_name: '2026年1月', start_date: '2026-01-31', end_date: '2026-02-03', status: 'closed' },
        { cycle_id: '202605', cycle_name: '2026年5月', start_date: '2026-05-27', end_date: '2026-05-30', status: 'active' },
      ]);
      setSelectedCycle('202605');
    }
  }, []);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const res = await monthlyApi.getBillingGantt(selectedCycle);
      const data = res?.data || res || { tasks: [] };
      setTasks(data.tasks || []);
    } catch {
      message.error('获取任务数据失败');
    } finally {
      setLoading(false);
    }
  }, [selectedCycle]);

  useEffect(() => { fetchCycles(); }, [fetchCycles]);

  useEffect(() => {
    if (selectedCycle) fetchTasks();
  }, [selectedCycle, fetchTasks]);

  const handleRefresh = () => {
    fetchTasks();
    message.success('已刷新');
  };

  const handleGenerateBrief = async () => {
    setBriefLoading(true);
    try {
      const res = await monthlyApi.generateBillingBrief(selectedCycle);
      const text = res?.data || res || '暂无数据';
      setBriefContent(text);
      setBriefModalOpen(true);
    } catch {
      message.error('生成简报失败');
    } finally {
      setBriefLoading(false);
    }
  };

  const handleExport = () => {
    const instance = chartRef.current?.getEchartsInstance();
    if (!instance) return;
    const url = instance.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' });
    const a = document.createElement('a');
    a.href = url;
    a.download = `月账进度_${selectedCycle}.png`;
    a.click();
    message.success('甘特图已导出');
  };

  const handleTaskClick = (task: BillingTask) => {
    setSelectedTask(task);
    setStatusModalOpen(true);
  };

  const handleStatusUpdate = async (newStatus: string) => {
    if (!selectedTask) return;
    try {
      await monthlyApi.updateBillingTaskStatus(selectedTask.task_id, newStatus);
      message.success(`状态已更新为"${newStatus}"`);
      setStatusModalOpen(false);
      fetchTasks();
    } catch {
      message.error('更新失败');
    }
  };

  // Per-swimlane stats
  const swimlaneStats = WORK_TYPE_ORDER.map((wt) => {
    const wtTasks = tasks.filter((t) => t.work_type === wt);
    const total = wtTasks.length;
    const completed = wtTasks.filter((t) => t.status === '已完成').length;
    const running = wtTasks.filter((t) => t.status === '进行中').length;
    const abnormal = wtTasks.filter((t) => t.status === '异常').length;
    return { workType: wt, total, completed, running, abnormal, pct: total > 0 ? Math.round((completed / total) * 100) : 0 };
  });

  const totalAll = tasks.length;
  const completedAll = tasks.filter((t) => t.status === '已完成').length;
  const runningAll = tasks.filter((t) => t.status === '进行中').length;
  const abnormalAll = tasks.filter((t) => t.status === '异常').length;

  // Swimlane Gantt chart — y-axis shows 5 swimlanes, each contains all its task bars
  const getGanttOption = (): EChartsOption => {
    if (tasks.length === 0) return {};

    // Group tasks by swimlane
    const grouped = WORK_TYPE_ORDER.map((wt) => tasks.filter((t) => t.work_type === wt));
    const allStarts = tasks.map((t) => dayjs(t.planned_start).valueOf());
    const allEnds = tasks.map((t) => dayjs(t.planned_end).valueOf());
    const baseTime = Math.min(...allStarts);
    const endTime = Math.max(...allEnds);
    const now = Date.now();
    const LANE_HEIGHT = 2; // in category units — controls vertical packing

    const statusColors: Record<string, string> = {
      '未开始': '#d9d9d9', '进行中': '#1890ff', '已完成': '#52c41a', '异常': '#ff4d4f',
    };

    // Build per-swimlane data with vertical track assignment
    const seriesData: any[] = [];
    const taskLookup: (BillingTask | null)[] = [];
    const taskPosMap = new Map<string, { laneIdx: number; yOffset: number }>();
    let dataIdx = 0;

    grouped.forEach((swimTasks, laneIdx) => {
      if (swimTasks.length === 0) return;
      const tracks = assignTracks(swimTasks);
      const trackCount = Math.max(tracks.length, 1);

      tracks.forEach((track, trackIdx) => {
        track.forEach((taskIdx) => {
          const task = swimTasks[taskIdx];
          const startMs = dayjs(task.planned_start).valueOf();
          const endMs = dayjs(task.planned_end).valueOf();
          // y-offset: center of lane + offset based on track
          const yOffset = (trackIdx - (trackCount - 1) / 2) * 0.35;
          seriesData.push({
            value: [startMs, endMs, laneIdx, yOffset, task.status, task.task_code, task.task_name],
          });
          taskPosMap.set(task.task_code, { laneIdx, yOffset });
          taskLookup[dataIdx] = task;
          dataIdx++;
        });
      });
    });

    // Build dependency arrows: from dep task's right edge to current task's left edge
    const arrowData: any[] = [];
    const taskByCode = new Map(tasks.map((t) => [t.task_code, t]));
    tasks.forEach((task) => {
      if (!task.dependency_codes) return;
      const deps = task.dependency_codes.split(',').map((s) => s.trim());
      deps.forEach((depCode) => {
        const depPos = taskPosMap.get(depCode);
        const taskPos = taskPosMap.get(task.task_code);
        if (!depPos || !taskPos) return;
        const depEndMs = dayjs(taskByCode.get(depCode)!.planned_end).valueOf();
        const taskStartMs = dayjs(task.planned_start).valueOf();
        arrowData.push({
          value: [depEndMs, depPos.laneIdx + depPos.yOffset, taskStartMs, taskPos.laneIdx + taskPos.yOffset],
        });
      });
    });

    ganttDataRef.current = { taskLookup };

    return {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const d = params.data;
          if (!d) return '';
          const v = d.value || d;
          const task = ganttDataRef.current.taskLookup[params.dataIndex];
          const lines = [
            `<b>${v[5]}</b> ${v[6]}`,
            `泳道：${WORK_TYPE_ORDER[v[2]]}`,
            `状态：${v[4]}`,
            `计划：${dayjs(v[0]).format('MM-DD HH:mm')} - ${dayjs(v[1]).format('MM-DD HH:mm')}`,
          ];
          if (task?.assignee) lines.push(`负责人：${task.assignee}`);
          if (task?.dependency_codes) lines.push(`依赖：${task.dependency_codes}`);
          return lines.join('<br/>');
        },
      },
      grid: { left: 120, right: 40, top: 20, bottom: 45 },
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: 0,
          minValueSpan: 1800000, // min zoom 30min
        },
        {
          type: 'slider',
          xAxisIndex: 0,
          height: 20,
          bottom: 5,
          borderColor: '#d9d9d9',
          fillerColor: 'rgba(24, 144, 255, 0.15)',
          labelFormatter: (v: number) => dayjs(v).format('MM-DD HH:mm'),
          handleStyle: { borderColor: '#1890ff', color: '#1890ff' },
        },
      ],
      xAxis: {
        type: 'time',
        min: baseTime,
        max: endTime + 3600000,
        axisLabel: { formatter: (v: number) => dayjs(v).format('MM-DD HH:mm'), fontSize: 11 },
        splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f0f0f0' } },
      },
      yAxis: {
        type: 'category',
        data: WORK_TYPE_ORDER,
        axisLabel: { fontSize: 13, fontWeight: 'bold', padding: [0, 8, 0, 0] },
        splitLine: { show: false },
        axisTick: { show: false },
        axisLine: { show: false },
      },
      series: [
        // Swimlane backgrounds
        ...WORK_TYPE_ORDER.map((_, i) => ({
          type: 'custom' as const,
          renderItem: (params: any, api: any) => {
            const [xLeft] = api.coord([baseTime, 0]);
            const [xRight] = api.coord([endTime + 3600000, 0]);
            const [, y0] = api.coord([baseTime, i - 0.5]);
            const [, y1] = api.coord([baseTime, i + 0.5]);
            return {
              type: 'rect',
              shape: { x: xLeft, y: y0, width: xRight - xLeft, height: y1 - y0 },
              style: { fill: WORK_TYPE_COLORS[i % WORK_TYPE_COLORS.length], opacity: 0.4 },
              silent: true,
            };
          },
          data: [{ value: [0] }],
          z: 0,
        }) as any),
        // Task bars
        {
          type: 'custom',
          renderItem: (params: any, api: any) => {
            const d = seriesData[params.dataIndex];
            if (!d) return null;
            const [startMs, endMs, laneIdx, yOffset, status] = d.value;
            const barHeight = 8;
            const effectiveLanePos = laneIdx + yOffset;
            const [x, y] = api.coord([startMs, effectiveLanePos]);
            const [x2] = api.coord([endMs, effectiveLanePos]);
            const width = Math.max(x2 - x, 2);
            return {
              type: 'rect',
              shape: { x, y: y - barHeight / 2, width, height: barHeight },
              style: { fill: statusColors[status] || '#d9d9d9', stroke: '#fff', lineWidth: 1, opacity: 0.85 },
            };
          },
          data: seriesData,
          encode: { x: [0, 1], y: 2 },
          z: 10,
        },
        // Dependency arrows
        arrowData.length > 0 ? {
          type: 'custom',
          renderItem: (params: any, api: any) => {
            const d = arrowData[params.dataIndex];
            if (!d) return null;
            const [x1, y1, x2, y2] = d.value;
            const [px1, py1] = api.coord([x1, y1]);
            const [px2, py2] = api.coord([x2, y2]);
            const dx = px2 - px1;
            const dy = py2 - py1;
            if (Math.abs(dx) < 2) return null; // skip zero-length arrows
            const angle = Math.atan2(dy, dx);
            const headLen = 6;
            const headAngle = Math.PI / 6;
            return {
              type: 'group',
              children: [
                {
                  type: 'line',
                  shape: { x1: px1, y1: py1, x2: px2, y2: py2 },
                  style: { stroke: '#faad14', lineWidth: 1.5, lineDash: [4, 3] },
                },
                {
                  type: 'polygon',
                  shape: {
                    points: [
                      [px2, py2],
                      [px2 - headLen * Math.cos(angle - headAngle), py2 - headLen * Math.sin(angle - headAngle)],
                      [px2 - headLen * Math.cos(angle + headAngle), py2 - headLen * Math.sin(angle + headAngle)],
                    ],
                  },
                  style: { fill: '#faad14', stroke: '#faad14', lineWidth: 1 },
                },
              ],
            };
          },
          data: arrowData,
          z: 5,
          silent: true,
        } as any : {},
        // Current time marker
        now >= baseTime && now <= endTime ? {
          type: 'line',
          data: [],
          markLine: {
            silent: true,
            symbol: 'none',
            data: [{ xAxis: now }],
            lineStyle: { color: '#ff4d4f', width: 2 },
            label: { formatter: '现在', color: '#ff4d4f', fontSize: 10 },
          },
          z: 20,
        } as any : {},
      ].filter(Boolean),
    };
  };

  const handleChartClick = (params: any) => {
    const { taskLookup } = ganttDataRef.current;
    const task = taskLookup[params.dataIndex];
    if (task) handleTaskClick(task);
  };

  return (
    <div style={{ padding: 16 }}>
      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space size="middle">
              <Title level={4} style={{ margin: 0 }}>月账进度</Title>
              <Select value={selectedCycle} onChange={setSelectedCycle} style={{ width: 160 }}>
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
              <Button icon={<ReloadOutlined />} onClick={handleRefresh}>刷新</Button>
              <Button icon={<ExportOutlined />} onClick={handleExport}>导出</Button>
              <Button icon={<FileTextOutlined />} loading={briefLoading} onClick={handleGenerateBrief}>生成简报</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Stats Cards */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="总任务"
              value={totalAll}
              suffix={<Text type="secondary" style={{ fontSize: 14 }}>已完成 {completedAll}</Text>}
            />
          </Card>
        </Col>
        {swimlaneStats.map((stat) => (
          <Col span={4} key={stat.workType}>
            <Card size="small">
              <Statistic
                title={stat.workType}
                value={stat.pct}
                suffix="%"
                valueStyle={{ color: stat.pct === 100 ? '#52c41a' : '#1890ff', fontSize: 22 }}
              />
              <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                已完成 {stat.completed}/{stat.total}
                {stat.abnormal > 0 && <Tag color="error" style={{ marginLeft: 4 }}>{stat.abnormal}异常</Tag>}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Status Summary */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space size={16}>
          <Badge color="#52c41a" text={<Text>{completedAll} 已完成</Text>} />
          <Badge color="#1890ff" text={<Text>{runningAll} 进行中</Text>} />
          <Badge color="#d9d9d9" text={<Text>{totalAll - completedAll - runningAll - abnormalAll} 未开始</Text>} />
          {abnormalAll > 0 && (
            <Badge color="#ff4d4f" text={<Text type="danger" className="abnormal-blink" style={{ cursor: 'pointer' }} onClick={() => setAbnormalDrawerOpen(true)}>{abnormalAll} 异常</Text>} />
          )}
        </Space>
      </Card>

      {/* Gantt Chart */}
      <Card title="泳道里程碑甘特图" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>
        ) : tasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 100, color: '#999' }}>暂无任务数据，请先导入任务配置</div>
        ) : (
          <ReactECharts
            ref={chartRef}
            option={getGanttOption()}
            style={{ height: 380 }}
            notMerge
            onEvents={{ click: handleChartClick }}
          />
        )}
      </Card>

      {/* Task Detail by Swimlane */}
      <Card title="任务明细" style={{ marginTop: 16 }}>
        <Tabs
          activeKey={selectedLane}
          onChange={setSelectedLane}
          items={WORK_TYPE_ORDER.map((wt) => {
            const laneTasks = tasks.filter((t) => t.work_type === wt);
            return {
              key: wt,
              label: <span>{wt} <Tag>{laneTasks.length}</Tag></span>,
              children: (
                <Table
                  dataSource={laneTasks}
                  rowKey="task_id"
                  size="small"
                  pagination={{ pageSize: 20, showSizeChanger: true, pageSizeOptions: ['10', '20', '50'] }}
                  columns={[
                    { title: '编码', dataIndex: 'task_code', key: 'task_code', width: 110 },
                    { title: '任务名称', dataIndex: 'task_name', key: 'task_name', ellipsis: true },
                    { title: '计划开始', dataIndex: 'planned_start', key: 'planned_start', width: 150, render: (v: string) => dayjs(v).format('MM-DD HH:mm') },
                    { title: '计划结束', dataIndex: 'planned_end', key: 'planned_end', width: 150, render: (v: string) => dayjs(v).format('MM-DD HH:mm') },
                    { title: '耗时(分)', dataIndex: 'duration_minutes', key: 'duration_minutes', width: 80 },
                    { title: '负责人', dataIndex: 'assignee', key: 'assignee', width: 90 },
                    {
                      title: '依赖',
                      dataIndex: 'dependency_codes',
                      key: 'dependency_codes',
                      width: 120,
                      render: (v: string | null) => v || '-',
                    },
                    {
                      title: '状态',
                      dataIndex: 'status',
                      key: 'status',
                      width: 90,
                      render: (status: string, record: BillingTask) => (
                        <Tag
                          color={STATUS_CONFIG[status]?.color}
                          style={{ cursor: 'pointer' }}
                          onClick={() => handleTaskClick(record)}
                        >
                          {status}
                        </Tag>
                      ),
                    },
                    {
                      title: '操作',
                      key: 'action',
                      width: 90,
                      render: (_: any, record: BillingTask) => (
                        <Button size="small" onClick={() => handleTaskClick(record)}>更新状态</Button>
                      ),
                    },
                  ]}
                />
              ),
            };
          })}
        />
      </Card>

      {/* Status Update Modal */}
      <Modal
        title={selectedTask ? `更新状态 - ${selectedTask.task_code} ${selectedTask.task_name}` : ''}
        open={statusModalOpen}
        onCancel={() => setStatusModalOpen(false)}
        footer={null}
        width={400}
      >
        {selectedTask && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">当前状态：</Text>
              <Tag color={STATUS_CONFIG[selectedTask.status]?.color}>{selectedTask.status}</Tag>
            </div>
            <div style={{ marginBottom: 12 }}>
              <Text type="secondary">计划：</Text>
              <Text>{dayjs(selectedTask.planned_start).format('MM-DD HH:mm')} - {dayjs(selectedTask.planned_end).format('MM-DD HH:mm')}</Text>
            </div>
            {selectedTask.assignee && (
              <div style={{ marginBottom: 12 }}>
                <Text type="secondary">负责人：</Text>
                <Text>{selectedTask.assignee}</Text>
              </div>
            )}
            <Divider />
            <Text strong>更新状态：</Text>
            <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {Object.entries(STATUS_CONFIG).map(([status, config]) => (
                <Button
                  key={status}
                  icon={config.icon}
                  style={{
                    borderColor: config.color,
                    color: selectedTask.status === status ? '#fff' : config.color,
                    backgroundColor: selectedTask.status === status ? config.color : undefined,
                  }}
                  disabled={selectedTask.status === status}
                  onClick={() => handleStatusUpdate(status)}
                >
                  {status}
                </Button>
              ))}
            </div>
          </div>
        )}
      </Modal>

      {/* Brief Preview Modal */}
      <Modal
        title={`进度简报 - ${selectedCycle}`}
        open={briefModalOpen}
        onCancel={() => setBriefModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setBriefModalOpen(false)}>关闭</Button>,
          <Button key="push" type="primary" icon={<SendOutlined />} onClick={() => message.success('已推送至钉钉群（演示）')}>
            推送钉钉
          </Button>,
        ]}
        width={560}
      >
        <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 13, lineHeight: 1.8, background: '#f5f5f5', padding: 16, borderRadius: 8 }}>
          {briefContent || '生成中...'}
        </div>
      </Modal>

      {/* Abnormal Tasks Drawer */}
      <Drawer
        title={
          <Space>
            <WarningOutlined style={{ color: '#ff4d4f' }} />
            <span>异常任务</span>
            <Tag color="error">{abnormalAll}</Tag>
          </Space>
        }
        placement="right"
        open={abnormalDrawerOpen}
        onClose={() => setAbnormalDrawerOpen(false)}
        width={420}
      >
        {tasks.filter((t) => t.status === '异常').length === 0 ? (
          <Text type="secondary">暂无异常任务</Text>
        ) : (
          tasks.filter((t) => t.status === '异常').map((task) => (
            <Card key={task.task_id} size="small" style={{ marginBottom: 12, borderLeft: '3px solid #ff4d4f' }}>
              <Space direction="vertical" style={{ width: '100%' }} size={4}>
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                  <Text strong style={{ fontSize: 13 }}>{task.task_code}</Text>
                  <Tag>{task.work_type}</Tag>
                </div>
                <Text>{task.task_name}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {dayjs(task.planned_start).format('MM-DD HH:mm')} - {dayjs(task.planned_end).format('MM-DD HH:mm')}
                </Text>
                {task.assignee && <Text type="secondary" style={{ fontSize: 12 }}>负责人：{task.assignee}</Text>}
                {task.remark && <Text type="warning" style={{ fontSize: 12 }}>备注：{task.remark}</Text>}
                <Button
                  size="small"
                  type="primary"
                  danger
                  style={{ marginTop: 4 }}
                  onClick={() => { setAbnormalDrawerOpen(false); handleTaskClick(task); }}
                >
                  处理异常
                </Button>
              </Space>
            </Card>
          ))
        )}
      </Drawer>

      {/* Blink animation */}
      <style>{`
        .abnormal-blink {
          animation: blink 1.2s ease-in-out infinite;
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  );
};

export default BillingProgress;
