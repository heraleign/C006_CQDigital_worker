import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Progress, Table, Tag, Row, Col, Statistic,
  Typography, Badge, Empty, Spin, Space, Select,
  Button, Dropdown, message, Modal,
} from 'antd';
import {
  CheckCircleOutlined, ClockCircleOutlined, FlagOutlined,
  FileTextOutlined, BranchesOutlined, BarChartOutlined,
  UnorderedListOutlined, ScheduleOutlined, UserOutlined,
  RobotOutlined, DatabaseOutlined, MessageOutlined,
  PauseCircleOutlined, CheckSquareOutlined, MoreOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { monthlyApi } from '@/services/monthly';

const { Title, Text } = Typography;

// ===== Types =====
interface LedgerTask {
  task_id: string;
  task_type: 'TDP_TASK' | 'PUBLISH_MSG' | 'MANUAL_OP' | 'SQL_SCRIPT';
  content: string;
  sort_order: number;
  status: 'completed' | 'pending' | 'running' | 'paused' | 'manual_skipped' | 'failed';
  start_time?: string;
  end_time?: string;
}

interface LedgerWorkPlan {
  plan_id: string;
  seq_no: number;
  name: string;
  time_point: string;
  task_mode: string;
  is_system_task: boolean;
  status: 'completed' | 'pending' | 'running' | 'paused' | 'manual_skipped';
  start_time?: string;
  end_time?: string;
  tasks: LedgerTask[];
}

interface LedgerMilestone {
  milestone_id: string;
  name: string;
  sort_order: number;
  status: 'completed' | 'pending' | 'running' | 'paused' | 'manual_skipped';
  progress_pct: number;
  start_time?: string;
  end_time?: string;
  work_plans: LedgerWorkPlan[];
}

interface LedgerStage {
  stage_id: string;
  name: string;
  sort_order: number;
  status: 'completed' | 'pending' | 'running' | 'paused' | 'manual_skipped';
  progress_pct: number;
  start_time?: string;
  end_time?: string;
  milestone_count: number;
  completed_milestone_count: number;
  milestones: LedgerMilestone[];
}

interface ProgressSummary {
  total_expected: number;
  actual_completed: number;
  delayed: number;
  alerts: number;
}

interface LedgerOverview {
  acct_month: string;
  total_stages: number;
  completed_stages: number;
  total_milestones: number;
  completed_milestones: number;
  total_work_plans: number;
  completed_work_plans: number;
  total_tasks: number;
  completed_tasks: number;
  overall_progress_pct: number;
  stages: LedgerStage[];
  progress_summary?: ProgressSummary;
}

// ===== Constants =====
const TASK_TYPE_CONFIG: Record<string, { color: string; label: string; icon: React.ReactNode }> = {
  TDP_TASK: { color: 'blue', label: 'TDP任务', icon: <DatabaseOutlined /> },
  PUBLISH_MSG: { color: 'green', label: '发布消息', icon: <MessageOutlined /> },
  MANUAL_OP: { color: 'orange', label: '人工操作', icon: <UserOutlined /> },
  SQL_SCRIPT: { color: 'purple', label: 'SQL脚本', icon: <FileTextOutlined /> },
};

const STATUS_CONFIG: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
  completed: { color: '#52c41a', text: '已完成', icon: <CheckCircleOutlined /> },
  running: { color: '#1890ff', text: '进行中', icon: <ClockCircleOutlined /> },
  pending: { color: '#d9d9d9', text: '未开始', icon: <ClockCircleOutlined /> },
  paused: { color: '#ff4d4f', text: '已暂停', icon: <PauseCircleOutlined /> },
  manual_skipped: { color: '#fa8c16', text: '手工放过', icon: <CheckSquareOutlined /> },
};

const STAGE_COLORS = ['#1677ff', '#52c41a', '#faad14', '#fa8c16', '#eb2f96'];

// ===== Components =====

/** Status badge for any item */
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  return (
    <Tag color={cfg.color} icon={cfg.icon}>
      {cfg.text}
    </Tag>
  );
};

/** Task type tag */
const TaskTypeTag: React.FC<{ type: string }> = ({ type }) => {
  const cfg = TASK_TYPE_CONFIG[type] || TASK_TYPE_CONFIG.MANUAL_OP;
  return (
    <Tag color={cfg.color} icon={cfg.icon}>
      {cfg.label}
    </Tag>
  );
};

/** Stage progress card (top row) */
const StageCard: React.FC<{
  stage: LedgerStage;
  index: number;
  isActive: boolean;
  onClick: () => void;
}> = ({ stage, index, isActive, onClick }) => {
  const color = STAGE_COLORS[index % STAGE_COLORS.length];
  return (
    <Card
      size="small"
      style={{
        cursor: 'pointer',
        borderColor: isActive ? color : undefined,
        boxShadow: isActive ? `0 0 0 2px ${color}33` : undefined,
        transition: 'all 0.2s',
      }}
      onClick={onClick}
      styles={{ body: { padding: 16 } }}
    >
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: 10,
            color,
            fontSize: 16,
            fontWeight: 700,
          }}
        >
          {stage.sort_order}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <Text strong style={{ fontSize: 15 }} ellipsis>
            {stage.name}
          </Text>
          <div style={{ marginTop: 2 }}>
            <StatusBadge status={stage.status} />
          </div>
        </div>
      </div>
      <Progress
        percent={stage.progress_pct}
        size="small"
        strokeColor={color}
        format={(p) => `${p}%`}
      />
      <div style={{ marginTop: 4 }}>
        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            里程碑 {stage.completed_milestone_count}/{stage.milestone_count}
          </Text>
          <Text type="secondary" style={{ fontSize: 12, marginLeft: 4, marginRight: 4 }}>·</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {stage.milestones.reduce((sum, m) => sum + m.work_plans.length, 0)} 计划
          </Text>
        </div>
        <div style={{ marginTop: 2, display: 'flex', gap: 10 }}>
          {stage.start_time != null && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              <ClockCircleOutlined style={{ marginRight: 2 }} />
              {dayjs(stage.start_time).format('MM-DD HH:mm')}
            </Text>
          )}
          {stage.start_time != null && stage.end_time != null && (
            <Text type="secondary" style={{ fontSize: 11 }}>→</Text>
          )}
          {stage.end_time != null && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              <CheckCircleOutlined style={{ marginRight: 2 }} />
              {dayjs(stage.end_time).format('MM-DD HH:mm')}
            </Text>
          )}
        </div>
      </div>
    </Card>
  );
};

/** Milestone timeline item */
const MilestonePanel: React.FC<{
  milestone: LedgerMilestone;
  isActive: boolean;
  onClick: () => void;
}> = ({ milestone, isActive, onClick }) => {
  const completedPlans = milestone.work_plans.filter((p) => p.status === 'completed').length;
  const totalPlans = milestone.work_plans.length;

  return (
    <Card
      size="small"
      style={{
        marginBottom: 12,
        cursor: 'pointer',
        borderLeft: isActive ? '4px solid #1677ff' : '4px solid transparent',
        background: isActive ? '#f0f7ff' : undefined,
        transition: 'all 0.2s',
      }}
      onClick={onClick}
    >
      <Row align="middle" justify="space-between">
        <Col flex="auto">
          <Space>
            <FlagOutlined style={{ color: '#1677ff' }} />
            <Text strong>{milestone.name}</Text>
            <StatusBadge status={milestone.status} />
          </Space>
          <div style={{ marginTop: 6, paddingLeft: 24 }}>
            <Space size="middle" align="center">
              <Progress
                percent={milestone.progress_pct}
                size="small"
                style={{ width: 160 }}
                format={(p) => `${p}%`}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>
                作业计划 {completedPlans}/{totalPlans}
              </Text>
              {milestone.start_time && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <ClockCircleOutlined style={{ marginRight: 2 }} />
                  {dayjs(milestone.start_time).format('MM-DD HH:mm')}
                </Text>
              )}
              {milestone.start_time && milestone.end_time && (
                <Text type="secondary" style={{ fontSize: 12 }}>→</Text>
              )}
              {milestone.end_time && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <CheckCircleOutlined style={{ marginRight: 2 }} />
                  {dayjs(milestone.end_time).format('MM-DD HH:mm')}
                </Text>
              )}
            </Space>
          </div>
        </Col>
        <Col>
          <Badge
            count={totalPlans}
            style={{ backgroundColor: '#1677ff' }}
            overflowCount={99}
          />
        </Col>
      </Row>
    </Card>
  );
};

/** Work plan table expanded to show tasks */
const WorkPlanTable: React.FC<{
  workPlans: LedgerWorkPlan[];
  onPlanClick: (plan: LedgerWorkPlan) => void;
  activePlanId: string | null;
  onRefresh?: () => void;
}> = ({ workPlans, onPlanClick, activePlanId, onRefresh }) => {
  return (
    <Table
      dataSource={workPlans}
      rowKey="plan_id"
      size="small"
      pagination={false}
      scroll={{ x: 'max-content' }}
      expandable={{
        expandedRowRender: (record: LedgerWorkPlan) => (
          <TaskListTable tasks={record.tasks} onRefresh={onRefresh} />
        ),
        rowExpandable: (record: LedgerWorkPlan) => record.tasks.length > 0,
        expandedRowKeys: activePlanId ? [activePlanId] : [],
        onExpandedRowsChange: (keys) => {
          // Collapse: active plan was removed from keys
          if (activePlanId && !keys.includes(activePlanId)) {
            const plan = workPlans.find((p) => p.plan_id === activePlanId);
            if (plan) onPlanClick(plan);  // toggles activePlanId → null
          } else if (keys.length > 0) {
            // Expand: a new plan was added (last key)
            const key = keys[keys.length - 1] as string;
            if (key !== activePlanId) {
              const plan = workPlans.find((p) => p.plan_id === key);
              if (plan) onPlanClick(plan);
            }
          }
        },
      }}
      columns={[
        {
          title: '序号',
          dataIndex: 'seq_no',
          width: 60,
          align: 'center',
        },
        {
          title: '计划名称',
          dataIndex: 'name',
          render: (v: string, record: LedgerWorkPlan) => (
            <Space>
              <ScheduleOutlined />
              <Text strong={record.status === 'running'}>{v}</Text>
              {record.is_system_task && <Tag color="cyan">系统</Tag>}
            </Space>
          ),
        },
        {
          title: '时间点',
          dataIndex: 'time_point',
          width: 110,
          render: (v: string) => v || '-',
        },
        {
          title: '执行方式',
          dataIndex: 'task_mode',
          width: 100,
          render: (v: string) => (
            <Tag icon={v === '数字员工' ? <RobotOutlined /> : <UserOutlined />}>
              {v}
            </Tag>
          ),
        },
        {
          title: '开始时间',
          dataIndex: 'start_time',
          width: 120,
          align: 'center',
          render: (v?: string) => (v ? dayjs(v).format('MM-DD HH:mm') : <Text type="secondary">-</Text>),
        },
        {
          title: '完成时间',
          dataIndex: 'end_time',
          width: 120,
          align: 'center',
          render: (v?: string) => (v ? dayjs(v).format('MM-DD HH:mm') : <Text type="secondary">-</Text>),
        },
        {
          title: '任务数',
          dataIndex: 'tasks',
          width: 80,
          align: 'center',
          render: (tasks: LedgerTask[]) => (
            <Badge count={tasks.length} style={{ backgroundColor: '#52c41a' }} overflowCount={99} />
          ),
        },
        {
          title: '状态',
          dataIndex: 'status',
          width: 90,
          render: (status: string) => <StatusBadge status={status} />,
        },
      ]}
    />
  );
};

/** Task list table */
const TaskListTable: React.FC<{ tasks: LedgerTask[]; onRefresh?: () => void }> = ({ tasks, onRefresh }) => {
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const handleUpdateStatus = async (taskId: string, status: string) => {
    setUpdatingId(taskId);
    try {
      await monthlyApi.updateConfigTask(taskId, { status });
      message.success('状态更新成功');
      onRefresh?.();
    } catch {
      message.error('状态更新失败');
    } finally {
      setUpdatingId(null);
    }
  };

  const getActionItems = (record: LedgerTask) => {
    const items = [
      { key: 'completed', label: '标记完成' },
      { key: 'pending', label: '标记为未完成' },
      { key: 'running', label: '进行中' },
      { key: 'paused', label: '暂停' },
      { key: 'manual_skipped', label: '手工放过' },
    ].filter((item) => item.key !== record.status);
    return items.map((item) => ({
      key: item.key,
      label: item.label,
      onClick: () => handleUpdateStatus(record.task_id, item.key),
      disabled: updatingId === record.task_id,
    }));
  };

  if (tasks.length === 0) {
    return (
      <div style={{ padding: 16, textAlign: 'center' }}>
        <Empty description="暂无任务" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </div>
    );
  }

  return (
    <Table
      dataSource={tasks}
      rowKey="task_id"
      size="small"
      pagination={false}
      style={{ margin: '8px 0' }}
      columns={[
        {
          title: '排序',
          dataIndex: 'sort_order',
          width: 60,
          align: 'center',
        },
        {
          title: '任务类型',
          dataIndex: 'task_type',
          width: 120,
          render: (type: string) => <TaskTypeTag type={type} />,
        },
        {
          title: '任务内容',
          dataIndex: 'content',
          render: (v: string, record: LedgerTask) => (
            <Text
              code={record.task_type === 'SQL_SCRIPT'}
              style={record.task_type === 'SQL_SCRIPT' ? { display: 'block', whiteSpace: 'pre-wrap', background: '#f6ffed' } : undefined}
            >
              {v}
            </Text>
          ),
        },
        {
          title: '开始时间',
          dataIndex: 'start_time',
          width: 150,
          align: 'center',
          render: (v?: string) => (v ? dayjs(v).format('MM-DD HH:mm') : <Text type="secondary">-</Text>),
        },
        {
          title: '结束时间',
          dataIndex: 'end_time',
          width: 150,
          align: 'center',
          render: (v?: string) => (v ? dayjs(v).format('MM-DD HH:mm') : <Text type="secondary">-</Text>),
        },
        {
          title: '状态',
          dataIndex: 'status',
          width: 90,
          render: (status: string) => <StatusBadge status={status} />,
        },
        {
          title: '操作',
          width: 120,
          align: 'center',
          render: (_: unknown, record: LedgerTask) => {
            if (record.task_type === 'TDP_TASK') {
              return <Text type="secondary">-</Text>;
            }
            const items = getActionItems(record);
            if (items.length === 0) {
              return <Text type="secondary">-</Text>;
            }
            return (
              <Dropdown menu={{ items }} placement="bottomLeft">
                <Button size="small" icon={<MoreOutlined />} loading={updatingId === record.task_id}>
                  操作
                </Button>
              </Dropdown>
            );
          },
        },
      ]}
    />
  );
};

// ===== Helpers =====

/** Parse time_point "X日HH:MM" relative to acct_month "YYYYMM" → deadline Date */
const parseTimePoint = (timePoint: string | undefined, acctMonth: string): Date | null => {
  if (!timePoint) return null;
  const m = /(\d+)日(\d+):(\d+)/.exec(timePoint);
  if (!m) return null;
  const year = parseInt(acctMonth.slice(0, 4), 10);
  const month = parseInt(acctMonth.slice(4, 6), 10);
  return new Date(year, month - 1, parseInt(m[1], 10), parseInt(m[2], 10), parseInt(m[3], 10));
};

/** Task enriched with stage/milestone/work_plan hierarchy info. */
interface EnrichedTask extends LedgerTask {
  stage_name: string;
  milestone_name: string;
  plan_name: string;
  time_point?: string;
}

/** Collect tasks from all work_plans where deadline has passed, grouped by category. */
const collectTasksByCategory = (overview: LedgerOverview, acctMonth: string) => {
  const now = new Date();
  const planned: EnrichedTask[] = [];
  const completed: EnrichedTask[] = [];
  const delayed: EnrichedTask[] = [];
  const alerts: EnrichedTask[] = [];

  for (const stage of overview.stages) {
    for (const ms of stage.milestones) {
      for (const wp of ms.work_plans) {
        const deadline = parseTimePoint(wp.time_point, acctMonth);
        const tasks = wp.tasks.map((t) => ({
          ...t,
          stage_name: stage.name,
          milestone_name: ms.name,
          plan_name: wp.name,
          time_point: wp.time_point,
        }));
        for (const t of tasks) {
          if (!deadline || deadline > now) continue;
          planned.push(t);
          if (t.status === 'completed') completed.push(t);
          else delayed.push(t);
          if (t.status === 'failed') alerts.push(t);
        }
      }
    }
  }
  return { planned, completed, delayed, alerts };
};

/** Detail modal title + column config per category */
const CATEGORY_COLUMNS: Record<string, { title: string; color: string }> = {
  planned: { title: '计划完成任务列表', color: '#1677ff' },
  completed: { title: '实际完成任务列表', color: '#52c41a' },
  delayed: { title: '延迟任务列表', color: '#fa8c16' },
  alerts: { title: '告警任务列表', color: '#ff4d4f' },
};

const generateAcctMonths = (): string[] => {
  const start = '202512';
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;
  const end = `${currentYear}${String(currentMonth).padStart(2, '0')}`;

  const months: string[] = [];
  let year = parseInt(start.slice(0, 4), 10);
  let month = parseInt(start.slice(4, 6), 10);

  while (true) {
    const ym = `${year}${String(month).padStart(2, '0')}`;
    months.push(ym);
    if (ym === end) break;
    month++;
    if (month > 12) {
      month = 1;
      year++;
    }
  }

  return months.reverse();
};

// ===== Main Page =====
const acctMonthOptions = generateAcctMonths().map((m) => ({ value: m, label: m }));

const LedgerDisplay: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [overview, setOverview] = useState<LedgerOverview | null>(null);
  const [activeStageId, setActiveStageId] = useState<string | null>(null);
  const [activeMilestoneId, setActiveMilestoneId] = useState<string | null>(null);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<string>(acctMonthOptions[0]?.value || '');
  const [detailModal, setDetailModal] = useState<{
    visible: boolean;
    category: string;
    tasks: EnrichedTask[];
    title: string;
    color: string;
  }>({ visible: false, category: '', tasks: [], title: '', color: '' });
  const [modalFilterStage, setModalFilterStage] = useState<string>('');
  const [modalFilterMs, setModalFilterMs] = useState<string>('');
  const [modalFilterStatus, setModalFilterStatus] = useState<string>('');

  const handleShowDetail = (category: string) => {
    if (!overview) return;
    const collected = collectTasksByCategory(overview, selectedMonth);
    const data = collected[category as keyof typeof collected] as EnrichedTask[];
    const cfg = CATEGORY_COLUMNS[category] || { title: category, color: '#1677ff' };
    setDetailModal({ visible: true, category, tasks: data, title: cfg.title, color: cfg.color });
    setModalFilterStage('');
    setModalFilterMs('');
    setModalFilterStatus('');
  };

  // Derived filter options from modal tasks
  const modalStageOptions = [...new Set(detailModal.tasks.map((t) => t.stage_name))];
  const filteredTasks = detailModal.tasks.filter((t) => {
    if (modalFilterStage && t.stage_name !== modalFilterStage) return false;
    if (modalFilterMs && t.milestone_name !== modalFilterMs) return false;
    if (modalFilterStatus && t.status !== modalFilterStatus) return false;
    return true;
  });
  const modalMsOptions = [...new Set(
    detailModal.tasks
      .filter((t) => !modalFilterStage || t.stage_name === modalFilterStage)
      .map((t) => t.milestone_name)
  )];

  const fetchData = useCallback(async (month?: string, silent?: boolean) => {
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    try {
      const res = await monthlyApi.getLedgerOverview(month ? { acct_month: month } : undefined);
      const data: LedgerOverview = res?.data || res;
      setOverview(data);
      if (data.stages.length > 0 && !activeStageId) {
        // Default to first running or pending stage, or first stage
        const runningStage = data.stages.find((s) => s.status === 'running');
        setActiveStageId(runningStage?.stage_id || data.stages[0].stage_id);
      }
    } catch {
      // fallback to empty
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeStageId]);

  useEffect(() => {
    fetchData(selectedMonth);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeStage = overview?.stages.find((s) => s.stage_id === activeStageId);

  const handleStageClick = (stageId: string) => {
    setActiveStageId(stageId);
    setActiveMilestoneId(null);
    setActivePlanId(null);
  };

  const handleMilestoneClick = (milestoneId: string) => {
    setActiveMilestoneId(milestoneId === activeMilestoneId ? null : milestoneId);
    setActivePlanId(null);
  };

  const handlePlanClick = (plan: LedgerWorkPlan) => {
    setActivePlanId(plan.plan_id === activePlanId ? null : plan.plan_id);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <Spin size="large" tip="加载月账数据..." />
      </div>
    );
  }

  if (!overview) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <Empty description="暂无月账数据" />
      </div>
    );
  }

  return (
    <div style={{ padding: 16 }}>
      {/* ===== Header & Overall Progress ===== */}
      <Card style={{ marginBottom: 16 }}>
        <Row align="middle" justify="space-between" style={{ marginBottom: 16 }}>
          <Col>
            <Space align="center">
              <BarChartOutlined style={{ fontSize: 22, color: '#1677ff' }} />
              <Title level={4} style={{ margin: 0 }}>
                月账进度
              </Title>
              {refreshing && <Spin size="small" style={{ marginLeft: 8 }} />}
              <Select
                value={selectedMonth}
                onChange={(val) => {
                  setSelectedMonth(val);
                  fetchData(val);
                }}
                style={{ width: 120 }}
                options={acctMonthOptions}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Text type="secondary">总体进度</Text>
              <Progress
                type="circle"
                percent={overview.overall_progress_pct}
                size={60}
                strokeColor={{ '0%': '#1677ff', '100%': '#52c41a' }}
                format={(p) => <span style={{ fontSize: 14, fontWeight: 700 }}>{p}%</span>}
              />
            </Space>
          </Col>
        </Row>

        {/* ===== Progress Summary: clickable metrics ===== */}
        {overview.progress_summary && (
          <div style={{
            marginBottom: 16, padding: '10px 16px',
            background: '#fafafa', borderRadius: 8,
            border: '1px solid #f0f0f0',
          }}>
            <Space size="large">
              <a onClick={() => handleShowDetail('planned')} style={{ cursor: 'pointer', textDecoration: 'none' }}>
                <span style={{ color: '#1677ff', fontWeight: 600 }}>计划完成</span>
                <span style={{ fontSize: 20, fontWeight: 700, margin: '0 4px', color: '#1677ff' }}>
                  {overview.progress_summary.total_expected}
                </span>
                <Text type="secondary">项</Text>
              </a>
              <Text type="secondary">|</Text>
              <a onClick={() => handleShowDetail('completed')} style={{ cursor: 'pointer', textDecoration: 'none' }}>
                <span style={{ color: '#52c41a', fontWeight: 600 }}>实际完成</span>
                <span style={{ fontSize: 20, fontWeight: 700, margin: '0 4px', color: '#52c41a' }}>
                  {overview.progress_summary.actual_completed}
                </span>
                <Text type="secondary">项</Text>
              </a>
              <Text type="secondary">|</Text>
              <a onClick={() => handleShowDetail('delayed')} style={{ cursor: 'pointer', textDecoration: 'none' }}>
                <span style={{ color: '#fa8c16', fontWeight: 600 }}>已延迟</span>
                <span style={{ fontSize: 20, fontWeight: 700, margin: '0 4px', color: '#fa8c16' }}>
                  {overview.progress_summary.delayed}
                </span>
                <Text type="secondary">项</Text>
              </a>
              {overview.progress_summary.alerts > 0 && (
                <>
                  <Text type="secondary">|</Text>
                  <a onClick={() => handleShowDetail('alerts')} style={{ cursor: 'pointer', textDecoration: 'none' }}>
                    <span style={{ color: '#ff4d4f', fontWeight: 600 }}>告警</span>
                    <span style={{ fontSize: 20, fontWeight: 700, margin: '0 4px', color: '#ff4d4f' }}>
                      {overview.progress_summary.alerts}
                    </span>
                    <Text type="secondary">项</Text>
                  </a>
                </>
              )}
            </Space>
          </div>
        )}

        <Row gutter={16}>
          <Col span={4}>
            <Statistic
              title="作业阶段"
              value={overview.completed_stages}
              suffix={`/ ${overview.total_stages}`}
              valueStyle={{ color: '#1677ff', fontSize: 22 }}
            />
          </Col>
          <Col span={4}>
            <Statistic
              title="里程碑"
              value={overview.completed_milestones}
              suffix={`/ ${overview.total_milestones}`}
              valueStyle={{ color: '#52c41a', fontSize: 22 }}
            />
          </Col>
          <Col span={4}>
            <Statistic
              title="作业计划"
              value={overview.completed_work_plans}
              suffix={`/ ${overview.total_work_plans}`}
              valueStyle={{ color: '#faad14', fontSize: 22 }}
            />
          </Col>
          <Col span={4}>
            <Statistic
              title="任务"
              value={overview.completed_tasks}
              suffix={`/ ${overview.total_tasks}`}
              valueStyle={{ color: '#eb2f96', fontSize: 22 }}
            />
          </Col>
          <Col span={8}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'flex-end', alignItems: 'center', height: '100%' }}>
              {Object.entries(TASK_TYPE_CONFIG).map(([key, cfg]) => (
                <Tag key={key} color={cfg.color} icon={cfg.icon}>
                  {cfg.label}
                </Tag>
              ))}
            </div>
          </Col>
        </Row>
      </Card>

      {/* ===== Detail Modal ===== */}
      <Modal
        title={<span style={{ color: detailModal.color }}>{detailModal.title}（{detailModal.tasks.length} 项）</span>}
        open={detailModal.visible}
        onCancel={() => setDetailModal({ ...detailModal, visible: false })}
        footer={null}
        width={1100}
        styles={{ body: { maxHeight: '70vh', overflow: 'auto', padding: 16 } }}
      >
        {/* Filter row */}
        <Space style={{ marginBottom: 12 }}>
          <Select
            placeholder="按阶段筛选"
            allowClear
            style={{ width: 150 }}
            value={modalFilterStage || undefined}
            onChange={(v) => { setModalFilterStage(v || ''); setModalFilterMs(''); }}
            options={modalStageOptions.map((s) => ({ value: s, label: s }))}
          />
          <Select
            placeholder="按里程碑筛选"
            allowClear
            style={{ width: 180 }}
            value={modalFilterMs || undefined}
            onChange={(v) => setModalFilterMs(v || '')}
            options={modalMsOptions.map((s) => ({ value: s, label: s }))}
          />
          <Select
            placeholder="按状态筛选"
            allowClear
            style={{ width: 130 }}
            value={modalFilterStatus || undefined}
            onChange={(v) => setModalFilterStatus(v || '')}
            options={[
              { value: 'completed', label: '已完成' },
              { value: 'running', label: '进行中' },
              { value: 'pending', label: '未开始' },
              { value: 'paused', label: '已暂停' },
              { value: 'manual_skipped', label: '手工放过' },
              { value: 'failed', label: '失败' },
            ]}
          />
          <Text type="secondary">
            已筛 {filteredTasks.length} / {detailModal.tasks.length} 项
          </Text>
        </Space>

        {/* Task table with hierarchy + operations */}
        <Table
          dataSource={filteredTasks}
          rowKey="task_id"
          size="small"
          pagination={{ defaultPageSize: 10, pageSizeOptions: [10, 20, 50], showSizeChanger: true, showTotal: (t) => `共 ${t} 项` }}
          columns={[
            { title: '阶段', dataIndex: 'stage_name', width: 100, ellipsis: true },
            { title: '里程碑', dataIndex: 'milestone_name', width: 110, ellipsis: true },
            { title: '作业计划', dataIndex: 'plan_name', width: 130, ellipsis: true },
            { title: '时间点', dataIndex: 'time_point', width: 80 },
            {
              title: '任务内容', dataIndex: 'content', ellipsis: true,
              render: (v: string, r: EnrichedTask) => (
                <Text code={r.task_type === 'SQL_SCRIPT'} style={r.task_type === 'SQL_SCRIPT' ? { background: '#f6ffed' } : undefined}>
                  {v}
                </Text>
              ),
            },
            {
              title: '类型', dataIndex: 'task_type', width: 80,
              render: (v: string) => {
                const cfg = TASK_TYPE_CONFIG[v] || TASK_TYPE_CONFIG.MANUAL_OP;
                return <Tag color={cfg.color}>{cfg.label}</Tag>;
              },
            },
            {
              title: '状态', dataIndex: 'status', width: 85,
              render: (s: string) => <StatusBadge status={s} />,
            },
            {
              title: '操作', width: 100, align: 'center',
              render: (_: unknown, record: EnrichedTask) => {
                if (record.task_type === 'TDP_TASK') return <Text type="secondary">-</Text>;
                const items = [
                  { key: 'completed', label: '标记完成' },
                  { key: 'running', label: '进行中' },
                  { key: 'paused', label: '暂停' },
                  { key: 'manual_skipped', label: '手工放过' },
                  { key: 'pending', label: '标记为未完成' },
                ].filter((item) => item.key !== record.status).map((item) => ({
                  key: item.key,
                  label: item.label,
                  onClick: async () => {
                    try {
                      await monthlyApi.updateConfigTask(record.task_id, { status: item.key });
                      message.success('状态更新成功');
                      // Refresh modal data
                      if (overview) {
                        const collected = collectTasksByCategory(overview, selectedMonth);
                        const data = collected[detailModal.category as keyof typeof collected] as EnrichedTask[];
                        setDetailModal({ ...detailModal, tasks: data });
                      }
                      fetchData(selectedMonth, true);
                    } catch {
                      message.error('状态更新失败');
                    }
                  },
                }));
                return (
                  <Dropdown menu={{ items }} placement="bottomLeft">
                    <Button size="small" icon={<MoreOutlined />}>操作</Button>
                  </Dropdown>
                );
              },
            },
          ]}
        />
      </Modal>

      {/* ===== Stage Cards ===== */}
      <Card title={<Space><BranchesOutlined /><span>作业阶段（点击下钻）</span></Space>} style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]}>
          {overview.stages.map((stage, idx) => (
            <Col span={Math.floor(24 / overview.stages.length)} key={stage.stage_id}>
              <StageCard
                stage={stage}
                index={idx}
                isActive={stage.stage_id === activeStageId}
                onClick={() => handleStageClick(stage.stage_id)}
              />
            </Col>
          ))}
        </Row>
      </Card>

      {/* ===== Milestones ===== */}
      {activeStage && (
        <Card
          title={
            <Space>
              <FlagOutlined />
              <span>
                {activeStage.name} — 里程碑列表
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  ({activeStage.milestones.length} 个)
                </Text>
              </span>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          {activeStage.milestones.length === 0 ? (
            <Empty description="该阶段暂无里程碑" />
          ) : (
            activeStage.milestones.map((ms) => (
              <div key={ms.milestone_id}>
                <MilestonePanel
                  milestone={ms}
                  isActive={ms.milestone_id === activeMilestoneId}
                  onClick={() => handleMilestoneClick(ms.milestone_id)}
                />
                {/* ===== Work Plans (expand when milestone active) ===== */}
                {ms.milestone_id === activeMilestoneId && (
                  <div style={{ marginLeft: 24, marginBottom: 16, paddingLeft: 16, borderLeft: '2px dashed #d9d9d9' }}>
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>
                        <ScheduleOutlined style={{ marginRight: 6 }} />
                        作业计划列表
                      </Text>
                    </div>
                    {ms.work_plans.length === 0 ? (
                      <Empty description="该里程碑暂无作业计划" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                    ) : (
                      <WorkPlanTable
                        workPlans={ms.work_plans}
                        onPlanClick={handlePlanClick}
                        activePlanId={activePlanId}
                        onRefresh={() => fetchData(selectedMonth, true)}
                      />
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </Card>
      )}

      {/* ===== Task Legend & Summary ===== */}
      <Card
        title={
          <Space>
            <UnorderedListOutlined />
            <span>任务类型说明</span>
          </Space>
        }
        size="small"
      >
        <Row gutter={16}>
          {Object.entries(TASK_TYPE_CONFIG).map(([key, cfg]) => (
            <Col span={6} key={key}>
              <Card size="small" style={{ borderLeft: `3px solid var(--ant-${cfg.color}-6, ${cfg.color})` }}>
                <Space>
                  {cfg.icon}
                  <Text strong>{cfg.label}</Text>
                </Space>
                <div style={{ marginTop: 4 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {key === 'TDP_TASK' && 'TDP调度任务，如 [TDP][统一处理][序号2251]'}
                    {key === 'PUBLISH_MSG' && '系统发布消息通知'}
                    {key === 'MANUAL_OP' && '人工操作步骤，如截图、核对'}
                    {key === 'SQL_SCRIPT' && 'SQL脚本执行'}
                  </Text>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>
    </div>
  );
};

export default LedgerDisplay;
