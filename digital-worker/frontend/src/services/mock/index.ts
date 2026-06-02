import dayjs from 'dayjs';

// ===== Helpers =====
const rand = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;
const pick = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
const list = <T,>(n: number, fn: (i: number) => T): T[] => Array.from({ length: n }, (_, i) => fn(i));

// ===== Constants =====
const datasourceCodes = ['DS_BILLING', 'DS_CUSTOMER', 'DS_PRODUCT', 'DS_CHANNEL', 'DS_FINANCE'];
const schemaCodes = ['SCHEMA_PUBLIC', 'SCHEMA_CORE', 'SCHEMA_ODS', 'SCHEMA_DWD', 'SCHEMA_DWS'];
const tableNames = ['T_USER', 'T_ACCOUNT', 'T_BILL', 'T_PRODUCT', 'T_ORDER', 'T_PAYMENT', 'T_CHARGE', 'T_FEE', 'T_SUBS', 'T_SERVICE'];
const fieldNames = ['用户数', '总收入', '出账金额', '实收金额', '欠费金额', '销账金额', '优惠金额', '新增用户', '离网用户', '活跃用户', 'ARPU值', 'DOU值', '通话时长', '短信条数', '流量使用量'];
const auditTypes = ['完整性检查', '准确性检查', '一致性检查', '及时性检查', '波动性检查'];
const ruleTypes = ['波动率检查', '阈值检查', '环比检查', '同比检查', '波动范围检查'];
const alertLevels: string[] = ['high', 'medium', 'low'];
const statusOptions = ['active', 'inactive', 'draft'];
const taskStatuses = ['running', 'completed', 'failed', 'pending'];
const scheduleTypes = ['daily', 'weekly', 'monthly', 'on_demand'];
const problemTypes = ['数据延迟', '数据缺失', '数据异常', '口径不一致', '处理失败'];
const analysisStatuses = ['pending', 'analyzing', 'completed', 'failed'];
const categories = ['账单类', '用户类', '产品类', '收入类', '渠道类'];
const platforms = ['邮件', '钉钉', '企业微信', '系统消息'];
const stages = ['数据采集', '数据清洗', '数据加工', '数据稽核', '报表生成'];

// ===== Audit Mock Data =====
function generateFields() {
  return list(20, (i) => ({
    config_id: `CFG_${String(i + 1).padStart(4, '0')}`,
    datasource_code: pick(datasourceCodes),
    schema_code: pick(schemaCodes),
    table_code: pick(tableNames),
    field_code: `COL_${String(i + 1).padStart(3, '0')}`,
    field_name: fieldNames[i % fieldNames.length],
    audit_type: pick(auditTypes),
    status_cd: pick(statusOptions),
    create_time: dayjs().subtract(rand(1, 90), 'day').format('YYYY-MM-DD HH:mm:ss'),
  }));
}

function generateRules() {
  return list(25, (i) => ({
    rule_id: `RULE_${String(i + 1).padStart(4, '0')}`,
    config_id: `CFG_${String(rand(1, 20)).padStart(4, '0')}`,
    rule_name: `${pick(ruleTypes)}-${pick(fieldNames)}-${i + 1}`,
    rule_type: pick(ruleTypes),
    threshold_upper: parseFloat((Math.random() * 20 + 5).toFixed(2)),
    threshold_lower: parseFloat((Math.random() * 5).toFixed(2)),
    alert_level: pick(alertLevels),
    status_cd: pick(['active', 'active', 'active', 'inactive', 'draft']),
    create_time: dayjs().subtract(rand(1, 60), 'day').format('YYYY-MM-DD HH:mm:ss'),
  }));
}

function generateTasks() {
  return list(15, (i) => ({
    task_id: `TASK_${String(i + 1).padStart(4, '0')}`,
    task_name: `稽核任务-${i + 1}-${pick(['收入', '用户', '产品', '账单', '费用'])}`,
    schedule_type: pick(scheduleTypes),
    rule_ids: list(rand(2, 6), () => `RULE_${String(rand(1, 25)).padStart(4, '0')}`),
    last_run_status: pick(taskStatuses),
    status_cd: pick(['active', 'active', 'active', 'inactive']),
  }));
}

function generateAlerts() {
  const statuses = ['new', 'processing', 'resolved', 'ignored'];
  return list(30, (i) => ({
    alert_id: `ALT_${String(i + 1).padStart(4, '0')}`,
    alert_level: pick(alertLevels),
    title: `${pick(['收入', '用户数', '出账金额', 'ARPU', '活跃用户'])}${pick(['异常波动', '数据缺失', '超阈值', '环比异常'])}`,
    source_task: `TASK_${String(rand(1, 15)).padStart(4, '0')}`,
    status: pick(statuses),
    create_time: dayjs().subtract(rand(0, 7), 'day').format('YYYY-MM-DD HH:mm:ss'),
  }));
}

function generateResultStats(params?: any) {
  const days = 30;
  const dates = list(days, (i) => dayjs().subtract(days - 1 - i, 'day').format('YYYY-MM-DD'));
  return {
    total_checks: rand(8000, 12000),
    passed: rand(6000, 10000),
    failed: rand(100, 500),
    warning: rand(200, 800),
    pass_rate: parseFloat((Math.random() * 10 + 88).toFixed(2)),
    trend: dates.map((date) => ({
      date,
      total: rand(280, 420),
      passed: rand(240, 380),
      failed: rand(5, 30),
      pass_rate: parseFloat((Math.random() * 8 + 90).toFixed(2)),
    })),
    distribution: auditTypes.map((type) => ({
      type,
      count: rand(100, 800),
      failed: rand(5, 50),
    })),
    detail: [
      ...list(50, (i) => ({
        execution_id: `EXEC_${String(i + 1).padStart(6, '0')}`,
        task_id: `TASK_${String(rand(1, 15)).padStart(4, '0')}`,
        acct_date: dayjs().subtract(rand(0, 30), 'day').format('YYYY-MM-DD'),
        check_result: pick(['passed', 'failed', 'warning']),
        alert_level: pick(alertLevels),
        deviation_rate: parseFloat((Math.random() * 15).toFixed(4)),
      })),
      // 指标波动案例：新增用户数异常波动（+30%，超出阈值±20%）
      {
        execution_id: 'EXEC_000051',
        task_id: 'TASK_DEV_USER',
        task_name: '用户发展指标稽核任务',
        rule_name: '波动率检查-新增用户数',
        field_name: '新增用户数',
        check_value: '13,000户',
        threshold: '±20%',
        expected_value: '10,000户',
        acct_date: '2024-01-15',
        check_result: 'failed',
        alert_level: 'high',
        deviation_rate: 30.00,
        anomaly_type: 'fluctuation',
      },
      ...list(7, (i) => ({
        execution_id: `EXEC_${String(52 + i).padStart(6, '0')}`,
        task_id: `TASK_${String(rand(1, 15)).padStart(4, '0')}`,
        task_name: `稽核任务-${rand(1, 15)}-${pick(['收入', '用户', '产品', '账单', '费用'])}`,
        rule_name: `${pick(['波动率检查', '阈值检查', '环比检查', '同比检查'])}-${pick(['用户数', '总收入', '出账金额', 'ARPU值', '活跃用户', 'DOU值'])}`,
        field_name: pick(['用户数', '总收入', '出账金额', 'ARPU值', 'DOU值', '通话时长', '流量使用量']),
        check_value: String(rand(10000, 50000)),
        threshold: '±20%',
        acct_date: dayjs().subtract(rand(0, 30), 'day').format('YYYY-MM-DD'),
        check_result: 'failed',
        alert_level: 'high',
        deviation_rate: parseFloat((Math.random() * 25 + 15).toFixed(2)),
        anomaly_type: 'fluctuation',
      })),
    ],
  };
}
// ===== Root Cause Mock Data =====
function generateKnowledge() {
  const titles = ['账单延迟处理方案', '收入异常排查流程', '用户数据缺失修复', 'ARPU波动分析方法', '出账数据核对规范', '数据口径变更记录', 'ETL任务失败处理', '数据质量提升方案'];
  return list(20, (i) => ({
    doc_id: `DOC_${String(i + 1).padStart(4, '0')}`,
    title: titles[i % titles.length],
    category: pick(categories),
    content: `## ${titles[i % titles.length]}

### 问题描述
在数据运维过程中，${titles[i % titles.length]}是一个常见问题。

### 处理步骤
1. 确认数据来源
2. 检查数据链路
3. 分析异常原因
4. 制定修复方案
5. 执行修复并验证

### 注意事项
- 操作前需备份数据
- 关注上下游影响
- 做好变更记录`,
    tags: pick([['数据质量', '稽核'], ['性能', '优化'], ['故障', '恢复'], ['规范', '标准'], ['监控', '告警']]),
    create_time: dayjs().subtract(rand(1, 180), 'day').format('YYYY-MM-DD HH:mm:ss'),
  }));
}

function generateAnalysis() {
  return list(15, (i) => ({
    record_id: `AR_${String(i + 1).padStart(4, '0')}`,
    problem_description: `${pick(problemTypes)}问题-${dayjs().subtract(i, 'day').format('YYYY-MM-DD')}`,
    problem_type: pick(problemTypes),
    analysis_status: pick(analysisStatuses),
    root_cause_result: i % 3 === 0 ? '' : `${pick(['数据源异常', 'ETL脚本错误', '配置变更导致', '网络超时', '内存溢出'])}`,
    create_time: dayjs().subtract(rand(1, 30), 'day').format('YYYY-MM-DD HH:mm:ss'),
  }));
}

function generateCases() {
  return list(25, (i) => ({
    case_id: `CASE_${String(i + 1).padStart(4, '0')}`,
    problem_type: pick(problemTypes),
    problem_title: `${pick(['收入', '用户', '账单', '产品', '费用'])}${pick(['波动异常', '数据不一致', '处理延迟', '统计口径问题', '数据缺失'])}`,
    problem_feature: `特征：${pick(['波动率', '阈值', '环比', '同比'])}超出${rand(5, 50)}%`,
    root_cause: pick(['源系统数据未及时推送', 'ETL脚本逻辑错误', '配置项被误修改', '数据库连接超时', '分布式任务调度失败']),
    solution: pick(['重启调度任务并重新跑数', '修复ETL脚本逻辑并重跑', '恢复配置并刷新缓存', '优化数据库连接池配置', '调整任务调度超时时间']),
    keywords: `${pick(['异常', '失败', '延迟', '不一致', '错误'])},${pick(['修复', '排查', '优化', '调整', '升级'])}`,
    effectiveness_score: rand(60, 100),
    use_count: rand(1, 50),
  }));
}

function generateLineage() {
  const nodes = [
    { id: 'n1', name: '源系统A', type: 'source' },
    { id: 'n2', name: '源系统B', type: 'source' },
    { id: 'n3', name: 'ODS层', type: 'ods' },
    { id: 'n4', name: 'DWD层', type: 'dwd' },
    { id: 'n5', name: 'DWS层', type: 'dws' },
    { id: 'n6', name: 'ADS层', type: 'ads' },
    { id: 'n7', name: '账单宽表', type: 'table' },
    { id: 'n8', name: '用户宽表', type: 'table' },
    { id: 'n9', name: '收入汇总表', type: 'table' },
    { id: 'n10', name: '报表输出', type: 'report' },
  ];
  const edges = [
    { source: 'n1', target: 'n3', relation: '数据采集' },
    { source: 'n2', target: 'n3', relation: '数据采集' },
    { source: 'n3', target: 'n4', relation: '数据清洗' },
    { source: 'n4', target: 'n5', relation: '数据加工' },
    { source: 'n5', target: 'n6', relation: '数据汇总' },
    { source: 'n4', target: 'n7', relation: '宽表生成' },
    { source: 'n4', target: 'n8', relation: '宽表生成' },
    { source: 'n5', target: 'n9', relation: '汇总计算' },
    { source: 'n6', target: 'n10', relation: '报表输出' },
    { source: 'n7', target: 'n9', relation: '数据关联' },
    { source: 'n8', target: 'n9', relation: '数据关联' },
  ];
  return { nodes, edges };
}

function generateAnalysisPaths() {
  return list(10, (i) => ({
    path_id: `PATH_${String(i + 1).padStart(4, '0')}`,
    problem_type: problemTypes[i % problemTypes.length],
    step_order: rand(1, 6),
    step_name: `步骤${rand(1, 6)}-${pick(['数据采集', '数据校验', '异常定位', '根因分析', '方案推荐', '结果验证'])}`,
    tool_code: `TOOL_${String(rand(1, 8)).padStart(4, '0')}`,
  }));
}

function generateSuggestions() {
  return list(12, (i) => ({
    id: `SUG_${String(i + 1).padStart(4, '0')}`,
    title: `${pick(['优化', '改进', '提升', '完善'])}${pick(['调度策略', '数据校验规则', '监控告警', '处理流程', '配置管理'])}`,
    priority: pick(['high', 'medium', 'low']),
    status: pick(['pending', 'accepted', 'implemented', 'rejected']),
    content: `建议内容：针对${pick(['数据延迟问题', '质量稽核效率', '异常处理速度', '系统稳定性', '运维自动化水平'])}，建议${pick(['优化调度策略', '增加校验规则', '完善监控体系', '引入自动化工具', '建立标准化流程'])}。`,
    expected_benefit: `预期${pick(['提升效率', '降低延迟', '减少故障', '提高质量', '节省人力'])}${rand(10, 80)}%`,
    source_analysis: `AR_${String(rand(1, 15)).padStart(4, '0')}`,
  }));
}

// ===== Root Cause Task List =====
function generateRcaTasks() {
  const taskNames = [
    '集团上传产品实例表', '收入月账数据抽取', '用户打标任务', '账单数据清洗',
    '客户信息同步', '产品实例采集', '报表数据汇总', '指标计算任务',
    '数据质量稽核任务', 'ETL批量导入', 'CRM数据同步', '月账应收计算',
    '渠道数据归集', '费用明细对账', '账期数据归档', '经营分析报表',
    '数据备份任务', '数据迁移任务', '数据校验任务', '调度监控任务',
  ];
  const modules = ['数据采集', '数据清洗', '数据加工', '数据稽核', '报表生成', '数据同步', '数据归档'];
  const statuses = ['running', 'completed', 'failed', 'waiting', 'pending', 'delayed'];

  return list(25, (i) => {
    const isSpecial = i < 2;
    let status: string;
    if (isSpecial) {
      status = i === 0 ? 'delayed' : 'failed';
    } else {
      status = pick(statuses);
    }
    return {
      task_id: `TASK_${String(i + 1).padStart(4, '0')}`,
      task_code: `RCA_${dayjs().format('YYYYMM')}_${String(i + 1).padStart(3, '0')}`,
      task_name: taskNames[i % taskNames.length] + (i >= taskNames.length ? `-${Math.floor(i / taskNames.length) + 1}` : ''),
      status,
      module: pick(modules),
      owner: pick(['张三', '李四', '王五', '赵六', '陈七']),
      start_time: status === 'pending' ? '' : dayjs().subtract(rand(0, 48), 'hour').format('YYYY-MM-DD HH:mm:ss'),
      end_time: status === 'completed' ? dayjs().subtract(rand(0, 24), 'hour').format('YYYY-MM-DD HH:mm:ss') : '',
      duration: status === 'running' || status === 'waiting' || status === 'pending' ? '' : `${rand(5, 120)}分钟`,
      priority: pick(['P0', 'P1', 'P2']),
    };
  });
}

// ===== Monthly Mock Data =====
function generateProgress() {
  return {
    acct_month: dayjs().format('YYYY-MM'),
    total_tasks: rand(80, 150),
    completed_tasks: rand(40, 100),
    progress_pct: parseFloat((Math.random() * 30 + 60).toFixed(2)),
    estimated_completion: dayjs().add(rand(3, 10), 'day').format('YYYY-MM-DD'),
    status: 'active',
    stage_progress: stages.map((stage) => ({
      stage,
      progress: rand(30, 100),
      status: pick(['completed', 'running', 'pending']),
    })),
  };
}

// ===== Monthly Ledger Overview (四级层次) =====
function generateLedgerOverview() {
  const stageNames = ['用户作业', '前置作业', '实收作业', '应收作业', '集团作业'];
  const milestoneDefs = [
    // 用户作业 (stage 0)
    { stageIdx: 0, name: '用户作业-1号任务' },
    { stageIdx: 0, name: '用户作业-2号任务' },
    { stageIdx: 0, name: '用户作业-3号任务' },
    // 前置作业 (stage 1)
    { stageIdx: 1, name: '前置作业-月底任务' },
    { stageIdx: 1, name: '前置作业-1号任务' },
    { stageIdx: 1, name: '前置作业-2号任务' },
    { stageIdx: 1, name: '前置作业-3号任务' },
    // 实收作业 (stage 2)
    { stageIdx: 2, name: '实收作业-1号任务' },
    { stageIdx: 2, name: '实收作业-2号任务' },
    { stageIdx: 2, name: '实收作业-3号任务' },
    { stageIdx: 2, name: '实收作业-4号任务' },
    { stageIdx: 2, name: '实收作业-5号任务' },
    { stageIdx: 2, name: '实收作业-7号任务' },
    { stageIdx: 2, name: '实收作业-15号任务' },
    { stageIdx: 2, name: '实收作业-25号任务' },
    { stageIdx: 2, name: '实收作业-月底任务' },
    // 应收作业 (stage 3)
    { stageIdx: 3, name: '应收作业-月底任务' },
    { stageIdx: 3, name: '应收作业-1号任务' },
    { stageIdx: 3, name: '应收作业-2号任务' },
    // 集团作业 (stage 4)
    { stageIdx: 4, name: '集团作业-1号任务' },
    { stageIdx: 4, name: '集团作业-2号任务' },
    { stageIdx: 4, name: '集团作业-3号任务' },
  ];

  const planTemplates = [
    {
      seq_no: 1,
      name: '截图计费1号批次接口层采集任务启动情况',
      time_point: '1日10:00',
      task_mode: '人工',
      is_system_task: false,
      tasks: [
        { task_type: 'MANUAL_OP', content: '截图计费1号批次接口层采集任务启动情况' },
        { task_type: 'TDP_TASK', content: '[TDP][统一处理][序号2251][月]INFBSN一号批次_1' },
        { task_type: 'TDP_TASK', content: '[TDP][统一处理][序号2252][月]INFBSN一号批次_2' },
        { task_type: 'TDP_TASK', content: '[TDP][统一处理][序号2253][月]INFBSN一号批次_3' },
        { task_type: 'PUBLISH_MSG', content: '前置作业3：计费1号批次接口层采集任务已启动' },
      ],
    },
    {
      seq_no: 2,
      name: '检查用户数据完整性并发送通知',
      time_point: '1日11:00',
      task_mode: '数字员工',
      is_system_task: true,
      tasks: [
        { task_type: 'SQL_SCRIPT', content: 'select count(*) from T_USER where status = \'ACTIVE\'' },
        { task_type: 'SQL_SCRIPT', content: 'select count(*) from T_ACCOUNT where acct_month = \'202605\'' },
        { task_type: 'PUBLISH_MSG', content: '用户数据完整性检查完成，无异常' },
      ],
    },
    {
      seq_no: 3,
      name: '实收数据核对与稽核',
      time_point: '2日09:00',
      task_mode: '数字员工',
      is_system_task: true,
      tasks: [
        { task_type: 'TDP_TASK', content: '[TDP][统一处理][序号3301][月]REAL_INCOME_CHECK' },
        { task_type: 'MANUAL_OP', content: '核对实收金额与银行到账记录' },
        { task_type: 'SQL_SCRIPT', content: 'select sum(amount) from T_RECEIPT where acct_month = \'202605\'' },
        { task_type: 'PUBLISH_MSG', content: '实收数据核对完成，金额一致' },
      ],
    },
    {
      seq_no: 4,
      name: '应收账单生成与校验',
      time_point: '2日14:00',
      task_mode: '数字员工',
      is_system_task: true,
      tasks: [
        { task_type: 'TDP_TASK', content: '[TDP][统一处理][序号4401][月]BILL_GENERATE' },
        { task_type: 'TDP_TASK', content: '[TDP][统一处理][序号4402][月]BILL_VERIFY' },
        { task_type: 'MANUAL_OP', content: '抽检10条账单记录验证金额准确性' },
      ],
    },
    {
      seq_no: 5,
      name: '集团数据汇总上报',
      time_point: '3日10:00',
      task_mode: '数字员工',
      is_system_task: true,
      tasks: [
        { task_type: 'SQL_SCRIPT', content: 'select * from V_GROUP_SUMMARY where acct_month = \'202605\'' },
        { task_type: 'PUBLISH_MSG', content: '集团数据汇总完成，准备上报' },
        { task_type: 'MANUAL_OP', content: '确认集团上报数据格式与内容' },
      ],
    },
  ];

  // Build stages with milestones and work plans
  const stages = stageNames.map((name, stageIdx) => {
    const stageMilestones = milestoneDefs
      .filter((m) => m.stageIdx === stageIdx)
      .map((m, mIdx) => {
        const msStatus = stageIdx < 2 ? 'completed' : stageIdx === 2 ? (mIdx < 3 ? 'completed' : mIdx === 3 ? 'running' : 'pending') : 'pending';
        const workPlans = list(rand(2, 5), (pIdx) => {
          const tpl = planTemplates[(stageIdx + mIdx + pIdx) % planTemplates.length];
          const planStatus = msStatus === 'completed' ? 'completed' : msStatus === 'running' ? (pIdx < 2 ? 'completed' : pIdx === 2 ? 'running' : 'pending') : 'pending';
          return {
            plan_id: `PL_${stageIdx}_${mIdx}_${pIdx}`,
            seq_no: pIdx + 1,
            name: tpl.name,
            time_point: tpl.time_point,
            task_mode: tpl.task_mode,
            is_system_task: tpl.is_system_task,
            status: planStatus,
            tasks: tpl.tasks.map((t, tIdx) => ({
              task_id: `TK_${stageIdx}_${mIdx}_${pIdx}_${tIdx}`,
              task_type: t.task_type,
              content: t.content,
              sort_order: tIdx + 1,
              status: planStatus === 'completed' ? 'completed' : planStatus === 'running' ? (tIdx < 2 ? 'completed' : 'pending') : 'pending' as any,
            })),
          };
        });

        const completedPlans = workPlans.filter((p: any) => p.status === 'completed').length;
        const progressPct = workPlans.length > 0 ? Math.round((completedPlans / workPlans.length) * 100) : 0;

        return {
          milestone_id: `MS_${stageIdx}_${mIdx}`,
          name: m.name,
          sort_order: mIdx + 1,
          status: msStatus,
          progress_pct: progressPct,
          work_plans: workPlans,
        };
      });

    const completedMs = stageMilestones.filter((m: any) => m.status === 'completed').length;
    const progressPct = stageMilestones.length > 0 ? Math.round((completedMs / stageMilestones.length) * 100) : 0;

    return {
      stage_id: `ST_${stageIdx}`,
      name,
      sort_order: stageIdx + 1,
      status: stageIdx < 2 ? 'completed' : stageIdx === 2 ? 'running' : 'pending' as any,
      progress_pct: progressPct,
      milestone_count: stageMilestones.length,
      completed_milestone_count: completedMs,
      milestones: stageMilestones,
    };
  });

  const totalMilestones = stages.reduce((sum, s) => sum + s.milestones.length, 0);
  const completedMilestones = stages.reduce((sum, s) => sum + s.milestones.filter((m: any) => m.status === 'completed').length, 0);
  const totalWorkPlans = stages.reduce((sum, s) => sum + s.milestones.reduce((ms: number, m: any) => ms + m.work_plans.length, 0), 0);
  const completedWorkPlans = stages.reduce((sum, s) => sum + s.milestones.reduce((ms: number, m: any) => ms + m.work_plans.filter((p: any) => p.status === 'completed').length, 0), 0);
  const totalTasks = stages.reduce((sum, s) => sum + s.milestones.reduce((ms: number, m: any) => ms + m.work_plans.reduce((ps: number, p: any) => ps + p.tasks.length, 0), 0), 0);
  const completedTasks = stages.reduce((sum, s) => sum + s.milestones.reduce((ms: number, m: any) => ms + m.work_plans.reduce((ps: number, p: any) => ps + p.tasks.filter((t: any) => t.status === 'completed').length, 0), 0), 0);

  return {
    acct_month: dayjs().format('YYYY-MM'),
    total_stages: stages.length,
    completed_stages: stages.filter((s) => s.status === 'completed').length,
    total_milestones: totalMilestones,
    completed_milestones: completedMilestones,
    total_work_plans: totalWorkPlans,
    completed_work_plans: completedWorkPlans,
    total_tasks: totalTasks,
    completed_tasks: completedTasks,
    overall_progress_pct: Math.round((completedTasks / Math.max(totalTasks, 1)) * 100),
    stages,
  };
}

// ===== Config Mock Data =====
const configStages = [
  { stage_id: 'st_1', name: '用户作业', sort_order: 1 },
  { stage_id: 'st_2', name: '前置作业', sort_order: 2 },
  { stage_id: 'st_3', name: '实收作业', sort_order: 3 },
  { stage_id: 'st_4', name: '应收作业', sort_order: 4 },
  { stage_id: 'st_5', name: '集团作业', sort_order: 5 },
];

const configMilestoneDefs = [
  { stage_id: 'st_1', name: '用户作业-1号任务', sort_order: 1 },
  { stage_id: 'st_1', name: '用户作业-2号任务', sort_order: 2 },
  { stage_id: 'st_1', name: '用户作业-3号任务', sort_order: 3 },
  { stage_id: 'st_2', name: '前置作业-月底任务', sort_order: 1 },
  { stage_id: 'st_2', name: '前置作业-1号任务', sort_order: 2 },
  { stage_id: 'st_2', name: '前置作业-2号任务', sort_order: 3 },
  { stage_id: 'st_2', name: '前置作业-3号任务', sort_order: 4 },
  { stage_id: 'st_3', name: '实收作业-1号任务', sort_order: 1 },
  { stage_id: 'st_3', name: '实收作业-2号任务', sort_order: 2 },
  { stage_id: 'st_3', name: '实收作业-3号任务', sort_order: 3 },
  { stage_id: 'st_3', name: '实收作业-4号任务', sort_order: 4 },
  { stage_id: 'st_3', name: '实收作业-5号任务', sort_order: 5 },
  { stage_id: 'st_4', name: '应收作业-月底任务', sort_order: 1 },
  { stage_id: 'st_4', name: '应收作业-1号任务', sort_order: 2 },
  { stage_id: 'st_4', name: '应收作业-2号任务', sort_order: 3 },
  { stage_id: 'st_5', name: '集团作业-1号任务', sort_order: 1 },
  { stage_id: 'st_5', name: '集团作业-2号任务', sort_order: 2 },
  { stage_id: 'st_5', name: '集团作业-3号任务', sort_order: 3 },
];

function generateConfigStages() {
  return configStages;
}

function generateConfigMilestones(stageId?: string) {
  let items = configMilestoneDefs.map((m, i) => ({
    milestone_id: `ms_${i + 1}`,
    stage_id: m.stage_id,
    stage_name: configStages.find((s) => s.stage_id === m.stage_id)?.name || '',
    name: m.name,
    sort_order: m.sort_order,
  }));
  if (stageId) items = items.filter((m) => m.stage_id === stageId);
  return items;
}

function generateConfigWorkPlans(params?: any) {
  const all = [];
  let idx = 1;
  for (const ms of configMilestoneDefs) {
    const msIdx = configMilestoneDefs.indexOf(ms);
    const planCount = rand(2, 5);
    for (let p = 0; p < planCount; p++) {
      all.push({
        plan_id: `wp_${idx}`,
        stage_id: ms.stage_id,
        stage_name: configStages.find((s) => s.stage_id === ms.stage_id)?.name || '',
        milestone_id: `ms_${msIdx + 1}`,
        milestone_name: ms.name,
        seq_no: p + 1,
        name: `${ms.name} 计划-${p + 1}`,
        time_point: `${p + 1}日${String(8 + p * 2).padStart(2, '0')}:00`,
        task_mode: pick(['人工', '数字员工']),
        is_system_task: Math.random() > 0.5,
        exec_template: '',
      });
      idx++;
    }
  }
  let filtered = all;
  if (params?.stage_id) filtered = filtered.filter((i) => i.stage_id === params.stage_id);
  if (params?.milestone_id) filtered = filtered.filter((i) => i.milestone_id === params.milestone_id);
  return filtered;
}

function generateConfigTasks(params?: any) {
  const taskContents = [
    { type: 'TDP_TASK', content: '[TDP][统一处理][序号2251][月]INFBSN一号批次_1' },
    { type: 'PUBLISH_MSG', content: '前置作业3：计费1号批次接口层采集任务已启动' },
    { type: 'MANUAL_OP', content: '截图计费1号批次接口层采集任务启动情况' },
    { type: 'SQL_SCRIPT', content: 'select count(*) from T_USER where status = \'ACTIVE\'' },
    { type: 'TDP_TASK', content: '[TDP][统一处理][序号3301][月]REAL_INCOME_CHECK' },
    { type: 'MANUAL_OP', content: '核对实收金额与银行到账记录' },
  ];
  const all = [];
  const plans = generateConfigWorkPlans();
  let idx = 1;
  for (const plan of plans) {
    const taskCount = rand(1, 4);
    for (let t = 0; t < taskCount; t++) {
      const tpl = taskContents[idx % taskContents.length];
      all.push({
        task_id: `tk_${idx}`,
        stage_id: plan.stage_id,
        stage_name: plan.stage_name,
        milestone_id: plan.milestone_id,
        milestone_name: plan.milestone_name,
        plan_id: plan.plan_id,
        plan_name: plan.name,
        task_type: tpl.type,
        content: tpl.content,
        sort_order: t + 1,
      });
      idx++;
    }
  }
  let filtered = all;
  if (params?.stage_id) filtered = filtered.filter((i) => i.stage_id === params.stage_id);
  if (params?.milestone_id) filtered = filtered.filter((i) => i.milestone_id === params.milestone_id);
  if (params?.plan_id) filtered = filtered.filter((i) => i.plan_id === params.plan_id);
  return filtered;
}

function parseTemplateMock(template: string) {
  const tasks: any[] = [];
  let order = 1;
  // TDP tasks
  const tdpMatches = template.match(/\[TDP\][^\n、）,，]+/g);
  if (tdpMatches) {
    tdpMatches.forEach((m) => {
      tasks.push({ sort_order: order++, task_type: 'TDP_TASK', content: m.trim() });
    });
  }
  // Publish messages
  const pubMatches = template.match(/发布‘([^‘’“”\n]+)’/g);
  if (pubMatches) {
    pubMatches.forEach((m) => {
      const content = m.replace(/发布‘/, '').replace(/’$/, '');
      tasks.push({ sort_order: order++, task_type: 'PUBLISH_MSG', content: content.trim() });
    });
  }
  // SQL scripts
  const sqlMatches = template.match(/(select|insert|create|drop)\s[\s\S]+?(?=\n\n|\n\d+\.|$)/gi);
  if (sqlMatches) {
    sqlMatches.forEach((m) => {
      tasks.push({ sort_order: order++, task_type: 'SQL_SCRIPT', content: m.trim() });
    });
  }
  // Manual ops (numbered steps)
  const manualMatches = template.match(/^\d+[\.、]\s*(.+?)(?=^\d+[\.、]|\Z)/gm);
  if (manualMatches) {
    manualMatches.forEach((m) => {
      const content = m.replace(/^\d+[\.、]\s*/, '').trim();
      tasks.push({ sort_order: order++, task_type: 'MANUAL_OP', content });
    });
  }
  // Re-sort by appearance in template
  tasks.sort((a, b) => template.indexOf(a.content) - template.indexOf(b.content));
  tasks.forEach((t, i) => { t.sort_order = i + 1; });
  return tasks;
}

function generateMilestones() {
  return list(8, (i) => ({
    milestone_id: `MIL_${String(i + 1).padStart(4, '0')}`,
    milestone_name: stages[i % stages.length],
    target_time: dayjs().add(i * 3 - 5, 'day').format('YYYY-MM-DD HH:mm:ss'),
    actual_time: i < 4 ? dayjs().add(i * 3 - 5, 'day').format('YYYY-MM-DD HH:mm:ss') : '',
    status: i < 4 ? 'completed' : i === 4 ? 'running' : 'pending',
    delay_minutes: i < 4 ? rand(0, 120) : 0,
  }));
}

function generateRunningTasks() {
  return list(12, (i) => ({
    task_id: `MT_${String(i + 1).padStart(4, '0')}`,
    task_code: `MTH_${dayjs().format('YYYYMM')}_${String(i + 1).padStart(3, '0')}`,
    task_name: `${pick(['收入月账', '用户月账', '产品月账', '费用月账', '渠道月账'])}-${i + 1}`,
    stage: pick(stages),
    status: pick(taskStatuses),
    start_time: dayjs().subtract(rand(0, 24), 'hour').format('YYYY-MM-DD HH:mm:ss'),
    duration: rand(120, 3600),
    progress_pct: rand(0, 100),
  }));
}

function generateOrchestrationTasks() {
  return list(10, (i) => ({
    task_id: `OT_${String(i + 1).padStart(4, '0')}`,
    task_code: `ORC_${dayjs().format('YYYYMM')}_${String(i + 1).padStart(3, '0')}`,
    task_name: `${pick(['数据采集', '数据清洗', '数据加工', '数据稽核', '报表生成'])}-${i + 1}`,
    stage: pick(stages),
    dependencies: i > 0 ? [`OT_${String(i).padStart(4, '0')}`] : [],
    estimated_duration: rand(300, 3600),
  }));
}

function generateDailyReports() {
  return list(10, (i) => ({
    report_id: `DR_${String(i + 1).padStart(4, '0')}`,
    acct_month: dayjs().format('YYYY-MM'),
    report_date: dayjs().subtract(i, 'day').format('YYYY-MM-DD'),
    title: `${dayjs().subtract(i, 'day').format('YYYY-MM-DD')}出账日报`,
    content: {
      summary: `当日出账${rand(10000, 50000)}笔，金额${rand(1000, 5000)}万元，稽核通过率98.5%`,
      receivable: { total: rand(10000, 15000), amount: (rand(1000, 5000) * 1000).toLocaleString() + '元', passRate: (98 + Math.random() * 2).toFixed(1), anomalies: rand(1, 5) },
      received: { total: rand(8000, 12000), amount: (rand(800, 4000) * 1000).toLocaleString() + '元', passRate: (97 + Math.random() * 3).toFixed(1), anomalies: rand(2, 6) },
      audit: { total: rand(20, 35), passed: rand(18, 33), failed: rand(1, 4), passRate: (92 + Math.random() * 7).toFixed(1) },
      alerts: [
        { level: 'high', msg: `应收稽核-金额一致性检查发现${rand(1, 5)}条异常`, time: '10:30' },
        { level: 'medium', msg: '实收稽核-账龄分析逾期率超过阈值', time: '11:15' },
      ],
      conclusion: '建议关注异常项，及时跟进处理。整体进度可控。',
    },
    status: pick(['draft', 'published', 'archived']),
  }));
}

function generatePublishReports() {
  return list(8, (i) => ({
    report_id: `RP_${String(i + 1).padStart(4, '0')}`,
    report_name: `${dayjs().format('YYYY-MM')}${pick(['收入月报', '用户月报', '产品质量月报', '运维月报', '稽核月报'])}`,
    category: pick(['月报', '日报', '季报', '年报']),
    platform: pick(platforms),
    plan_time: dayjs().add(i, 'day').format('YYYY-MM-DD HH:mm:ss'),
    status: pick(['draft', 'scheduled', 'published', 'failed']),
  }));
}

// ===== Dashboard Mock Data =====
function generateDashboardSummary() {
  return {
    total_tasks: rand(80, 150),
    running_tasks: rand(5, 20),
    completed_tasks: rand(40, 100),
    failed_tasks: rand(1, 10),
    alert_count: rand(5, 30),
    quality_score: parseFloat((Math.random() * 15 + 82).toFixed(1)),
    progress_pct: parseFloat((Math.random() * 30 + 60).toFixed(1)),
  };
}

function generateTrends() {
  const days = 14;
  const categories = ['收入稽核', '用户稽核', '产品稽核'];
  const result = [];
  for (let d = 0; d < days; d++) {
    for (const cat of categories) {
      result.push({
        date: dayjs().subtract(days - 1 - d, 'day').format('YYYY-MM-DD'),
        value: rand(80, 100),
        category: cat,
      });
    }
  }
  return result;
}

function generateRecentAlerts() {
  return list(10, (i) => ({
    alert_id: `ALT_${String(rand(1, 30)).padStart(4, '0')}`,
    alert_level: pick(alertLevels),
    title: `${pick(['收入', '用户数', '出账金额', 'ARPU', '活跃用户'])}${pick(['异常波动', '数据缺失', '超阈值', '环比异常'])}`,
    source_task: `TASK_${String(rand(1, 15)).padStart(4, '0')}`,
    status: 'new',
    create_time: dayjs().subtract(rand(0, 2), 'hour').format('YYYY-MM-DD HH:mm:ss'),
  }));
}

// ===== Case Study Preset Data =====
const CASE_STUDIES = {
  'task_delay': {
    preset_type: 'task_delay',
    problem_description: '集团上传产品实例表任务超时2小时未完成，当前状态为等待中',
    task_id: 'JT_PROD_INST_UPLOAD',
    acct_month: '202604',
    analysis_logs: [
      { step: 1, action: '获取任务状态', detail: '调用 get_task_status("JT_PROD_INST_UPLOAD")', result: '任务状态：waiting（等待中），未失败 → 进入上游依赖追溯', duration: '1秒', status: 'completed' },
      { step: 2, action: '获取上游依赖', detail: '调用 get_upstream_dependencies("JT_PROD_INST_UPLOAD")', result: '上游任务：TASK_A(✓已完成)、TASK_B(✓已完成)、TASK_C(✗等待中)', duration: '2秒', status: 'completed' },
      { step: 3, action: '递归追溯上游', detail: '调用 get_upstream_dependencies("TASK_C")', result: '上游任务：TASK_C1(✓已完成)、TASK_C2(✗失败) ← 根源任务', duration: '2秒', status: 'completed' },
      { step: 4, action: '获取错误信息', detail: '调用 get_task_error_info("TASK_C2")', result: '错误类型：FILE_NOT_ARRIVED\n错误信息：源文件不存在 /data/interface/prod_inst_20260420.dat', duration: '1秒', status: 'completed' },
      { step: 5, action: '文件状态检查', detail: '检查文件 /data/interface/prod_inst_20260420.dat', result: '文件不存在 | 预计到达05:30 | 已延迟180分钟 | 近7天送达率100%', duration: '3秒', status: 'completed' },
      { step: 6, action: '核实根因详情', detail: '综合所有信息进行根因定位', result: '根因类型：FILE_NOT_ARRIVED（源文件未送达）\n溯源深度：2级\n影响链路：TASK_C2 → TASK_C → JT_PROD_INST_UPLOAD', duration: '2秒', status: 'completed' },
      { step: 7, action: '生成分析报告', detail: '生成结构化分析报告', result: '报告已生成，即将推送通知', duration: '2秒', status: 'completed' },
    ],
    result: {
      root_cause: '源文件未送达（FILE_NOT_ARRIVED）',
      root_cause_detail: '上游任务TASK_C2（源系统接口采集）因源文件 /data/interface/prod_inst_20260420.dat 未按时送达而失败，导致依赖链路上的TASK_C和JT_PROD_INST_UPLOAD任务阻塞等待。历史数据显示该文件近7天均准时到达（平均05:15），本次属偶发性延迟。',
      trace_path: 'JT_PROD_INST_UPLOAD(waiting) → TASK_C(waiting) → TASK_C2(failed) ← 根因',
      evidence: [
        '任务状态确认：JT_PROD_INST_UPLOAD 处于 waiting 状态，非失败',
        '上游追溯：TASK_C 因上游 TASK_C2 失败而阻塞',
        '根因定位：TASK_C2 源文件采集任务失败，错误类型 FILE_NOT_ARRIVED',
        '文件检查：/data/interface/prod_inst_20260420.dat 不存在于服务器',
        '历史对比：近7天文件均准时送达（平均05:15），属偶发性延迟',
      ],
      source_system: '集团CRM系统',
      source_contact: '集团数据组-张三（13912345678）',
      impact_assessment: '影响下游2个任务阻塞，涉及产品实例表数据更新，预计影响5个业务报表的时效性',
      severity: '中',
      solution: [
        '联系集团数据组张三（13912345678）确认文件状态和预计送达时间',
        '文件送达后，手动触发 TASK_C2 任务重跑',
        'TASK_C 和 JT_PROD_INST_UPLOAD 将自动恢复执行',
        '验证下游数据完整性和准确性',
      ],
      prevention: [
        '增加文件送达预警监控，设置超时自动告警',
        '建立文件送达确认机制，数据提供方送达后自动通知',
        '考虑设置文件等待超时上限，超时后自动通知人工介入',
      ],
      manual_time: '75分钟',
      auto_time: '15秒',
      improvement_pct: '99.7%',
    },
  },
  'metric_anomaly': {
    preset_type: 'metric_anomaly',
    problem_description: '新增用户数指标异常波动，今日13,000户较昨日10,000户上涨30%，超出阈值±20%',
    task_id: '',
    acct_month: '202401',
    analysis_logs: [
      { step: 1, action: '意图识别', detail: '识别问题类型', result: '指标异常波动类 | 分析路径：多维度下钻 | 置信度96%', duration: '5秒', status: 'completed' },
      { step: 2, action: '数据质量校验', detail: '检查数据完整性、重复性、逻辑性', result: '✓ 数据完整 | ✗ 2,600条同一经办人 | ✗ 1,800条14-15时集中入网 | ✗ 实名率8%', duration: '30秒', status: 'completed' },
      { step: 3, action: '多维度下钻分析', detail: '按时间→地域→渠道→产品→用户画像逐级下钻', result: '14:00-15:00(+213%) → 渝北区(+220%,占增量73%) → XX代理商(+1300%) → 0元体验卡(+5100%) → 单人张三1800户/小时', duration: '90秒', status: 'completed' },
      { step: 4, action: '业务规则验证', detail: '执行5项业务规则检查', result: '单人效能(×180倍)✗ | 号码连号率68%✗ | 实名率8%✗ | 激活率3%✗ | 产品集中度96%✗', duration: '30秒', status: 'completed' },
      { step: 5, action: '根因定位', detail: '综合多维度交叉分析结果', result: '根因类型：CHANNEL_FRAUD（渠道虚假发展）\n置信度：98%\n证据：5维度交叉确认', duration: '10秒', status: 'completed' },
      { step: 6, action: '生成报告并推送', detail: '生成结构化报告并推送通知', result: '报告已生成，推送至量子密信+启明APP', duration: '10秒', status: 'completed' },
    ],
    result: {
      root_cause: '渠道虚假发展（CHANNEL_FRAUD）',
      root_cause_detail: '渝北XX代理商为冲刺KPI考核，利用0元体验卡政策漏洞，由经办人张三个人在14:00-15:00一小时内批量录入1,800户虚假用户信息。用户均未实名认证、未激活使用，号码连号率高达68%，属于典型的虚假发展行为。',
      trace_path: '指标异常(+30%) → 时间下钻(14时+213%) → 地域下钻(渝北+220%) → 渠道下钻(XX代理+1300%) → 产品下钻(0元卡+5100%) → 交叉定位 → 规则验证 → 根因确认',
      evidence: [
        '时间集中：14:00-15:00暴增1,800户（+213%）',
        '地域集中：渝北区增长2,200户，占增量73%',
        '渠道集中：XX代理商增长2,600户（+1300%）',
        '产品集中：0元体验卡2,600户（+5100%）',
        '经办集中：单人张三办理1,800户/小时，超标180倍',
        '号码异常：连号率68%（正常<5%）',
        '实名缺失：实名率8%（正常>95%）',
        '未激活：激活率3%（正常>80%）',
      ],
      fake_users: 2600,
      severity: '严重',
      risk_level: 'CRITICAL',
      impact_assessment: '2,600户虚假用户数据将严重影响经营分析准确性，涉及违反实名制监管规定',
      solution: [
        '【紧急】冻结渝北XX代理商发展权限，立即执行',
        '【紧急】锁定经办人张三操作账号，暂停业务办理',
        '【紧急】冻结2,600个疑似虚假用户，防止入网',
        '【调查】追溯该代理商近30天发展明细，排查历史数据',
        '【调查】外呼核实200个样本号码，确认虚假比例',
        '【长效】设置单人单小时发展量上限（≤20户）',
        '【长效】启用号码连号检测拦截规则（>5个连号触发）',
        '【长效】强制0元卡实时实名认证，未实名拒绝办理',
      ],
      prevention: [
        '单人单小时发展量上限 ≤20户，超限自动拦截',
        '号码连号检测：连号>5个时自动阻断发展',
        '实名认证强制：0元体验卡必须100%实时实名',
        '72小时未激活预警：激活率<30%时触发渠道预警',
      ],
      manual_time: '120分钟',
      auto_time: '79秒',
      improvement_pct: '99%',
    },
  },
};

// ===== Assistant Mock Data =====
function generateAssistantResponse(message: string): any {
  // Case study demo responses
  const caseStudyResponses: Record<string, { reply: string; suggestions: string[] }> = {
    '场景一：任务延期诊断': {
      reply: `我来帮您分析「集团上传产品实例表」任务延期问题 🔍

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Step 1] 查询任务状态...
✅ JT_PROD_INST_UPLOAD → 状态：waiting（等待中）
→ 非失败状态，进入上游依赖追溯

[Step 2] 获取上游依赖...
📋 上游任务清单：
  ✓ TASK_A — 已完成
  ✓ TASK_B — 已完成
  ✗ TASK_C — 等待中（阻塞点）

[Step 3] 递归追溯 TASK_C 上游...
📋 TASK_C 上游：
  ✓ TASK_C1 — 已完成
  ✗ TASK_C2 — 失败 ← 根源任务

[Step 4] 获取 TASK_C2 错误信息...
❌ 错误类型：FILE_NOT_ARRIVED
❌ 源文件不存在：/data/interface/prod_inst_20260420.dat

[Step 5] 文件状态检查...
📁 目标文件：prod_inst_20260420.dat
📁 是否存在：否
📁 预计到达：05:30，已延迟180分钟
📁 历史记录：近7天均准时送达

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **根因分析结果**

问题根因：源文件未送达（FILE_NOT_ARRIVED）
溯源链路：JT_PROD_INST_UPLOAD → TASK_C → TASK_C2 ← 根因

处理建议：
① 联系集团数据组张三（13912345678）确认文件状态
② 文件送达后触发 TASK_C2 重跑
③ 上下游任务将自动恢复执行
④ 建议增加文件送达预警监控

效果对比：人工75分钟 → 自动化15秒（提升99.7%）`,
      suggestions: ['场景二：指标波动诊断', '查进度', '看告警'],
    },
    '场景二：指标波动诊断': {
      reply: `我来帮您分析「新增用户数」指标异常波动 🔍

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Step 1] 数据质量校验...
✅ 数据采集完整，无缺失分区
⚠️ 发现异常特征：
  - 2,600条用户记录经办人同为「张三」
  - 1,800条在14:00-15:00集中入网
  - 异常渠道实名率仅8%

[Step 2] 多维度下钻分析...
┌──────────┬────────────┬──────────┬──────────┐
│ 维度      │ 今日值      │ 昨日值    │ 变化     │
├──────────┼────────────┼──────────┼──────────┤
│ 时间14时  │ 2,500户    │ 800户    │ +213% ✗  │
│ 地域渝北  │ 3,200户    │ 1,000户  │ +220% ✗  │
│ XX代理商  │ 2,800户    │ 200户    │ +1300% ✗ │
│ 0元体验卡 │ 2,600户    │ 50户     │ +5100% ✗ │
└──────────┴────────────┴──────────┴──────────┘

[Step 3] 业务规则验证...
❌ 单人效能：1,800户/小时（超标180倍）
❌ 号码连号率：68%（标准<5%）
❌ 实名率：8%（标准>95%）
❌ 激活率：3%（标准>80%）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **根因分析结果**

问题根因：渠道虚假发展（置信度98%）
风险等级：🔴 严重 | 虚假用户数：2,600户

紧急措施：
✅ 冻结渝北XX代理商发展权限
✅ 锁定经办人张三操作账号
✅ 冻结2,600个疑似虚假用户
📋 追溯近30天发展明细，设置单人发展量上限

效果对比：人工120分钟 → 自动化79秒（提升99%）`,
      suggestions: ['场景一：任务延期诊断', '查进度', '看告警'],
    },
  };

  // Check for case study demos first
  for (const [key, resp] of Object.entries(caseStudyResponses)) {
    if (message.includes(key) || message === key) {
      return resp;
    }
  }

  const responses: Record<string, string> = {
    '查进度': `当前月账处理进度为 78.5%，已完成 85 个任务中的 67 个。预计完成时间：2026-05-15。各阶段进度如下：
- 数据采集：100% ✅
- 数据清洗：95%
- 数据加工：82%
- 数据稽核：65%
- 报表生成：45%`,
    '看告警': '当前有 12 条未处理告警，其中严重级别 3 条，警告级别 5 条，提示级别 4 条。最紧急的告警是「收入异常波动」，来自稽核任务 TASK_0005。',
    '问任务': '目前有 8 个任务正在运行，5 个任务等待执行。运行中的任务包括：收入月账-001（87%）、用户月账-002（62%）、产品月账-003（45%）等。',
    '导数据': `数据导出功能支持以下格式：
1. CSV - 适用于Excel打开
2. Excel - 包含格式和样式
3. JSON - 适用于程序对接
请告诉我您需要的格式和数据范围。`,
  };

  // Task-specific responses for AI assistant with task context
  const taskNameMatch = message.match(/「([^」]+)」/);
  const taskName = taskNameMatch ? taskNameMatch[1] : '';
  if (taskName) {
    const taskRelatedResponse = generateTaskContextResponse(taskName, message);
    if (taskRelatedResponse) {
      return taskRelatedResponse;
    }
  }

  for (const [key, response] of Object.entries(responses)) {
    if (message.includes(key)) {
      return {
        reply: response,
        suggestions: Object.keys(responses).filter(k => k !== key),
      };
    }
  }

  return {
    reply: `您好！我是数字员工小智，可以帮您：
- 查进度：查询月账处理进度
- 看告警：查看当前告警信息
- 问任务：了解任务运行状态
- 导数据：导出各类数据报表
请问有什么可以帮您的？`,
    suggestions: ['查进度', '看告警', '问任务', '导数据'],
  };
}

function generateTaskContextResponse(taskName: string, message: string): { reply: string; suggestions: string[] } | null {
  // Simulate task-specific AI response based on known tasks
  const taskResponses: Record<string, string> = {
    '上游依赖有哪些': '以下是该任务的上游依赖关系：\n\n📋 **上游依赖列表：**\n  - TASK_A（数据采集）— ✅ 已完成\n  - TASK_B（数据清洗）— ✅ 已完成\n  - TASK_C（数据加工）— ⏳ 运行中\n\n📊 **依赖链路图：**\n  源系统 → 采集(TASK_A) → 清洗(TASK_B) → 加工(TASK_C) → 当前任务\n\n💡 **建议：** 如果该任务发生阻塞，建议先检查 TASK_C 的状态，它是最近的直接上游。',
    '影响范围': '该任务的影响范围如下：\n\n🔍 **直接影响：**\n  - 下游 3 个任务将等待此任务完成后才能执行\n  - 涉及 5 张数据表的更新\n\n📈 **业务影响：**\n  - 应收模块报表延迟约 2 小时\n  - 经营分析数据不可用\n\n🔄 **级联影响：**\n  该任务延迟 1 小时 → 下游任务整体延迟约 2.5 小时',
    '进度': `任务「${taskName}」的当前进度为 65%，预计还需 45 分钟完成。\n\n已完成步骤：\n  ✅ 数据获取 — 100%\n  ✅ 数据校验 — 100%\n  🔄 数据加工 — 60%\n  ⏳ 结果输出 — 0%\n\n⏰ 预计完成时间：${dayjs().add(45, 'minute').format('HH:mm')}`,
    '预计完成': `任务「${taskName}」预计在 ${dayjs().add(45, 'minute').format('HH:mm')} 前完成。当前进度 65%，剩余 2 个处理步骤。`,
  };

  for (const [keyword, response] of Object.entries(taskResponses)) {
    if (message.includes(keyword)) {
      return { reply: response, suggestions: Object.keys(taskResponses).filter(k => k !== keyword) };
    }
  }

  // Generic fallback for unrecognized task queries
  return {
    reply: `关于任务「${taskName}」，我可以帮您查询以下信息：\n\n1️⃣ **上游依赖** — 查看该任务依赖哪些前置任务及其状态\n2️⃣ **影响范围** — 了解该任务延迟会影响哪些下游\n3️⃣ **当前进度** — 查看任务执行进度和预计完成时间\n4️⃣ **任务详情** — 查看任务的完整配置和历史运行记录\n5️⃣ **异常排查** — 分析任务失败或异常的原因\n\n请问您想了解哪方面的信息？`,
    suggestions: ['上游依赖有哪些', '影响范围有多大', '当前进度如何', '预计完成时间'],
  };
}

function generateSessions() {
  return list(5, (i) => ({
    session_id: `SESS_${String(i + 1).padStart(4, '0')}`,
    title: i === 0 ? '当前对话' : `${pick(['月账进度咨询', '告警处理', '数据分析', '任务调度', '报表查询'])}`,
    created_at: dayjs().subtract(i * 2, 'hour').format('YYYY-MM-DD HH:mm:ss'),
    status: i === 0 ? 'active' : 'archived',
  }));
}

function generateChatMessages(sessionId: string) {
  return [
    {
      message_id: 'MSG_0001',
      session_id: sessionId,
      role: 'user' as const,
      content: '你好，请问当前月账处理进度如何？',
      message_type: 'text',
      created_at: dayjs().subtract(10, 'minute').format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      message_id: 'MSG_0002',
      session_id: sessionId,
      role: 'assistant' as const,
      content: '当前月账处理进度为 78.5%，已完成 85 个任务中的 67 个。预计完成时间：2026-05-15。各阶段进度如下：\n- 数据采集：100% ✅\n- 数据清洗：95%\n- 数据加工：82%\n- 数据稽核：65%\n- 报表生成：45%',
      message_type: 'text',
      created_at: dayjs().subtract(9, 'minute').format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      message_id: 'MSG_0003',
      session_id: sessionId,
      role: 'user' as const,
      content: '有哪些告警需要关注？',
      message_type: 'text',
      created_at: dayjs().subtract(5, 'minute').format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      message_id: 'MSG_0004',
      session_id: sessionId,
      role: 'assistant' as const,
      content: '当前有 12 条未处理告警，其中严重级别 3 条，警告级别 5 条，提示级别 4 条。最紧急的告警是「收入异常波动」，来自稽核任务 TASK_0005。',
      message_type: 'text',
      created_at: dayjs().subtract(4, 'minute').format('YYYY-MM-DD HH:mm:ss'),
    },
  ];
}

// ===== Settings Mock Data =====
function generateTools() {
  return list(8, (i) => ({
    tool_id: `TOOL_${String(i + 1).padStart(4, '0')}`,
    tool_name: pick(['数据采集器', '清洗引擎', '稽核引擎', '分析引擎', '报表生成器', '告警推送', '数据导出', '调度器']),
    tool_code: `TOOL_${String(i + 1).padStart(4, '0')}`,
    description: `用于${pick(['数据采集', '数据清洗', '数据稽核', '数据分析', '报表生成', '告警推送', '数据导出', '任务调度'])}的自动化工具`,
    status: pick(['active', 'active', 'active', 'inactive']),
  }));
}

function generatePrompts() {
  return list(6, (i) => ({
    prompt_id: `PROMPT_${String(i + 1).padStart(4, '0')}`,
    prompt_name: pick(['问题分析提示词', '根因推断提示词', '方案推荐提示词', '报告生成提示词', '对话摘要提示词', '规则生成提示词']),
    prompt_type: pick(['analysis', 'generation', 'summary', 'chat']),
    content: '你是一个数据运维专家，请根据以下信息' + pick(['分析问题原因', '生成解决方案', '生成分析报告', '总结对话内容', '生成稽核规则']) + '。\n\n上下文信息：\n{context}\n\n请给出专业的分析和建议。',
    status: pick(['active', 'active', 'draft']),
  }));
}

function generateUsers() {
  const roles = ['admin', 'operator', 'viewer', 'analyst'];
  return list(10, (i) => ({
    user_id: `USER_${String(i + 1).padStart(4, '0')}`,
    username: pick(['zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'sunqi', 'zhouba', 'wujiu', 'zhengshi', 'chenyi', 'liuer']),
    real_name: pick(['张三', '李四', '王五', '赵六', '孙七', '周八', '吴九', '郑十', '陈一', '刘二']),
    email: `user${i + 1}@example.com`,
    role: pick(roles),
    status: pick(['active', 'active', 'active', 'inactive']),
  }));
}

// ===== Mock Handler =====
const handlerMap: Record<string, (method: string, params?: any) => any> = {
  // Dashboard
  'dashboard/summary': () => generateDashboardSummary(),
  'dashboard/trends': () => generateTrends(),
  'dashboard/recent-alerts': () => generateRecentAlerts(),

  // Audit - Fields
  'audit/fields': (method, params) => {
    const all = generateFields();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  },
  'audit/datasources': () => datasourceCodes.map((c) => ({ datasource_code: c, datasource_name: c.replace('DS_', '') + '数据源' })),
  'audit/schemas': () => schemaCodes.map((c) => ({ schema_code: c, schema_name: c.replace('SCHEMA_', '') })),
  'audit/tables': () => tableNames.map((c) => ({ table_code: c, table_name: c.replace('T_', '') + '表' })),
  'audit/fields-by-table': () => fieldNames.map((f, i) => ({ field_code: 'COL_' + String(i + 1).padStart(3, '0'), field_name: f, data_type: 'string' })),

  // Audit - Rules
  'audit/rules': (method, params) => {
    if (method === 'post') return { rule_id: 'RULE_' + String(rand(1, 9999)).padStart(4, '0'), ...params };
    const all = generateRules();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  },
  'audit/rules/ai-generate': (method, params) => {
    if (method === 'post') return { generate_id: 'GEN_' + String(rand(1, 999)).padStart(4, '0'), status: 'processing' };
    return { status: 'completed', rules: generateRules().slice(0, 5) };
  },
  'audit/rules/batch-confirm': () => ({ success: true, confirmed_count: rand(1, 10) }),

  // Audit - Tasks
  'audit/tasks': (method, params) => {
    if (method === 'post') return { task_id: 'TASK_' + String(rand(1, 9999)).padStart(4, '0'), ...params };
    const all = generateTasks();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  },

  // Audit - Alerts
  'audit/alerts': (method, params) => {
    const all = generateAlerts();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    let filtered = all;
    if (params?.status) filtered = filtered.filter((a) => a.status === params.status);
    if (params?.alert_level) filtered = filtered.filter((a) => a.alert_level === params.alert_level);
    return { items: filtered.slice(start, start + pageSize), total: filtered.length, page, page_size: pageSize };
  },

  // Audit - Results
  'audit/results/statistics': () => generateResultStats(),
  'audit/results/trend': () => generateResultStats().trend,
  'audit/results/distribution': () => generateResultStats().distribution,
  'audit/results/details': (method, params) => {
    const all = generateResultStats().detail;
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  },

  // Audit - Reports
  'audit/reports': (method, params) => {
    if (method === 'post') return { report_id: 'REP_' + String(rand(1, 9999)).padStart(4, '0'), status: 'generating' };
    return list(8, (i) => ({
      report_id: 'REP_' + String(i + 1).padStart(4, '0'),
      report_name: dayjs().format('YYYY-MM') + ['稽核月报', '质量月报', '问题汇总报告', '整改跟踪报告'][i % 4],
      report_type: ['monthly', 'weekly', 'daily'][i % 3],
      status: ['draft', 'completed', 'generating'][i % 3],
      create_time: dayjs().subtract(i, 'day').format('YYYY-MM-DD HH:mm:ss'),
    }));
  },


  // Audit - Importance & Upgrade
  'audit/importance-configs': (method, params) => {
    if (method === 'post') return { config_id: 'IMP_' + String(rand(1, 9999)).padStart(4, '0'), ...params };
    return list(5, (i) => ({
      config_id: 'IMP_' + String(i + 1).padStart(4, '0'),
      field_code: 'COL_' + String(i + 1).padStart(3, '0'),
      field_name: fieldNames[i],
      importance_level: ['high', 'medium', 'low'][i % 3],
      weight: parseFloat((Math.random() * 0.5 + 0.1).toFixed(2)),
      status: 'active',
    }));
  },

  'audit/upgrade-rules': (method, params) => {
    if (method === 'post') return { rule_id: 'UPR_' + String(rand(1, 9999)).padStart(4, '0'), ...params };
    const all = list(8, (i) => ({
      rule_id: 'UPR_' + String(i + 1).padStart(4, '0'),
      rule_name: '升级规则-' + String(i + 1),
      trigger_condition: '连续' + String(rand(2, 5)) + '次' + ['告警', '失败', '超阈值'][i % 3],
      upgrade_action: ['升级告警级别', '通知值班人员', '触发应急流程', '暂停任务'][i % 4],
      status: ['active', 'inactive'][i % 2],
    }));
    return { items: all, total: all.length, page: 1, page_size: 20 };
  },
};


export function mockHandler(method: string, url: string, params?: any): any {
  // Normalize URL
  let normalized = url.replace(/^\/api\/v1\//, '').replace(/^\//, '');

  // Try exact match first
  if (handlerMap[normalized] !== undefined) {
    return handlerMap[normalized](method, params);
  }

  // Try pattern matching for URLs with resource IDs
  const idPatterns = [
    { prefix: 'audit/fields/', handler: () => generateFields()[0] },
    { prefix: 'audit/rules/', handler: (m: string) => {
      if (m === 'put') return { rule_id: params?.rule_id || 'RULE_0001', ...params };
      if (m === 'delete') return { success: true };
      return generateRules()[0];
    }},
    { prefix: 'audit/alerts/', handler: (m: string) => {
      if (m === 'put') return { alert_id: params?.alert_id || 'ALT_0001', status: 'processing', ...params };
      return generateAlerts()[0];
    }},
    { prefix: 'root-cause/knowledge/', handler: () => generateKnowledge()[0] },
    { prefix: 'root-cause/analysis/', handler: (m: string, p?: any) => {
      // Handle nested params from axios config
      const flatParams: any = p?.params || p || {};
      if (m === 'get' && flatParams.preset_type) {
        const preset: any = CASE_STUDIES[flatParams.preset_type as keyof typeof CASE_STUDIES];
        if (preset) return {
          record_id: 'AR_PRESET_' + flatParams.preset_type,
          ...flatParams,
          is_preset: true,
          preset_type: flatParams.preset_type,
          analysis_status: 'completed',
          analysis_logs: preset.analysis_logs,
          root_cause_result: preset.result.root_cause,
          root_cause_detail: preset.result.root_cause_detail,
          trace_path: preset.result.trace_path,
          evidence: preset.result.evidence,
          impact_assessment: preset.result.impact_assessment,
          severity: preset.result.severity,
          solution: preset.result.solution,
          prevention: preset.result.prevention,
          source_system: preset.result.source_system || '',
          source_contact: preset.result.source_contact || '',
          fake_users: preset.result.fake_users,
          risk_level: preset.result.risk_level,
          manual_time: preset.result.manual_time,
          auto_time: preset.result.auto_time,
          improvement_pct: preset.result.improvement_pct,
        };
      }
      return generateAnalysis()[0];
    } },
    { prefix: 'root-cause/cases/', handler: () => generateCases()[0] },
    { prefix: 'root-cause/suggestions/', handler: () => generateSuggestions()[0] },
    { prefix: 'root-cause/analysis-paths/', handler: () => generateAnalysisPaths()[0] },
    { prefix: 'settings/tools/', handler: () => generateTools()[0] },
    { prefix: 'settings/prompts/', handler: () => generatePrompts()[0] },
    { prefix: 'settings/users/', handler: () => generateUsers()[0] },
    { prefix: 'config/stages/', handler: (m: string) => {
      if (m === 'put') return { stage_id: params?.stage_id || 'st_1', ...params };
      if (m === 'delete') return { success: true };
      return generateConfigStages()[0];
    }},
    { prefix: 'config/milestones/', handler: (m: string) => {
      if (m === 'put') return { milestone_id: params?.milestone_id || 'ms_1', ...params };
      if (m === 'delete') return { success: true };
      return generateConfigMilestones()[0];
    }},
    { prefix: 'config/work-plans/', handler: (m: string) => {
      if (m === 'put') return { plan_id: params?.plan_id || 'wp_1', ...params };
      if (m === 'delete') return { success: true };
      return generateConfigWorkPlans()[0];
    }},
    { prefix: 'config/tasks/', handler: (m: string) => {
      if (m === 'put') return { task_id: params?.task_id || 'tk_1', ...params };
      if (m === 'delete') return { success: true };
      return generateConfigTasks()[0];
    }},
    { prefix: 'settings/user-manage/', handler: () => generateUsers()[0] },
    { prefix: 'monthly/tasks/', handler: (m: string) => {
      if (m === 'put') return { task_id: 'OT_0001', ...params, updated: true };
      if (m === 'delete') return { success: true };
      return generateRunningTasks()[0];
    }},
    { prefix: 'monthly/reports/', handler: (m: string) => {
      if (m === 'post') return { report_id: 'RP_' + String(rand(1, 9999)).padStart(4, '0'), status: 'published' };
      return generatePublishReports()[0];
    }},
  ];

  for (const { prefix, handler: h } of idPatterns) {
    if (normalized.startsWith(prefix)) {
      return h(method, params);
    }
  }


  // Handle special action URLs
  if (normalized.includes('audit/rules/') && normalized.endsWith('/confirm')) {
    return { success: true, rule_id: 'RULE_0001', status: 'confirmed' };
  }
  if (normalized.includes('audit/rules/') && normalized.endsWith('/reject')) {
    return { success: true, rule_id: 'RULE_0001', status: 'rejected' };
  }
  if (normalized.includes('audit/tasks/') && normalized.endsWith('/execute')) {
    return { success: true, task_id: 'TASK_0001', execution_id: 'EXEC_' + String(rand(1, 9999)).padStart(4, '0') };
  }

  // Root cause - knowledge base listing
  if (normalized === 'root-cause/knowledge' || normalized.startsWith('root-cause/knowledge?')) {
    const all = generateKnowledge();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    let filtered = all;
    if (params?.category) filtered = filtered.filter((d) => d.category === params.category);
    if (params?.keyword) filtered = filtered.filter((d) => d.title.includes(params.keyword) || d.content.includes(params.keyword));
    return { items: filtered.slice(start, start + pageSize), total: filtered.length, page, page_size: pageSize };
  }

  // Root cause - analysis listing
  if (normalized === 'root-cause/analysis' || normalized.startsWith('root-cause/analysis?')) {
    if (method === 'post') {
      // Check if preset analysis is requested
      if (params?.preset_type && CASE_STUDIES[params.preset_type as keyof typeof CASE_STUDIES]) {
        const preset: any = CASE_STUDIES[params.preset_type as keyof typeof CASE_STUDIES];
        return {
          record_id: 'AR_' + String(rand(1, 9999)).padStart(4, '0'),
          ...params,
          preset_type: params.preset_type,
          is_preset: true,
          analysis_status: 'completed',
          analysis_logs: preset.analysis_logs,
          root_cause_result: preset.result.root_cause,
          root_cause_detail: preset.result.root_cause_detail,
          trace_path: preset.result.trace_path,
          evidence: preset.result.evidence,
          impact_assessment: preset.result.impact_assessment,
          severity: preset.result.severity,
          solution: preset.result.solution,
          prevention: preset.result.prevention,
          source_system: preset.result.source_system || '',
          source_contact: preset.result.source_contact || '',
          fake_users: preset.result.fake_users,
          risk_level: preset.result.risk_level,
          manual_time: preset.result.manual_time,
          auto_time: preset.result.auto_time,
          improvement_pct: preset.result.improvement_pct,
        };
      }
      return { record_id: 'AR_' + String(rand(1, 9999)).padStart(4, '0'), ...params, analysis_status: 'pending' };
    }
    const all = generateAnalysis();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Root cause - cases listing
  if (normalized === 'root-cause/cases' || normalized.startsWith('root-cause/cases?')) {
    const all = generateCases();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    let filtered = all;
    if (params?.problem_type) filtered = filtered.filter((c) => c.problem_type === params.problem_type);
    if (params?.keyword) filtered = filtered.filter((c) => c.problem_title.includes(params.keyword) || c.keywords.includes(params.keyword));
    return { items: filtered.slice(start, start + pageSize), total: filtered.length, page, page_size: pageSize };
  }

  // Root cause - suggestions listing
  if (normalized === 'root-cause/suggestions' || normalized.startsWith('root-cause/suggestions?')) {
    const all = generateSuggestions();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Root cause - lineage graph data
  if (normalized.includes('root-cause/lineage')) {
    return generateLineage();
  }

  // Root cause - analysis paths listing
  if (normalized === 'root-cause/analysis-paths' || normalized.startsWith('root-cause/analysis-paths?')) {
    const all = generateAnalysisPaths();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    let filtered = all;
    if (params?.problem_type) filtered = filtered.filter((p) => p.problem_type === params.problem_type);
    return { items: filtered.slice(start, start + pageSize), total: filtered.length, page, page_size: pageSize };
  }

  // Root cause - task list
  if (normalized === 'root-cause/task-list' || normalized.startsWith('root-cause/task-list?')) {
    const all = generateRcaTasks();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 15;
    const start = (page - 1) * pageSize;
    let filtered = all;
    if (params?.status) filtered = filtered.filter((t) => t.status === params.status);
    return { items: filtered.slice(start, start + pageSize), total: filtered.length, page, page_size: pageSize };
  }


  // Config - stages
  if (normalized === 'config/stages' || normalized.startsWith('config/stages?')) {
    if (method === 'post') return { stage_id: 'st_' + String(rand(1, 999)), ...params };
    if (method === 'put') return { stage_id: params?.stage_id || 'st_1', ...params };
    if (method === 'delete') return { success: true };
    return { items: generateConfigStages(), total: configStages.length, page: 1, page_size: 20 };
  }

  // Config - milestones
  if (normalized === 'config/milestones' || normalized.startsWith('config/milestones?')) {
    if (method === 'post') return { milestone_id: 'ms_' + String(rand(1, 999)), ...params };
    if (method === 'put') return { milestone_id: params?.milestone_id || 'ms_1', ...params };
    if (method === 'delete') return { success: true };
    const all = generateConfigMilestones();
    let filtered = all;
    if (params?.stage_id) filtered = filtered.filter((m) => m.stage_id === params.stage_id);
    return { items: filtered, total: filtered.length, page: 1, page_size: 20 };
  }

  // Config - work plans
  if (normalized === 'config/work-plans' || normalized.startsWith('config/work-plans?')) {
    if (method === 'post') return { plan_id: 'wp_' + String(rand(1, 999)), ...params };
    if (method === 'put') return { plan_id: params?.plan_id || 'wp_1', ...params };
    if (method === 'delete') return { success: true };
    const all = generateConfigWorkPlans(params);
    return { items: all, total: all.length, page: 1, page_size: 20 };
  }

  // Config - tasks
  if (normalized === 'config/tasks' || normalized.startsWith('config/tasks?')) {
    if (method === 'post') return { task_id: 'tk_' + String(rand(1, 999)), ...params };
    if (method === 'put') return { task_id: params?.task_id || 'tk_1', ...params };
    if (method === 'delete') return { success: true };
    const all = generateConfigTasks(params);
    return { items: all, total: all.length, page: 1, page_size: 20 };
  }

  // Config - parse template
  if (normalized.includes('config/parse-template')) {
    if (method === 'post') {
      return { tasks: parseTemplateMock(params?.template || '') };
    }
    return { tasks: [] };
  }

  // Monthly - ledger overview (四级层次展示)
  if (normalized.includes('monthly/ledger/overview')) {
    return generateLedgerOverview();
  }

  // Monthly - progress
  if (normalized.includes('monthly/progress')) {
    return generateProgress();
  }

  // Monthly - milestones
  if (normalized.includes('monthly/milestones')) {
    return { items: generateMilestones(), total: 8, page: 1, page_size: 20 };
  }

  // Monthly - running tasks
  if (normalized.includes('monthly/running-tasks')) {
    return { items: generateRunningTasks(), total: 12, page: 1, page_size: 20 };
  }

  // Monthly - tasks listing
  if (normalized === 'monthly/tasks' || normalized.startsWith('monthly/tasks?')) {
    const all = generateRunningTasks();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Monthly - orchestration
  if (normalized.includes('monthly/orchestration')) {
    const tasks = generateOrchestrationTasks();
    const nodes = tasks.map((t: any) => ({ id: t.task_id, name: t.task_name }));
    const edges = tasks.filter((t: any) => t.dependencies.length > 0).map((t: any) => ({ source: t.dependencies[0], target: t.task_id }));
    return { tasks, dag: { nodes, edges } };
  }

  // Monthly - daily report
  if (normalized.includes('monthly/daily-report')) {
    const reports = generateDailyReports();
    return { items: reports, total: reports.length, page: 1, page_size: 20 };
  }

  // Monthly - reports publish
  if (normalized.includes('monthly/reports')) {
    const all = generatePublishReports();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Assistant - sessions
  if (normalized.includes('assistant/sessions')) {
    return { items: generateSessions(), total: 5, page: 1, page_size: 20 };
  }

  // Assistant - chat
  if (normalized.includes('assistant/chat')) {
    if (method === 'post') {
      const userMsg = params?.message || params?.content || '';
      return generateAssistantResponse(userMsg);
    }
    const sessionId = params?.session_id || 'SESS_0001';
    return { items: generateChatMessages(sessionId), total: 4, page: 1, page_size: 20 };
  }

  // Settings - tools
  if (normalized.includes('settings/tools')) {
    const all = generateTools();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Settings - prompts
  if (normalized.includes('settings/prompts')) {
    const all = generatePrompts();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Settings - users
  if (normalized.includes('settings/users') || normalized.includes('settings/user-manage')) {
    const all = generateUsers();
    const page = params?.page || 1;
    const pageSize = params?.page_size || 10;
    const start = (page - 1) * pageSize;
    return { items: all.slice(start, start + pageSize), total: all.length, page, page_size: pageSize };
  }

  // Not found
  return null;
}
