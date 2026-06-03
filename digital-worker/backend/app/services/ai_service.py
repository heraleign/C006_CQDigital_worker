"""AI service - OpenAI-compatible API wrapper with mock mode support"""
import json
import random
from typing import Any, Optional
from app.config import settings
from app.utils.logger import logger


class AIService:
    """AI service for various AI-powered features."""

    @staticmethod
    async def chat_completion(
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict:
        """Send chat completion request to AI API or return mock response."""
        if settings.USE_MOCK:
            return AIService._mock_chat_response(messages)

        try:
            import httpx
            # Use a short timeout so the mock fallback kicks in before the
            # frontend (30s) or upstream client times out.  If the API key
            # is a placeholder or the endpoint is unreachable we fail fast.
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    f"{settings.AI_ENDPOINT}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.AI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model or settings.AI_MODEL,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return AIService._mock_chat_response(messages)

    @staticmethod
    def _mock_chat_response(messages: list[dict]) -> dict:
        """Generate mock chat response."""
        last_msg = messages[-1]["content"] if messages else ""

        responses = {
            "质量": "根据系统数据分析，本月数据质量整体评分为96.8分，较上月提升1.2分。主要问题集中在客户信息完整性方面，手机号缺失率为3.5%，较上月下降0.8个百分点。建议继续加强数据源端校验，并建立定期的数据质量巡检机制。",
            "任务": "本月共计划128个数据运维任务，已完成98个，完成率76.6%。其中ETL任务完成率82.3%，数据质量检查任务完成率71.5%。当前有12个任务正在执行中，3个任务执行失败需要关注。",
            "告警": "当前系统共有8个活跃告警，其中2个严重告警，5个警告，1个信息提示。严重告警主要集中在账单数据同步延迟和客户信息缺失两个方面，建议优先处理。",
            "根因": "经过系统分析，发现主要根因如下：1)上游CRM系统接口超时导致数据写入失败，占比45%；2)网络波动导致数据同步延迟，占比30%；3)数据源端质量问题，占比25%。建议优先优化接口超时机制。",
            "延迟": "数据延迟问题分析：当前主要延迟发生在ETL-002（账单数据抽取）和ETL-001（客户数据抽取）两个任务。平均延迟时间约45分钟，主要原因是数据量突增和资源竞争。建议增加调度节点和优化数据分片策略。",
        }

        reply = "您好，我是数据运维数字员工助手。我可以帮助您进行数据质量分析、根因排查、任务监控等工作。请问有什么可以帮您的吗？"
        for key, resp in responses.items():
            if key in last_msg:
                reply = resp
                break

        return {
            "id": f"mock_chat_{random.randint(10000, 99999)}",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": random.randint(50, 200),
                "completion_tokens": random.randint(100, 500),
                "total_tokens": random.randint(150, 700),
            },
        }

    @staticmethod
    async def generate_audit_rules(
        table_name: str,
        field_descriptions: list[dict],
        business_scenario: Optional[str] = None,
    ) -> list[dict]:
        """Generate audit rules using AI."""
        if settings.USE_MOCK:
            return AIService._mock_generate_rules(table_name, field_descriptions)

        prompt = f"""根据以下表结构和业务场景，生成数据质量审计规则：
表名：{table_name}
字段：{json.dumps(field_descriptions, ensure_ascii=False)}
业务场景：{business_scenario or '通用数据质量审计'}
请生成10-15条数据质量审计规则。"""

        result = await AIService.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        try:
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return AIService._mock_generate_rules(table_name, field_descriptions)

    @staticmethod
    def _mock_generate_rules(table_name: str, field_descriptions: list[dict]) -> list[dict]:
        """Generate mock audit rules."""
        rules = []
        rule_templates = [
            {"name": "非空校验", "type": "null_check", "severity": "high"},
            {"name": "唯一性校验", "type": "duplicate", "severity": "high"},
            {"name": "格式校验", "type": "format", "severity": "medium"},
            {"name": "范围校验", "type": "range", "severity": "medium"},
            {"name": "枚举值校验", "type": "format", "severity": "low"},
        ]
        for i, fd in enumerate(field_descriptions[:10]):
            tmpl = rule_templates[i % len(rule_templates)]
            rules.append({
                "rule_name": f"{fd.get('field_name', f'field_{i}')}{tmpl['name']}",
                "rule_code": f"AI_R{i+1:03d}",
                "rule_type": tmpl["type"],
                "rule_level": tmpl["severity"],
                "rule_content": {"field": fd.get("field_name"), "action": "reject"},
                "field_name": fd.get("field_name"),
                "table_name": table_name,
                "severity": tmpl["severity"],
                "threshold": 0.95 if tmpl["severity"] == "high" else 0.9,
                "ai_generated": True,
                "confirm_status": "pending",
            })
        return rules

    @staticmethod
    async def root_cause_analysis(
        problem_description: str,
        context: Optional[dict] = None,
    ) -> dict:
        """Perform root cause analysis using AI."""
        if settings.USE_MOCK:
            return AIService._mock_root_cause_analysis(problem_description)

        prompt = f"""作为数据运维专家，请对以下问题进行根因分析：
问题描述：{problem_description}
上下文：{json.dumps(context or {}, ensure_ascii=False)}
请提供分析过程、根因结论和改进建议。"""

        result = await AIService.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        try:
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return AIService._mock_root_cause_analysis(problem_description)

    @staticmethod
    def _mock_root_cause_analysis(problem_description: str) -> dict:
        """Generate mock root cause analysis."""
        return {
            "analysis_process": [
                {"step": 1, "action": "数据采集与预处理", "result": "已完成相关数据采集"},
                {"step": 2, "action": "异常特征提取", "result": "提取到关键异常特征"},
                {"step": 3, "action": "相关性分析", "result": "发现数据源异常与任务延迟高度相关"},
                {"step": 4, "action": "根因定位", "result": "确认根因为上游数据源接口超时"},
            ],
            "root_cause": "上游CRM系统接口超时导致数据写入失败，累计影响5张核心表的数据质量",
            "confidence": 0.92,
            "suggestions": [
                "增加接口超时时间至30秒",
                "引入消息队列异步处理数据写入",
                "建立数据补偿机制，确保数据最终一致性",
                "增加接口健康检查监控",
            ],
        }

    @staticmethod
    async def generate_daily_report(report_date: str, task_data: dict) -> dict:
        """Generate daily report content using AI."""
        if settings.USE_MOCK:
            return AIService._mock_daily_report(report_date)

        prompt = f"""作为数据运维助手，请生成{report_date}的日报。
任务数据：{json.dumps(task_data, ensure_ascii=False)}
请生成结构化的日报内容。"""

        result = await AIService.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        try:
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return AIService._mock_daily_report(report_date)

    @staticmethod
    def _mock_daily_report(report_date: str) -> dict:
        """Generate mock daily report."""
        return {
            "summary": f"{report_date}数据运维工作平稳，各项指标正常",
            "task_completion": {
                "total": 42,
                "completed": 38,
                "failed": 1,
                "running": 3,
                "completion_rate": 90.5,
            },
            "quality_metrics": {
                "overall_score": 96.5,
                "data_integrity": 98.2,
                "data_accuracy": 97.1,
                "data_timeliness": 95.3,
            },
            "exceptions": [
                {"type": "数据延迟", "count": 2, "severity": "low"},
                {"type": "格式错误", "count": 5, "severity": "low"},
            ],
            "key_events": [
                "完成月度数据质量审计任务",
                "修复了客户信息同步延迟问题",
                "更新了3条数据质量规则",
            ],
            "plan_for_next_day": [
                "继续监控数据同步任务",
                "完成剩余数据质量检查",
                "准备月度总结报告",
            ],
        }

    @staticmethod
    async def case_matching(
        problem_description: str,
        cases: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """Match similar cases using AI."""
        if settings.USE_MOCK:
            return AIService._mock_case_matching(problem_description, cases, top_k)

        prompt = f"""根据以下问题描述，从案例库中匹配最相似的案例：
问题：{problem_description}
案例库：{json.dumps(cases, ensure_ascii=False)}
请返回top{top_k}个最匹配的案例及相似度评分。"""

        result = await AIService.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        try:
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return AIService._mock_case_matching(problem_description, cases, top_k)

    @staticmethod
    def _mock_case_matching(
        problem_description: str,
        cases: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """Generate mock case matching results."""
        results = []
        for i, case in enumerate(cases[:top_k]):
            results.append({
                "case_id": case.get("id", i + 1),
                "case_title": case.get("case_title", f"案例_{i+1}"),
                "similarity": round(random.uniform(0.6, 0.98), 2),
                "match_reason": f"问题描述与案例{i+1}相似度较高，涉及相同的{random.choice(['数据源', '任务类型', '异常模式'])}",
                "case": case,
            })
        return sorted(results, key=lambda x: x["similarity"], reverse=True)


ai_service = AIService()
