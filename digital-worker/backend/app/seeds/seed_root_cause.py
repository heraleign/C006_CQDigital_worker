#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seed root_cause tables with rich telecom business data."""
import json, random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.root_cause import OpsTaskLineage, OpsProblemCase, OpsAnalysisPath

random.seed(42)
NOW = datetime.now()

DEPT_NAMES = ['数据管理部','技术研发部','业务运营部','质量监控部','财务结算部','运维保障部']
OWNERS = ['张三','李四','王五','赵六','陈七','周八']

# =======================================================================
# Task Lineage Data - 35 telecom tasks with full DAG
# =======================================================================
LINEAGE_DATA = [
    ('ETL_BILL_001', '计费系统原始话单采集', 'etl', 'DS_BILL_RAW', 'DS_ODS', [], [{"code": "ETL_BILL_002", "name": "ETL BILL 002"}, {"code": "DQC_BILL_001", "name": "DQC BILL 001"}], '赵六', '数据管理部', '计费系统原始话单采集-电信数据ETL任务', 'hourly'),
    ('ETL_BILL_002', '计费话单数据清洗', 'etl', 'DS_ODS', 'DS_DWD', [{"code": "ETL_BILL_001", "name": "ETL BILL 001"}], [{"code": "DQC_BILL_001", "name": "DQC BILL 001"}, {"code": "ETL_BILL_003", "name": "ETL BILL 003"}], '赵六', '数据管理部', '计费话单数据清洗-电信数据ETL任务', 'daily'),
    ('ETL_BILL_003', '计费批价处理', 'etl', 'DS_DWD', 'DS_DWS', [{"code": "ETL_BILL_002", "name": "ETL BILL 002"}, {"code": "DQC_BILL_001", "name": "DQC BILL 001"}], [{"code": "RPT_BILL_001", "name": "RPT BILL 001"}, {"code": "ETL_BILL_004", "name": "ETL BILL 004"}], '张三', '数据管理部', '计费批价处理-电信数据ETL任务', 'daily'),
    ('ETL_BILL_004', '账单数据生成', 'etl', 'DS_DWS', 'DS_BILL_ADS', [{"code": "ETL_BILL_003", "name": "ETL BILL 003"}], [{"code": "RPT_BILL_001", "name": "RPT BILL 001"}, {"code": "SYNC_BILL_001", "name": "SYNC BILL 001"}], '张三', '数据管理部', '账单数据生成-电信数据ETL任务', 'daily'),
    ('DQC_BILL_001', '计费数据质量检查', 'dqc', 'DS_ODS', 'DS_DWD', [{"code": "ETL_BILL_001", "name": "ETL BILL 001"}, {"code": "ETL_BILL_002", "name": "ETL BILL 002"}], [{"code": "ETL_BILL_003", "name": "ETL BILL 003"}], '王五', '数据管理部', '计费数据质量检查-电信数据ETL任务', 'daily'),
    ('ETL_CRM_001', 'CRM客户数据抽取', 'etl', 'DS_CRM_RAW', 'DS_ODS', [], [{"code": "ETL_CRM_002", "name": "ETL CRM 002"}, {"code": "DQC_CRM_001", "name": "DQC CRM 001"}], '李四', '数据管理部', 'CRM客户数据抽取-电信数据ETL任务', 'hourly'),
    ('ETL_CRM_002', '客户信息数据清洗', 'etl', 'DS_ODS', 'DS_DWD', [{"code": "ETL_CRM_001", "name": "ETL CRM 001"}], [{"code": "ETL_CRM_003", "name": "ETL CRM 003"}, {"code": "DQC_CRM_001", "name": "DQC CRM 001"}], '李四', '数据管理部', '客户信息数据清洗-电信数据ETL任务', 'daily'),
    ('ETL_CRM_003', '客户标签计算', 'etl', 'DS_DWD', 'DS_DWS', [{"code": "ETL_CRM_002", "name": "ETL CRM 002"}, {"code": "DQC_CRM_001", "name": "DQC CRM 001"}], [{"code": "RPT_CRM_001", "name": "RPT CRM 001"}, {"code": "SYNC_CRM_001", "name": "SYNC CRM 001"}], '王五', '数据管理部', '客户标签计算-电信数据ETL任务', 'daily'),
    ('DQC_CRM_001', '客户数据质量检查', 'dqc', 'DS_DWD', 'DS_DWD', [{"code": "ETL_CRM_001", "name": "ETL CRM 001"}, {"code": "ETL_CRM_002", "name": "ETL CRM 002"}], [{"code": "ETL_CRM_003", "name": "ETL CRM 003"}], '王五', '数据管理部', '客户数据质量检查-电信数据ETL任务', 'daily'),
    ('RPT_CRM_001', '客户分析报表', 'report', 'DS_DWS', 'DS_RPT', [{"code": "ETL_CRM_003", "name": "ETL CRM 003"}], [], '李四', '数据管理部', '客户分析报表-电信数据ETL任务', 'weekly'),
    ('ETL_ORD_001', '订单数据采集', 'etl', 'DS_ORD_RAW', 'DS_ODS', [], [{"code": "ETL_ORD_002", "name": "ETL ORD 002"}, {"code": "DQC_ORD_001", "name": "DQC ORD 001"}], '陈七', '数据管理部', '订单数据采集-电信数据ETL任务', 'hourly'),
    ('ETL_ORD_002', '订单数据清洗与转换', 'etl', 'DS_ODS', 'DS_DWD', [{"code": "ETL_ORD_001", "name": "ETL ORD 001"}], [{"code": "ETL_ORD_003", "name": "ETL ORD 003"}, {"code": "DQC_ORD_001", "name": "DQC ORD 001"}], '陈七', '数据管理部', '订单数据清洗与转换-电信数据ETL任务', 'daily'),
    ('ETL_ORD_003', '订单状态计算', 'etl', 'DS_DWD', 'DS_DWS', [{"code": "ETL_ORD_002", "name": "ETL ORD 002"}, {"code": "DQC_ORD_001", "name": "DQC ORD 001"}], [{"code": "RPT_ORD_001", "name": "RPT ORD 001"}, {"code": "SYNC_ORD_001", "name": "SYNC ORD 001"}], '陈七', '数据管理部', '订单状态计算-电信数据ETL任务', 'daily'),
    ('DQC_ORD_001', '订单数据质量检查', 'dqc', 'DS_DWD', 'DS_DWD', [{"code": "ETL_ORD_001", "name": "ETL ORD 001"}, {"code": "ETL_ORD_002", "name": "ETL ORD 002"}], [{"code": "ETL_ORD_003", "name": "ETL ORD 003"}], '王五', '数据管理部', '订单数据质量检查-电信数据ETL任务', 'daily'),
    ('RPT_ORD_001', '订单分析报表', 'report', 'DS_DWS', 'DS_RPT', [{"code": "ETL_ORD_003", "name": "ETL ORD 003"}], [], '陈七', '数据管理部', '订单分析报表-电信数据ETL任务', 'daily'),
    ('ETL_INC_001', '收入数据采集', 'etl', 'DS_INC_RAW', 'DS_ODS', [], [{"code": "ETL_INC_002", "name": "ETL INC 002"}, {"code": "DQC_INC_001", "name": "DQC INC 001"}], '张三', '数据管理部', '收入数据采集-电信数据ETL任务', 'hourly'),
    ('ETL_INC_002', '收入数据清洗', 'etl', 'DS_ODS', 'DS_DWD', [{"code": "ETL_INC_001", "name": "ETL INC 001"}], [{"code": "ETL_INC_003", "name": "ETL INC 003"}, {"code": "ETL_INC_004", "name": "ETL INC 004"}, {"code": "DQC_INC_001", "name": "DQC INC 001"}], '张三', '数据管理部', '收入数据清洗-电信数据ETL任务', 'daily'),
    ('ETL_INC_003', '实收数据计算', 'etl', 'DS_DWD', 'DS_DWS', [{"code": "ETL_INC_002", "name": "ETL INC 002"}, {"code": "DQC_INC_001", "name": "DQC INC 001"}], [{"code": "RPT_INC_001", "name": "RPT INC 001"}, {"code": "SYNC_INC_001", "name": "SYNC INC 001"}], '张三', '数据管理部', '实收数据计算-电信数据ETL任务', 'daily'),
    ('ETL_INC_004', '应收数据计算', 'etl', 'DS_DWD', 'DS_DWS', [{"code": "ETL_INC_002", "name": "ETL INC 002"}, {"code": "ETL_BILL_003", "name": "ETL BILL 003"}], [{"code": "RPT_REC_001", "name": "RPT REC 001"}, {"code": "SYNC_REC_001", "name": "SYNC REC 001"}], '李四', '数据管理部', '应收数据计算-电信数据ETL任务', 'daily'),
    ('DQC_INC_001', '收入数据质量检查', 'dqc', 'DS_DWD', 'DS_DWD', [{"code": "ETL_INC_001", "name": "ETL INC 001"}, {"code": "ETL_INC_002", "name": "ETL INC 002"}], [{"code": "ETL_INC_003", "name": "ETL INC 003"}, {"code": "ETL_INC_004", "name": "ETL INC 004"}], '王五', '数据管理部', '收入数据质量检查-电信数据ETL任务', 'daily'),
    ('RPT_BILL_001', '账单汇总报表生成', 'report', 'DS_BILL_ADS', 'DS_RPT', [{"code": "ETL_BILL_003", "name": "ETL BILL 003"}, {"code": "ETL_BILL_004", "name": "ETL BILL 004"}], [{"code": "SYNC_GRP_001", "name": "SYNC GRP 001"}], '张三', '数据管理部', '账单汇总报表生成-电信数据ETL任务', 'daily'),
    ('RPT_INC_001', '收入分析报表', 'report', 'DS_DWS', 'DS_RPT', [{"code": "ETL_INC_003", "name": "ETL INC 003"}], [], '李四', '数据管理部', '收入分析报表-电信数据ETL任务', 'daily'),
    ('RPT_REC_001', '应收分析报表', 'report', 'DS_DWS', 'DS_RPT', [{"code": "ETL_INC_004", "name": "ETL INC 004"}], [], '李四', '数据管理部', '应收分析报表-电信数据ETL任务', 'daily'),
    ('SYNC_BILL_001', '账单数据同步至BOSS', 'sync', 'DS_BILL_ADS', 'DS_BOSS', [{"code": "ETL_BILL_004", "name": "ETL BILL 004"}], [], '赵六', '数据管理部', '账单数据同步至BOSS-电信数据ETL任务', 'daily'),
    ('SYNC_CRM_001', '客户数据同步至CRM', 'sync', 'DS_DWS', 'DS_CRM', [{"code": "ETL_CRM_003", "name": "ETL CRM 003"}], [], '李四', '数据管理部', '客户数据同步至CRM-电信数据ETL任务', 'daily'),
    ('SYNC_ORD_001', '订单数据同步至订单中心', 'sync', 'DS_DWS', 'DS_ORD', [{"code": "ETL_ORD_003", "name": "ETL ORD 003"}], [], '陈七', '数据管理部', '订单数据同步至订单中心-电信数据ETL任务', 'daily'),
    ('SYNC_INC_001', '实收数据同步至财务', 'sync', 'DS_DWS', 'DS_FIN', [{"code": "ETL_INC_003", "name": "ETL INC 003"}], [], '张三', '数据管理部', '实收数据同步至财务-电信数据ETL任务', 'daily'),
    ('SYNC_REC_001', '应收数据同步至财务', 'sync', 'DS_DWS', 'DS_FIN', [{"code": "ETL_INC_004", "name": "ETL INC 004"}], [], '李四', '数据管理部', '应收数据同步至财务-电信数据ETL任务', 'daily'),
    ('SYNC_GRP_001', '集团报表数据上传', 'sync', 'DS_RPT', 'DS_GRP', [{"code": "RPT_BILL_001", "name": "RPT BILL 001"}, {"code": "RPT_INC_001", "name": "RPT INC 001"}, {"code": "RPT_REC_001", "name": "RPT REC 001"}], [], '赵六', '数据管理部', '集团报表数据上传-电信数据ETL任务', 'monthly'),
    ('API_BILL_001', '账单查询接口', 'api', 'DS_BILL_ADS', 'DS_BILL_ADS', [{"code": "ETL_BILL_004", "name": "ETL BILL 004"}], [], '赵六', '数据管理部', '账单查询接口-电信数据ETL任务', 'realtime'),
    ('API_CRM_001', '客户信息查询接口', 'api', 'DS_DWD', 'DS_DWD', [{"code": "ETL_CRM_002", "name": "ETL CRM 002"}], [], '李四', '数据管理部', '客户信息查询接口-电信数据ETL任务', 'realtime'),
    ('ARC_BILL_001', '账单数据归档', 'archive', 'DS_BILL_ADS', 'DS_ARCHIVE', [{"code": "ETL_BILL_004", "name": "ETL BILL 004"}], [], '赵六', '数据管理部', '账单数据归档-电信数据ETL任务', 'monthly'),
    ('ARC_INC_001', '收入数据归档', 'archive', 'DS_DWS', 'DS_ARCHIVE', [{"code": "ETL_INC_003", "name": "ETL INC 003"}, {"code": "ETL_INC_004", "name": "ETL INC 004"}], [], '张三', '数据管理部', '收入数据归档-电信数据ETL任务', 'monthly'),
    ('DQC_CROSS_001', '业财数据交叉校验', 'dqc', 'DS_DWS', 'DS_DWS', [{"code": "ETL_INC_003", "name": "ETL INC 003"}, {"code": "ETL_INC_004", "name": "ETL INC 004"}, {"code": "ETL_BILL_003", "name": "ETL BILL 003"}], [{"code": "RPT_REC_001", "name": "RPT REC 001"}], '王五', '数据管理部', '业财数据交叉校验-电信数据ETL任务', 'daily'),
    ('DQC_CROSS_002', '客户订单交叉校验', 'dqc', 'DS_DWS', 'DS_DWS', [{"code": "ETL_CRM_003", "name": "ETL CRM 003"}, {"code": "ETL_ORD_003", "name": "ETL ORD 003"}], [{"code": "RPT_CRM_001", "name": "RPT CRM 001"}], '王五', '数据管理部', '客户订单交叉校验-电信数据ETL任务', 'daily'),
]

# =======================================================================
# Problem Cases Data - 18 telecom operations cases
# =======================================================================
CASES_DATA = [
    ("某省4G话单采集延迟导致出账推迟", "data_delay", "auto", "critical", "某省分公司4G话单数据采集任务延迟2.5小时导致出账推迟1.5小时。影响全省1200万用户。", "影响全省1200万用户", "上游网元接口大量超时导致采集线程池耗尽", "增加接口超时时间,线程池扩容50%,添加熔断降级", "多系统依赖场景下单接口抖动会级联放大", ["数据延迟", "话单采集"], "ETL_BILL_001", ["t_bill_detail", "t_charge_record"], "赵六", "运维保障部", 150),
    ("收入月账1号批次延迟4小时", "data_delay", "manual", "high", "收入月账1号批次数据采集延迟4小时,原定凌晨2点启动的任务直到早上6点才完成。", "影响月账整体进度", "月末数据量突增40%,调度资源估算不足", "动态调整采集资源,建立数据量预警机制", "账期切换日需提前评估数据量变化趋势", ["数据延迟", "月账"], "ETL_INC_001", ["t_charge_record"], "张三", "财务结算部", 240),
    ("CRM客户数据日同步延迟3小时", "data_delay", "auto", "medium", "CRM客户数据日间增量同步任务连续3天延迟完成。", "影响客户标签计算", "CRM源端表新增分区,同步工具未更新分区键", "更新同步工具分区配置,添加分区变更自动感知", "源端表结构变更需及时通知下游", ["数据延迟", "CRM"], "SYNC_CRM_001", ["t_customer_info"], "李四", "业务运营部", 180),
    ("省际数据同步延迟导致集团报表异常", "data_delay", "auto", "high", "省公司与集团间数据同步链路延迟超5小时,导致集团报表数据不完整。", "影响集团级经营决策", "跨省网络链路带宽瓶颈,未启用数据压缩", "启用数据压缩传输,优化为增量+压缩模式", "跨地域数据传输必须默认启用压缩", ["数据延迟", "跨省传输"], "SYNC_GRP_001", ["t_operation_log"], "赵六", "运维保障部", 300),
    ("客户信息表20%记录缺少手机号", "data_quality", "auto", "high", "客户信息表约20%记录缺少手机号字段,影响精准营销触达率。", "约300万用户无法接收营销短信", "CRM接口升版后手机号字段映射失败", "修正字段映射配置,补充离线修复脚本,添加空值校验", "接口变更必须有完善的兼容性测试", ["数据质量", "缺失"], "ETL_CRM_001", ["t_customer_info"], "李四", "业务运营部", 480),
    ("账单金额与计费汇总偏差0.35%", "data_quality", "auto", "critical", "财务对账发现账单金额与计费系统偏差0.35%,涉及金额约350万元。", "财务月报无法出具", "分布式事务部分失败未回滚重试", "引入可靠消息事务,建立日对账+自动修复流程", "资金相关数据链路必须满足最终一致性", ["数据质量", "计费"], "DQC_CROSS_001", ["t_bill_detail", "t_charge_record"], "王五", "财务结算部", 600),
    ("订单状态5%卡在待支付超48小时", "data_quality", "auto", "high", "5%订单在待支付状态停留超48小时,正常应在2小时内完成支付或取消。", "影响5万笔订单闭环", "支付回调接口高峰期超时,未做补偿查询", "优化回调接口性能,添加补偿扫描任务,引入消息队列", "关键状态流转必须有补偿机制", ["数据质量", "订单"], "ETL_ORD_003", ["t_order_main"], "陈七", "业务运营部", 360),
    ("套餐变更后计费未切换导致多扣费", "data_quality", "manual", "high", "套餐变更后账单仍按原套餐计费,约8000名用户多扣费约32万元。", "引发用户投诉升级", "变更数据同步链路延迟,未在账期切换前完成同步", "优化为实时+补偿双重机制,出账前增加一致性校验", "计费配置变更必须确保账期切换前完成同步", ["数据质量", "套餐"], "SYNC_BILL_001", ["t_product_def", "t_package_def"], "赵六", "财务结算部", 480),
    ("产品实例表数据重复60%", "data_quality", "auto", "medium", "集团上传产品实例表发现大量重复记录,去重后仅为上传量的60%。", "下游报表数据膨胀失真", "上游系统未设置数据幂等性约束", "上游添加幂等性校验,下游增加去重处理", "跨系统数据交换必须约定幂等性策略", ["数据质量", "重复"], "ETL_CRM_003", ["t_product_def"], "王五", "质量监控部", 120),
    ("IDC存储故障导致历史数据丢失", "system_fault", "manual", "critical", "IDC机房磁盘阵列RAID5双盘离线,近3个月历史账单数据不可用。", "1000万用户无法查询历史账单", "RAID卡固件bug,备份系统未及时修复", "升级RAID卡固件,修复备份系统,实施异地多活", "数据安全必须遵循3-2-1原则", ["系统故障", "数据丢失"], "ARC_BILL_001", ["t_bill_detail"], "赵六", "运维保障部", 720),
    ("计费系统数据库连接池耗尽", "system_fault", "auto", "critical", "计费系统月结日并发激升,数据库连接池耗尽导致服务中断。", "月结处理中断30分钟", "连接池配置200不足,高峰并发350", "连接池扩容到500,优化回收策略,添加限流", "核心系统连接池需根据高峰流量压测评估", ["系统故障", "数据库"], "ETL_BILL_003", ["t_charge_record"], "赵六", "运维保障部", 45),
    ("调度系统OOM导致批量任务失败", "system_fault", "auto", "high", "批量调度任务凌晨出现OOM,12个采集和处理任务执行失败。", "12个任务失败,影响次日报表", "JVM堆内存4GB不足,新增3个数据源后需6GB", "JVM调整到8GB,优化内存模型,添加自动重试", "系统扩容需考虑数据增长趋势", ["系统故障", "OOM"], "ETL_BILL_001", ["t_operation_log"], "赵六", "技术研发部", 90),
    ("月末集中入账导致月账延迟6小时", "business", "auto", "high", "月末集中入账量是平日3倍,月账各环节排队积压,整体延迟6小时。", "出账时间延迟6小时", "各渠道集中入账超出日常处理能力2倍", "引导错峰入账,动态扩容,建立入账量预警", "月账处理需建立弹性资源池", ["业务异常", "月账"], "ETL_INC_001", ["t_charge_record"], "张三", "财务结算部", 360),
    ("新套餐首日订购量暴增8倍", "business", "auto", "medium", "新5G套餐首日订购量达预期8倍,系统承载超限。", "接口响应从200ms飙至5s", "系统未设计弹性扩展,数据库查询成瓶颈", "添加Redis缓存,优化索引,建立自动扩容机制", "新业务上线前需进行容量评估", ["业务异常", "套餐"], "ETL_ORD_001", ["t_product_def"], "陈七", "业务运营部", 180),
    ("集团考核口径变更导致报表偏差5%", "business", "manual", "high", "集团考核口径变更未通知数据团队,报表数据偏差5%。", "经营报表数据失准", "口径变更流程不规范", "建立口径变更标准化流程,添加版本号管理", "跨部门协作需建立明确的变更通知SLA", ["业务异常", "口径"], "RPT_BILL_001", ["t_operation_log"], "李四", "质量监控部", 240),
    ("省公司收入对账差异37万元", "business", "manual", "high", "省公司与总部收入对账发现37万元差异。", "影响收入确认和绩效考核", "科目映射表未同步更新", "统一科目映射表通过配置中心下发,建立日对账", "两级系统映射表必须通过统一配置管理", ["业务异常", "对账"], "DQC_CROSS_001", ["t_account_balance"], "张三", "财务结算部", 300),
    ("账单查询接口超时率30%", "data_delay", "auto", "critical", "账单查询API在月初出账高峰期超时率达30%。", "50万用户月初账单查询体验差", "索引碎片化,缓存命中率低", "重建索引,引入多级缓存,添加限流降级", "用户查询接口需设计多级缓存和限流策略", ["接口", "性能"], "API_BILL_001", ["t_bill_detail"], "赵六", "技术研发部", 120),
    ("订单中心接口超时链式故障", "data_delay", "auto", "high", "订单中心接口间歇性超时导致上游采集任务大面积阻塞。", "5项采集任务阻塞,数据延迟3小时", "接口未设置合理超时阈值", "设置10s超时,使用异步非阻塞IO,添加熔断器", "系统间调用必须设置超时和熔断机制", ["接口", "链式故障"], "ETL_ORD_001", ["t_order_main"], "陈七", "技术研发部", 180),
]

# =======================================================================
# Analysis Paths Data - 12 path templates with detailed steps
# =======================================================================

# =======================================================================
# Analysis Paths Data - 12 path templates with detailed steps
# =======================================================================
PATHS_DATA = [
    ("数据延迟根因分析流程", "data_delay", "适用于计费数据延迟、月账延迟、同步延迟等场景", [{"order": 1, "name": "确认延迟范围和影响", "method": "metric_check"}, {"order": 2, "name": "检查上游数据就绪状态", "method": "check_upstream"}, {"order": 3, "name": "检查任务调度执行日志", "method": "log_analyzer"}, {"order": 4, "name": "检查数据量异常波动", "method": "volume_compare"}, {"order": 5, "name": "检查系统资源使用率", "method": "resource_monitor"}, {"order": 6, "name": "检查网络和接口延迟", "method": "network_diagnose"}, {"order": 7, "name": "定位根因并启动恢复", "method": "root_cause_fix"}], 60, 0.85),
    ("数据质量异常排查流程", "data_quality", "适用于数据缺失、重复、不一致、格式错误等质量问题", [{"order": 1, "name": "确认异常数据类型和范围", "method": "anomaly_scope"}, {"order": 2, "name": "数据完整性检查", "method": "check_completeness"}, {"order": 3, "name": "数据准确性校验", "method": "check_accuracy"}, {"order": 4, "name": "数据一致性对比", "method": "check_consistency"}, {"order": 5, "name": "数据时效性检查", "method": "check_timeliness"}, {"order": 6, "name": "源端数据溯源分析", "method": "data_trace"}, {"order": 7, "name": "制定修复方案并执行", "method": "data_repair"}], 90, 0.78),
    ("系统故障定位流程", "system", "适用于服务不可用、OOM、连接池耗尽、硬件故障", [{"order": 1, "name": "确认故障现象和影响面", "method": "fault_scope"}, {"order": 2, "name": "检查系统资源使用率", "method": "check_sys_resource"}, {"order": 3, "name": "分析应用错误日志", "method": "check_app_log"}, {"order": 4, "name": "检查数据库连接和慢查询", "method": "check_db_conn"}, {"order": 5, "name": "检查网络连通性和延迟", "method": "check_network"}, {"order": 6, "name": "检查依赖中间件状态", "method": "check_middleware"}, {"order": 7, "name": "确定根因并执行恢复", "method": "sys_recovery"}], 45, 0.82),
    ("业务异常分析流程", "business", "适用于收入波动、对账差异、套餐异常、口径变更", [{"order": 1, "name": "确认业务异常指标", "method": "biz_metric_verify"}, {"order": 2, "name": "同环比数据对比分析", "method": "trend_analysis"}, {"order": 3, "name": "数据源交叉验证", "method": "cross_source_verify"}, {"order": 4, "name": "关联业务系统排查", "method": "related_biz_check"}, {"order": 5, "name": "核对最近配置变更", "method": "config_change_audit"}, {"order": 6, "name": "定位根因并制定方案", "method": "biz_root_cause"}, {"order": 7, "name": "执行修复并验证效果", "method": "biz_fix_verify"}], 120, 0.75),
    ("计费异常排查流程", "data_delay", "适用于计费批价异常、账单数据错误、出账延迟", [{"order": 1, "name": "检查计费数据采集状态", "method": "check_bill_collect"}, {"order": 2, "name": "检查批价处理结果", "method": "check_pricing"}, {"order": 3, "name": "检查账期切换状态", "method": "check_account_period"}, {"order": 4, "name": "检查出账文件生成情况", "method": "check_output_file"}, {"order": 5, "name": "比对上月同期数据量", "method": "volume_mom_compare"}, {"order": 6, "name": "检查计费规则配置变更", "method": "check_biz_rule_change"}, {"order": 7, "name": "执行重批或补偿处理", "method": "rerun_pricing"}], 90, 0.8),
    ("收入波动分析流程", "business", "适用于收入数据异常波动、ARPU异常、入账异常", [{"order": 1, "name": "确认收入波动幅度", "method": "revenue_volatility"}, {"order": 2, "name": "按业务类型拆解收入", "method": "revenue_by_biz"}, {"order": 3, "name": "按渠道维度拆解收入", "method": "revenue_by_channel"}, {"order": 4, "name": "按地域维度拆解收入", "method": "revenue_by_region"}, {"order": 5, "name": "对比上月和去年同期", "method": "mom_yoy_compare"}, {"order": 6, "name": "关联营销活动分析", "method": "campaign_correlation"}, {"order": 7, "name": "输出收入波动根因报告", "method": "revenue_report"}], 60, 0.88),
    ("用户数据异常排查流程", "data_quality", "适用于用户信息缺失、异常增长/流失、标签异常", [{"order": 1, "name": "确认用户数据异常范围", "method": "user_anomaly_scope"}, {"order": 2, "name": "检查CRM数据同步链路", "method": "check_crm_sync"}, {"order": 3, "name": "检查用户数据完整性", "method": "check_user_completeness"}, {"order": 4, "name": "检查用户标签计算逻辑", "method": "check_user_tag_logic"}, {"order": 5, "name": "对比多源用户数据", "method": "cross_source_user_check"}, {"order": 6, "name": "定位数据异常根因", "method": "user_rca"}, {"order": 7, "name": "执行数据修复和补偿", "method": "user_data_repair"}], 45, 0.82),
    ("ETL任务失败排查流程", "data_delay", "适用于ETL抽取、清洗、加载任务执行失败或超时", [{"order": 1, "name": "确认失败任务范围和影响", "method": "failed_task_scope"}, {"order": 2, "name": "查看任务错误日志", "method": "check_task_log"}, {"order": 3, "name": "检查上游数据源可用性", "method": "check_upstream_source"}, {"order": 4, "name": "检查依赖任务执行状态", "method": "check_dependency"}, {"order": 5, "name": "检查系统资源使用情况", "method": "check_task_resource"}, {"order": 6, "name": "检查数据量变化情况", "method": "check_data_volume_change"}, {"order": 7, "name": "手动触发重跑并监控", "method": "rerun_task"}], 30, 0.9),
    ("数据对账差异排查流程", "data_quality", "适用于业财对账、营收对账、省-总部对账", [{"order": 1, "name": "确认对账差异金额和范围", "method": "diff_scope"}, {"order": 2, "name": "按科目维度拆解差异", "method": "diff_by_subject"}, {"order": 3, "name": "按时间维度拆解差异", "method": "diff_by_time"}, {"order": 4, "name": "核对双方案务处理逻辑", "method": "check_both_accounting"}, {"order": 5, "name": "检查映射表和规则配置", "method": "check_mapping_config"}, {"order": 6, "name": "逐笔比对差异明细", "method": "line_by_line_compare"}, {"order": 7, "name": "生成对账差异报告", "method": "diff_report"}], 120, 0.72),
    ("接口性能排查流程", "data_delay", "适用于API响应超时、吞吐量下降、连接池耗尽", [{"order": 1, "name": "确认接口性能下降指标", "method": "perf_metric_check"}, {"order": 2, "name": "检查CPU和内存使用率", "method": "check_cpu_mem"}, {"order": 3, "name": "检查数据库慢查询", "method": "check_slow_query"}, {"order": 4, "name": "检查缓存命中率", "method": "check_cache_hit"}, {"order": 5, "name": "检查线程池和连接池状态", "method": "check_thread_pool"}, {"order": 6, "name": "检查网络延迟和带宽", "method": "check_network_perf"}, {"order": 7, "name": "输出优化建议并执行", "method": "perf_optimize"}], 45, 0.85),
    ("跨系统数据同步排查流程", "data_delay", "适用于跨数据中心、跨省、跨系统数据同步延迟或失败", [{"order": 1, "name": "确认同步延迟时长和范围", "method": "sync_delay_scope"}, {"order": 2, "name": "检查源端数据变更日志", "method": "check_source_change_log"}, {"order": 3, "name": "检查同步工具运行状态", "method": "check_sync_tool"}, {"order": 4, "name": "检查网络带宽和延迟", "method": "check_network_bandwidth"}, {"order": 5, "name": "检查目标端写入性能", "method": "check_target_write_perf"}, {"order": 6, "name": "检查数据压缩传输配置", "method": "check_compress_config"}, {"order": 7, "name": "调整同步策略并恢复", "method": "sync_recovery"}], 60, 0.83),
    ("月账异常处理流程", "business", "适用于月账进度异常、批次处理失败、出账异常", [{"order": 1, "name": "确认异常批次和作业类型", "method": "check_batch_status"}, {"order": 2, "name": "检查前置作业完成情况", "method": "check_pre_task"}, {"order": 3, "name": "检查用户数据波动审核", "method": "check_user_volatility"}, {"order": 4, "name": "检查实收作业执行状态", "method": "check_income_task"}, {"order": 5, "name": "检查应收作业执行状态", "method": "check_rec_task"}, {"order": 6, "name": "检查集团数据同步状态", "method": "check_grp_sync"}, {"order": 7, "name": "评估影响并调整出账计划", "method": "adjust_schedule"}], 90, 0.8),
]



def seed():
    engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in ["ops_task_lineage","ops_problem_case","ops_analysis_path"]:
            db.execute(text(f"DELETE FROM {t}"))
        db.commit()
        print("Cleared existing root_cause data.")

        print("Seeding ops_task_lineage (35 tasks)...")
        import random as rnd
        for code, name, typ, inp, out, ups, downs, owner, dept, desc, sched in LINEAGE_DATA:
            db.add(OpsTaskLineage(
                task_code=code, task_name=name, task_type=typ,
                upstream_tasks=ups, downstream_tasks=downs,
                datasource_input=inp, datasource_output=out,
                schedule_type=sched, owner=owner, department=dept,
                description=desc, status=1, created_at=NOW, updated_at=NOW,
            ))
        db.flush()
        print("  Lineage committed.")

        print("Seeding ops_problem_case (18 cases)...")
        for title, ctype, source, severity, desc, impact, root_cause, sol, lessons, tags, task_code, tables, handler, dept, duration in CASES_DATA:
            occur_time = NOW - timedelta(hours=rnd.randint(1, 720))
            resolve_time = occur_time + timedelta(minutes=duration)
            db.add(OpsProblemCase(
                case_title=title, case_type=ctype, case_source=source,
                status="closed", severity=severity,
                description=desc, impact_range=impact, root_cause=root_cause,
                solution=sol, lessons_learned=lessons, tags=tags,
                related_task_code=task_code, related_tables=tables,
                handler=handler, handler_department=dept,
                occurrence_time=occur_time, resolve_time=resolve_time,
                resolution_duration=duration, is_template=False,
                usage_count=rnd.randint(1,200), rating=round(rnd.uniform(3.5,5.0),1),
                created_by="system", created_at=NOW, updated_at=NOW,
            ))
        db.flush()
        print("  Cases committed.")

        print("Seeding ops_analysis_path (12 paths)...")
        for name, ptype, scenarios, steps, duration, rate in PATHS_DATA:
            db.add(OpsAnalysisPath(
                path_name=name, path_type=ptype, steps=steps,
                applicable_scenarios=scenarios, expected_duration=duration,
                success_rate=rate, usage_count=rnd.randint(10,500),
                status=1, created_by="system", created_at=NOW, updated_at=NOW,
            ))
        db.flush()
        print("  Paths committed.")

        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()
        print("Root cause tables seeded successfully!")
        cnt_l = db.execute(text("SELECT COUNT(*) FROM ops_task_lineage")).scalar()
        cnt_c = db.execute(text("SELECT COUNT(*) FROM ops_problem_case")).scalar()
        cnt_p = db.execute(text("SELECT COUNT(*) FROM ops_analysis_path")).scalar()
        print(f"  ops_task_lineage: {cnt_l} rows")
        print(f"  ops_problem_case: {cnt_c} rows")
        print(f"  ops_analysis_path: {cnt_p} rows")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback; traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()

