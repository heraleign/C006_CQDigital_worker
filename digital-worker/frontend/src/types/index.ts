// ===== Common =====
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface OptionType {
  label: string;
  value: string;
}

// ===== Audit =====
export interface FieldConfig {
  config_id: string;
  datasource_code: string;
  schema_code: string;
  table_code: string;
  field_code: string;
  field_name: string;
  audit_type: string;
  status_cd: string;
  create_time: string;
}

export interface RuleConfig {
  rule_id: string;
  config_id: string;
  rule_name: string;
  rule_type: string;
  threshold_upper: number;
  threshold_lower: number;
  alert_level: string;
  status_cd: string;
  create_time: string;
}

export interface AuditTask {
  task_id: string;
  task_name: string;
  schedule_type: string;
  rule_ids: string[];
  last_run_status: string;
  status_cd: string;
}

export interface AuditAlert {
  alert_id: string;
  alert_level: string;
  title: string;
  source_task: string;
  status: string;
  create_time: string;
}

export interface AuditResult {
  execution_id: string;
  task_id: string;
  acct_date: string;
  check_result: string;
  alert_level: string;
  deviation_rate: number;
}

// ===== Root Cause =====
export interface KnowledgeDoc {
  doc_id: string;
  title: string;
  category: string;
  content: string;
  tags: string[];
  create_time: string;
}

export interface AnalysisRecord {
  record_id: string;
  problem_description: string;
  problem_type: string;
  analysis_status: string;
  root_cause_result: string;
  create_time: string;
}

export interface ProblemCase {
  case_id: string;
  problem_type: string;
  problem_title: string;
  problem_feature: string;
  root_cause: string;
  solution: string;
  keywords: string;
  effectiveness_score: number;
  use_count: number;
}

export interface LineageNode {
  id: string;
  name: string;
  type: string;
}

export interface LineageEdge {
  source: string;
  target: string;
  relation: string;
}

export interface AnalysisPath {
  path_id: string;
  problem_type: string;
  step_order: number;
  step_name: string;
  tool_code: string;
}

export interface Suggestion {
  id: string;
  title: string;
  priority: string;
  status: string;
  content: string;
  expected_benefit: string;
  source_analysis: string;
}

// ===== Monthly =====
export interface MonthlyProgress {
  acct_month: string;
  total_tasks: number;
  completed_tasks: number;
  progress_pct: number;
  estimated_completion: string;
  status: string;
}

export interface Milestone {
  milestone_id: string;
  milestone_name: string;
  target_time: string;
  actual_time: string;
  status: string;
  delay_minutes: number;
}

export interface TaskMonitor {
  task_id: string;
  task_code: string;
  task_name: string;
  stage: string;
  status: string;
  start_time: string;
  duration: number;
  progress_pct: number;
}

export interface DailyReport {
  report_id: string;
  acct_month: string;
  report_date: string;
  title: string;
  content: any;
  status: string;
}

export interface OrchestrationTask {
  task_id: string;
  task_code: string;
  task_name: string;
  stage: string;
  dependencies: string[];
  estimated_duration: number;
}

export interface ReportPublish {
  report_id: string;
  report_name: string;
  category: string;
  platform: string;
  plan_time: string;
  status: string;
}

// ===== Assistant =====
export interface ChatSession {
  session_id: string;
  title: string;
  created_at: string;
  status: string;
}

export interface ChatMessage {
  message_id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_type: string;
  created_at: string;
}

// ===== Dashboard =====
export interface DashboardSummary {
  total_tasks: number;
  running_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  alert_count: number;
  quality_score: number;
  progress_pct: number;
}

export interface TrendItem {
  date: string;
  value: number;
  category: string;
}

// ===== Settings =====
export interface ToolItem {
  tool_id: string;
  tool_name: string;
  tool_code: string;
  description: string;
  category?: string;
  method?: string;
  priority?: string;
  status: string;
  hermes_registered?: boolean;
}

export interface PromptTemplate {
  prompt_id: string;
  prompt_name: string;
  prompt_type: string;
  content: string;
  status: string;
}

export interface SysUser {
  user_id: string;
  username: string;
  real_name: string;
  email: string;
  role: string;
  status: string;
}
