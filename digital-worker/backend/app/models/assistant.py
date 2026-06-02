import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
)
from sqlalchemy.orm import relationship
from app.database import Base


class AiChatSession(Base):
    """AI对话会话"""
    __tablename__ = "ai_chat_session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_title = Column(String(200), comment="会话标题")
    session_type = Column(String(50), default="general", comment="会话类型: general/analysis/audit/report")
    user_id = Column(Integer, ForeignKey("sys_user.id"), comment="用户ID")
    user_name = Column(String(100), comment="用户名")
    context_summary = Column(Text, comment="上下文摘要")
    message_count = Column(Integer, default=0, comment="消息数量")
    status = Column(String(20), default="active", comment="状态: active/archived/deleted")
    is_pinned = Column(Boolean, default=False, comment="是否置顶")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    messages = relationship("AiChatMessage", backref="session", order_by="AiChatMessage.created_at")


class AiChatMessage(Base):
    """AI对话消息"""
    __tablename__ = "ai_chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("ai_chat_session.id"), nullable=False, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    content_type = Column(String(50), default="text", comment="内容类型: text/markdown/code/image")
    tokens_used = Column(Integer, comment="Token数量")
    ai_model = Column(String(100), comment="AI模型")
    message_metadata = Column("metadata", JSON, comment="元数据")
    feedback_score = Column(Integer, comment="反馈评分")
    created_at = Column(DateTime, default=datetime.datetime.now)


class SysAiConfig(Base):
    """AI配置"""
    __tablename__ = "sys_ai_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_name = Column(String(200), nullable=False, comment="配置名称")
    config_code = Column(String(100), unique=True, comment="配置编码")
    provider = Column(String(50), default="openai", comment="提供商: openai/azure/ollama")
    endpoint = Column(String(500), comment="API端点")
    api_key = Column(String(500), comment="API密钥(加密)")
    model_name = Column(String(100), comment="模型名称")
    parameters = Column(JSON, comment="参数配置")
    max_tokens = Column(Integer, default=4096, comment="最大Token数")
    temperature = Column(Float, default=0.7, comment="温度参数")
    context_limit = Column(Integer, default=10, comment="上下文限制(消息数)")
    is_default = Column(Boolean, default=False, comment="是否默认配置")
    status = Column(Integer, default=1)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class SysInterfaceLog(Base):
    """接口调用日志"""
    __tablename__ = "sys_interface_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interface_name = Column(String(200), comment="接口名称")
    interface_type = Column(String(50), comment="接口类型: internal/external")
    request_url = Column(String(500), comment="请求URL")
    request_method = Column(String(10), comment="请求方法")
    request_headers = Column(JSON, comment="请求头")
    request_body = Column(JSON, comment="请求体")
    response_code = Column(Integer, comment="响应码")
    response_body = Column(JSON, comment="响应体")
    duration_ms = Column(Integer, comment="耗时(毫秒)")
    caller = Column(String(100), comment="调用方")
    status = Column(String(10), default="success")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.datetime.now)


class SysJobSchedule(Base):
    """任务调度配置"""
    __tablename__ = "sys_job_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(200), nullable=False, comment="任务名称")
    job_code = Column(String(100), unique=True, comment="任务编码")
    job_type = Column(String(50), comment="任务类型: audit/monthly/system")
    trigger_type = Column(String(20), comment="触发类型: cron/interval/manual")
    trigger_config = Column(JSON, comment="触发配置")
    target_function = Column(String(200), comment="目标函数")
    parameters = Column(JSON, comment="参数")
    status = Column(Integer, default=1, comment="状态: 0禁用 1启用")
    last_run_time = Column(DateTime, comment="最后运行时间")
    last_run_result = Column(String(20), comment="最后运行结果")
    next_run_time = Column(DateTime, comment="下次运行时间")
    run_count = Column(Integer, default=0, comment="运行次数")
    fail_count = Column(Integer, default=0, comment="失败次数")
    description = Column(Text, comment="描述")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
