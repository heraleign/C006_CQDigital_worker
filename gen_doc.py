# -*- coding: utf-8 -*-
import os

path = r'e:\project\ClaudeCodeWs\C006_CQDigital_worker\运维数字员工产品设计-汇总.md'

content = """# 数据运维数字员工产品设计 - 汇总文档

> **文档说明**：本文档整合《数据运维数字员工产品功能清单》《产品设计说明书》《数据库设计》《AI智能助手》《APP端设计》五份源文档，形成完整的产品设计参考，供Claude Code进行前后端分离模式开发使用。

---

## 目录

- [一、产品概述](#一产品概述)
- [二、技术栈约定](#二技术栈约定)
- [三、项目目录结构](#三项目目录结构)
- [四、功能模块设计](#四功能模块设计)
  - [4.1 数据质量稽核数字员工](#41-数据质量稽核数字员工-dq-ai)
  - [4.2 根因分析数字员工](#42-根因分析数字员工-rca-ai)
  - [4.3 月账数字员工](#43-月账数字员工-ma-ai)
  - [4.4 AI智能助手](#44-ai智能助手)
  - [4.5 移动端APP](#45-移动端app)
- [五、数据库设计](#五数据库设计)
- [六、API接口设计](#六api接口设计)
- [七、非功能性需求](#七非功能性需求)
- [八、开发指南](#八开发指南)

---

## 一、产品概述

### 1.1 产品组成

```
数据运维数字员工
├── 数据质量稽核数字员工（DQ-AI）
│   └── 6大核心功能模块，23个功能点
├── 根因分析数字员工（RCA-AI）
│   └── 7大核心功能模块，28个功能点
├── 月账数字员工（MA-AI）
│   └── 5大核心功能模块，19个功能点
└── 公共支撑平台（含AI智能助手）
    └── 5大支撑模块 + AI助手
```

### 1.2 功能统计

| 数字员工 | 核心功能模块 | 功能点数量 | 接口数量 | 数据表数量 |
|---------|------------|-----------|---------|-----------|
| 数据质量稽核 | 6个 | 23个 | 15个 | 8个 |
| 根因分析 | 7个 | 28个 | 18个 | 12个 |
| 月账数字员工 | 5个 | 19个 | 12个 | 10个 |
| 公共支撑 | 5个 | 15个 | 10个 | 6个 |
| **合计** | **23个** | **85个** | **55个** | **36个** |

### 1.3 页面路由总览

| 路由 | 页面 | 所属模块 | 优先级 |
|-----|------|---------|--------|
| /dashboard | 总览看板 | 公共 | P0 |
| /audit/field-config | 稽核指标配置 | 数据质量稽核 | P0 |
| /audit/rule-generate | AI辅助规则生成 | 数据质量稽核 | P0 |
| /audit/rule-confirm | 规则确认与任务管理 | 数据质量稽核 | P0 |
| /audit/alert-manage | 告警分级管理 | 数据质量稽核 | P1 |
| /audit/result-view | 稽核结果运营视图 | 数据质量稽核 | P1 |
| /root-cause/knowledge-base | 知识库管理 | 根因分析 | P0 |
| /root-cause/analysis | 智能分析 | 根因分析 | P0 |
| /root-cause/case-library | 案例库管理 | 根因分析 | P0 |
| /root-cause/suggestion | 质量改进建议 | 根因分析 | P1 |
| /monthly/monitor | 月账进度监控 | 月账管理 | P0 |
| /monthly/task-orchestration | 任务编排 | 月账管理 | P0 |
| /monthly/daily-report | 出账日报 | 月账管理 | P1 |
| /monthly/report-publish | 报表发布管理 | 月账管理 | P1 |
| /settings/tools | 工具注册管理 | 系统设置 | P0 |
| /settings/prompts | Prompt模板管理 | 系统设置 | P0 |
| /settings/knowledge-base | 知识库管理 | 系统设置 | P0 |
| /settings/notifications | 通知配置 | 系统设置 | P1 |
| /settings/user-manage | 用户管理 | 系统设置 | P0 |
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Part 1 written')
