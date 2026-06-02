# -*- coding: utf-8 -*-
path = r'e:\project\ClaudeCodeWs\C006_CQDigital_worker\运维数字员工产品设计-汇总.md'

part2 = """

## 二、技术栈约定

### 2.1 总体架构：前后端分离

```
+------------------------------------------------------------------+
|                        前端 (Frontend)                            |
|     React 18 + TypeScript + Ant Design 5 + ECharts               |
|     Vite 构建工具                                                |
+------------------------------------------------------------------+
|                        API Gateway                               |
|                  Nginx / Traefik 反向代理                         |
+------------------------------------------------------------------+
|                        后端 (Backend)                             |
|     Python 3.11 + FastAPI + SQLAlchemy 2.0 + Celery              |
|     OpenAI兼容接口（可配置endpoint/model/api_key）                |
+------------------------------------------------------------------+
|                         数据库                                    |
|     MySQL 8.0 (主存储)                                           |
|     Redis 7.0+ (缓存/分布式锁)                                   |
+------------------------------------------------------------------+
|                        环境管理                                   |
|     Python venv (后端虚拟环境)                                    |
|     npm (前端包管理)                                             |
|     pip (后端包管理)                                             |
|     Docker Compose (基础服务)                                    |
+------------------------------------------------------------------+
```

### 2.2 详细技术选型

| 层级 | 技术组件 | 版本 | 用途 |
|-----|---------|------|------|
| 前端框架 | React | 18.x | UI框架 |
| 前端语言 | TypeScript | 5.x | 类型安全 |
| UI组件库 | Ant Design | 5.x | 企业级UI |
| 数据可视化 | ECharts | 5.x | 图表展示 |
| 状态管理 | Zustand | 4.x | 轻量状态管理 |
| HTTP客户端 | Axios | 1.x | API请求 |
| 路由 | React Router | 6.x | 前端路由 |
| 构建工具 | Vite | 5.x | 构建打包 |
| 后端框架 | FastAPI | 0.110+ | RESTful API |
| ORM | SQLAlchemy | 2.0+ | 数据库ORM |
| 异步任务 | Celery | 5.3+ | 异步/定时任务 |
| 消息队列 | Redis/RabbitMQ | - | Celery Broker |
| AI集成 | OpenAI SDK | 1.x | 大模型调用 |
| 数据校验 | Pydantic | 2.x | 请求/响应校验 |
| 数据库 | MySQL | 8.0 | 持久化存储 |
| 缓存 | Redis | 7.0+ | 缓存/Session |

---

## 三、项目目录结构

```
digital-worker/
├── README.md
├── docker-compose.yml              # MySQL + Redis 基础服务
├── .env.example                    # 环境变量模板
│
├── backend/
│   ├── requirements.txt
│   ├── .env
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── config.py               # 配置管理
│   │   ├── database.py             # 数据库连接
│   │   ├── models/                 # SQLAlchemy ORM模型
│   │   │   ├── __init__.py
│   │   │   ├── audit.py
│   │   │   ├── root_cause.py
│   │   │   ├── monthly.py
│   │   │   ├── system.py
│   │   │   └── assistant.py
│   │   ├── schemas/                # Pydantic请求/响应
│   │   ├── api/                    # 路由层
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audit.py
│   │   │   │   ├── root_cause.py
│   │   │   │   ├── monthly.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── system.py
│   │   │   │   └── assistant.py
│   │   │   └── router.py
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── audit_service.py
│   │   │   ├── root_cause_service.py
│   │   │   ├── monthly_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── ai_service.py       # AI调用
│   │   │   ├── knowledge_service.py
│   │   │   └── assistant_service.py
│   │   ├── tasks/                  # Celery异步任务
│   │   ├── utils/                  # 工具函数
│   │   └── seeds/                  # 种子数据
│   └── migrations/                 # Alembic迁移
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── .env
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── routes/
│       │   └── index.tsx
│       ├── layouts/
│       │   ├── MainLayout.tsx
│       │   ├── Sidebar.tsx
│       │   ├── Header.tsx
│       │   └── AssistantDrawer.tsx
│       ├── pages/
│       │   ├── Dashboard/
│       │   ├── Audit/              # 数据质量稽核
│       │   ├── RootCause/          # 根因分析
│       │   ├── Monthly/            # 月账管理
│       │   └── Settings/           # 系统设置
│       ├── components/             # 公共组件
│       │   ├── MetricCard/
│       │   ├── StatusTag/
│       │   ├── ProgressTimeline/
│       │   ├── LineageGraph/
│       │   ├── ChatWindow/
│       │   └── AIChatBox/
│       ├── services/               # API调用层
│       ├── stores/                 # Zustand状态
│       ├── hooks/                  # 自定义Hook
│       ├── types/                  # TS类型定义
│       └── styles/
```

with open(path, 'a', encoding='utf-8') as f:
    f.write(part2)

print('Part 2 done')
