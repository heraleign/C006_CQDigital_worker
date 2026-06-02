# 数据运维数字员工 (DQ Digital Worker)

数据质量稽核、根因分析、月账监控一体化运维平台。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Ant Design 5 + ECharts 5 + Zustand + Vite 5 |
| 后端 | Python 3.11+ + FastAPI + SQLAlchemy 2.0 + Pydantic 2 |
| 数据库 | MySQL 8.0 (SQLAlchemy ORM) |
| 缓存/队列 | Redis + Celery |
| AI | OpenAI 兼容 API (可配置) |

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

# 启动 (Mock 模式，无需数据库)
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## Mock 模式

默认启用 Mock 模式 (`USE_MOCK=true`)，无需数据库即可完整演示所有功能。

环境变量控制：
- 后端: `USE_MOCK=true` (`.env` 文件)
- 前端: `VITE_USE_MOCK=true` (`.env` 文件)

## 项目结构

```
digital-worker/
├── backend/
│   └── app/
│       ├── api/v1/       # REST API 路由
│       ├── models/       # SQLAlchemy 数据模型 (36 表)
│       ├── schemas/      # Pydantic 请求/响应模型
│       ├── services/     # 业务逻辑 + Mock 数据
│       ├── tasks/        # Celery 异步任务
│       ├── utils/        # 工具 (响应/认证/日志)
│       └── seeds/        # 种子数据
├── frontend/
│   └── src/
│       ├── pages/        # 19 个页面
│       ├── components/   # 公共组件
│       ├── services/     # API 服务 + Mock
│       ├── layouts/      # 布局
│       ├── stores/       # Zustand 状态管理
│       └── types/        # TypeScript 类型定义
└── docs/
```

## 模块

| 模块 | 说明 |
|---|---|
| DQ-AI | 数据质量稽核 (字段配置/规则生成/告警/结果) |
| RCA-AI | 根因分析 (知识库/分析/案例/建议) |
| MA-AI | 月账监控 (进度/编排/日报/报表) |
| Platform | 平台设置 (工具/Prompt/用户/通知) |
