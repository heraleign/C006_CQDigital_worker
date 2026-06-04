# 数据运维数字员工 (DQ Digital Worker)

数据质量稽核、根因分析、月账监控一体化运维平台。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Ant Design 5 + ECharts 5 + Zustand + Vite 5 |
| 后端 | Python 3.11+ + FastAPI + SQLAlchemy 2.0 + Pydantic 2 |
| 数据库 | MySQL 8.0 (SQLAlchemy ORM) |
| 缓存/队列 | Redis + Celery |
| AI | OpenAI 兼容 API (可配置，无 Key 时自动降级为 Mock) |

## 快速开始

### 前置条件

- Node.js >= 18
- Python >= 3.11
- MySQL 8.0 + Redis (可选，Mock 模式无需)

### 后端

```bash
cd backend

# 创建并激活虚拟环境
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动 (数据库模式，需建表并导入种子数据)
USE_MOCK=false uvicorn app.main:app --reload --port 8000

# 启动 (Mock 模式，无需数据库)
# USE_MOCK=true uvicorn app.main:app --reload --port 8000
```

### 种子数据（数据库模式）

```bash
cd backend
PYTHONPATH=. python -m app.seeds.seed_all          # 全量 45 张表
PYTHONPATH=. python -m app.seeds.seed_root_cause    # 仅根因分析 3 张表
PYTHONPATH=. python -m app.seeds.seed_reports       # 仅报表发布 2 张表

# 数据质量稽核专用种子（8 张 dq_* 表，20+15+8+5+5+25+40+5 条数据）
PYTHONPATH=. python scripts/seed_audit_data.py
```

### 前端

```bash
cd frontend
npm install
npm run dev        # 开发模式 (热更新)
npm run build      # 生产构建 (输出到 dist/)
```

访问 http://localhost:5173

## 运行模式

两套独立 Mock 机制，可独立开关：

| 模式 | 前端 `.env` | 后端 `.env` | 效果 |
|------|------------|------------|------|
| 全 Mock | `VITE_USE_MOCK=true` | `USE_MOCK=true` | 无需任何后端服务 |
| 前端 Mock + 后端真实 | `VITE_USE_MOCK=true` | `USE_MOCK=false` | 前端自生成数据 |
| 全真实 | `VITE_USE_MOCK=false` | `USE_MOCK=false` | 需 MySQL 和种子数据 |
| 混合 | `VITE_USE_MOCK=false` | `USE_MOCK=true` | 后端 Mock 数据服务 |

> **注意**: 前端 Mock 和后端 Mock 是独立的。`VITE_USE_MOCK=true` 时前端不调后端 API。
> AI 功能在 `USE_MOCK=true` 或 API Key 无效时自动降级为 Mock 响应（5s 超时 fallback）。

## 项目结构

```
digital-worker/
├── backend/
│   └── app/
│       ├── api/v1/           # REST API 路由 (dashboard/audit/root-cause/monthly/settings)
│       ├── models/           # SQLAlchemy ORM 模型 (45 表)
│       ├── schemas/          # Pydantic 请求/响应校验
│       ├── services/         # 业务逻辑层
│       │   ├── mock_data.py      # 后端 Mock 数据生成器
│       │   ├── database_service.py  # 数据库查询服务
│       │   ├── root_cause_service.py # 根因分析服务
│       │   ├── ai_service.py       # AI 服务 (OpenAI + Mock 降级)
│       │   └── ...
│       ├── tasks/            # Celery 异步任务
│       ├── utils/            # 工具 (统一响应/认证/日志)
│       └── seeds/            # 种子数据脚本
│           ├── seed_all.py           # 全量种子
│           ├── seed_root_cause.py    # 根因分析专用 (35+18+12 条)
│           ├── seed_reports.py       # 报表发布专用
│           └── seed_billing_tasks.py # 月账任务专用
├── frontend/
│   └── src/
│       ├── pages/            # 页面组件 (19 页)
│       │   ├── RootCause/        # 根因分析 (4 页)
│       │   │   ├── Analysis.tsx       # 智能分析 (一键演示)
│       │   │   ├── KnowledgeBase.tsx  # 知识库管理
│       │   │   ├── TaskList.tsx       # 任务列表
│       │   │   ├── CaseLibrary.tsx    # 案例库
│       │   │   └── Suggestions.tsx    # 改进建议
│       │   ├── Audit/            # 数据稽核 (5 页)
│       │   ├── Monthly/          # 月账监控 (7 页)
│       │   └── ...
│       ├── components/       # 公共组件
│       ├── services/         # API 服务 + 前端 Mock
│       ├── stores/           # Zustand 状态管理
│       └── types/            # TypeScript 类型定义
└── docs/
    └── db_schema.sql         # 数据库建表脚本
```

## 模块

| 模块 | 英文标识 | 说明 |
|------|---------|------|
| 数据稽核 | DQ-AI | 字段配置/规则生成/执行审计/告警管理/结果查看 |
| 根因分析 | RCA-AI | 智能分析/知识库管理/血缘关系/任务诊断/案例库/改进建议 |
| 月账监控 | MA-AI | 账期配置/任务监控/进度甘特图/日报/报表发布 |
| 平台设置 | Platform | 工具配置/Prompt 管理/用户管理/通知管理 |

## 根因分析模块 (RCA-AI) 功能详解

### 1. 智能分析 — 一键演示

两个预设场景，点击即展示完整的 7 步根因分析动画：

| 场景 | 触发方式 | 分析链路 |
|------|---------|---------|
| **任务延期分析** | 点击"场景一"卡片 | 任务状态 → 上游依赖 → 递归追溯 → 错误定位 → 文件检查 → 根因确认 → 报告生成 |
| **指标波动分析** | 点击"场景二"卡片 | 意图识别 → 数据校验 → 多维度下钻 → 规则验证 → 根因定位 → 报告推送 |

非预设场景可自定义问题描述，后端 AI 服务自动分析（API Key 无效时 Mock 降级）。

### 2. 知识库管理

三个数据维度：

| 维度 | 数据库表 | 数据量 | 内容 |
|------|---------|:------:|------|
| 运维知识 | `ops_problem_case` | 18 条 | 话单延迟/数据质量/系统故障/业务异常等真实电信案例 |
| 血缘关系 | `ops_task_lineage` | 35 条 | 计费/CRM/订单/收入 ETL 任务的完整 DAG |
| 分析路径 | `ops_analysis_path` | 12 条×7 步 | 数据延迟/质量/系统故障/业务异常等逐层排查方法论 |

API 输出已自动转换字段名（`case_title`→`title`、`description`→`content` 等），前端直接消费。

### 3. 任务列表

24 条电信运维任务，支持状态筛选：

- **failed/delayed** 状态任务 → 显示红色"根因诊断"按钮 → 调用预设分析
- **completed/running** 状态任务 → 显示蓝色"AI 咨询"按钮 → 唤起 AI 助手

### 4. 预设分析 API

后端 `POST /api/v1/root-cause/analysis` 检测 `preset_type` 参数：

```json
{"preset_type": "task_delay"}
// 或
{"preset_type": "metric_anomaly"}
```

直接返回完整分析结果（7 步日志 + 根因/溯源/证据/方案/预防），零 AI 调用耗时。

### 5. 种子数据

```bash
# 根因分析 3 张表 — 电信业务真实数据
PYTHONPATH=. python -m app.seeds.seed_root_cause

# 输出示例:
#   ops_task_lineage:   35 rows
#   ops_problem_case:   18 rows
#   ops_analysis_path:  12 rows
```

## Bug Fixes 记录

| 问题 | 根因 | 修复 |
|------|------|------|
| 一键演示超时 30s | AI 调用 httpx timeout=60s > 前端 axios timeout=30s，Mock fallback 赶不上 | AI 超时降至 5s ([ai_service.py](backend/app/services/ai_service.py)) |
| 一键演示 422 | `analysis_id: int` 无法解析字符串 `AR_PRESET_*` | 改为 `analysis_id: str`，支持预设 ID ([root_cause.py](backend/app/api/v1/root_cause.py)) |
| 预设数据空 | 后端无 `preset_type` 检测，返回空模型 | 新增 `_PRESETS` 字典，匹配 `preset_type` 直接返回富数据 ([root_cause.py](backend/app/api/v1/root_cause.py)) |
| 知识库数据为空 | 种子数据仅 10 条通用内容，前后端字段不匹配 | 新增 35+18+12 条电信数据 + API 字段转换层 ([seed_root_cause.py](backend/app/seeds/seed_root_cause.py)) |
| 任务列表为空 | 后端缺少 `/task-list` 路由 | 新增 24 条任务 API ([root_cause.py](backend/app/api/v1/root_cause.py)) |

## 环境变量

`backend/.env`:

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MYSQL_HOST` | localhost | 数据库地址 |
| `MYSQL_PORT` | 3306 | 数据库端口 |
| `MYSQL_USER` | root | 数据库用户 |
| `MYSQL_PASSWORD` | 123456 | 数据库密码 |
| `MYSQL_DATABASE` | db_digital_worker | 数据库名 |
| `USE_MOCK` | false | 后端 Mock 模式开关 |
| `AI_ENDPOINT` | https://api.openai.com/v1 | AI API 地址 |
| `AI_MODEL` | gpt-4 | AI 模型名 |
| `AI_API_KEY` | sk-your-key-here | AI API Key (无效时自动 Mock) |

`frontend/.env`:

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_USE_MOCK` | false | 前端 Mock 模式开关 |
| `VITE_API_BASE_URL` | /api/v1 | API 基础路径 |
