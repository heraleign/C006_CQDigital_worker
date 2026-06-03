"""Root cause service wrapping MockDataService."""
from typing import Any, Optional
from app.config import settings
from app.services.database_service import DatabaseService


class RootCauseService:
    """Service for root cause module operations."""

    def __init__(self):
        if not settings.USE_MOCK:
            self.mock = DatabaseService()
        else:
            from app.services.mock_data import MockDataService
            self.mock = MockDataService()
        self._cases_cache = None
        self._paths_cache = None
        self._analyses_cache = None

    @property
    def cases(self):
        if self._cases_cache is None:
            self._cases_cache = self.mock.get_problem_cases(page=1, page_size=200)["items"]
        return self._cases_cache

    @property
    def paths(self):
        if self._paths_cache is None:
            self._paths_cache = self.mock.get_analysis_paths(page=1, page_size=200)["items"]
        return self._paths_cache

    @property
    def analyses(self):
        if self._analyses_cache is None:
            self._analyses_cache = self.mock.get_root_cause_analyses(page=1, page_size=200)["items"]
        return self._analyses_cache

    def get_lineage(self, page=1, page_size=20):
        return self.mock.get_task_lineage(page, page_size)

    def get_lineage_graph(self, page=1, page_size=20):
        """Return lineage as {nodes, edges} graph format for frontend."""
        raw = self.mock.get_task_lineage(page, page_size)
        nodes = []
        edges = []
        seen = set()
        for task in raw.get("items", []):
            tid = f"task_{task['id']}"
            if tid not in seen:
                nodes.append({"id": tid, "name": task.get("task_name", ""), "type": task.get("task_type", "etl")})
                seen.add(tid)
            # upstream → task
            for up in task.get("upstream_tasks", []) or []:
                up_id = up.get("code", "") if isinstance(up, dict) else str(up)
                if up_id and up_id not in seen:
                    nodes.append({"id": up_id, "name": up.get("name", up_id) if isinstance(up, dict) else up_id, "type": "upstream"})
                    seen.add(up_id)
                if up_id:
                    edges.append({"source": up_id, "target": tid, "relation": "依赖"})
            # task → downstream
            for down in task.get("downstream_tasks", []) or []:
                down_id = down.get("code", "") if isinstance(down, dict) else str(down)
                if down_id and down_id not in seen:
                    nodes.append({"id": down_id, "name": down.get("name", down_id) if isinstance(down, dict) else down_id, "type": "downstream"})
                    seen.add(down_id)
                if down_id:
                    edges.append({"source": tid, "target": down_id, "relation": "被依赖"})
        return {"nodes": nodes, "edges": edges}

    def batch_import_lineage(self, tasks: list[dict]):
        return {"imported": len(tasks), "status": "success"}

    def get_paths(self, page=1, page_size=20):
        return self.mock.get_analysis_paths(page, page_size)

    def get_paths_flat(self, page=1, page_size=50):
        """Return analysis paths as flat rows (one row per step) for frontend."""
        raw = self.mock.get_analysis_paths(page, page_size)
        rows = []
        for path in raw.get("items", []):
            steps = path.get("steps", []) or []
            if isinstance(steps, list):
                for step in steps:
                    rows.append({
                        "path_id": str(path["id"]),
                        "problem_type": path.get("path_type", ""),
                        "step_order": step.get("order", 0),
                        "step_name": step.get("name", ""),
                        "tool_code": step.get("method", "manual_check"),
                    })
            else:
                rows.append({
                    "path_id": str(path["id"]),
                    "problem_type": path.get("path_type", ""),
                    "step_order": 1,
                    "step_name": path.get("path_name", ""),
                    "tool_code": "manual_check",
                })
        return {
            "items": rows,
            "total": len(rows),
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (len(rows) + page_size - 1) // page_size),
        }

    def get_path(self, path_id: int):
        return self.mock.get_item(self.paths, path_id)

    def create_path(self, data: dict):
        return self.mock.create_item(self.paths, data)

    def update_path(self, path_id: int, data: dict):
        return self.mock.update_item(self.paths, path_id, data)

    def delete_path(self, path_id: int):
        return self.mock.delete_item(self.paths, path_id)

    def create_analysis(self, data: dict):
        return self.mock.create_item(self.analyses, data)

    def get_analysis(self, analysis_id: int):
        return self.mock.get_item(self.analyses, analysis_id)

    def get_analysis_steps(self, analysis_id: int):
        return self.mock.get_analysis_steps(analysis_id)

    def get_analyses_records(self, page=1, page_size=20):
        return self.mock.get_root_cause_analyses(page, page_size)

    def add_feedback(self, data: dict):
        feedbacks = self.mock.get_user_feedback(page=1, page_size=200)["items"]
        return self.mock.create_item(feedbacks, data)

    def save_as_case(self, analysis_id: int):
        analysis = self.get_analysis(analysis_id)
        if analysis:
            analysis["is_saved_as_case"] = True
            return {"success": True, "case_id": analysis_id}
        return {"success": False}

    def get_knowledge(self, page=1, page_size=20, keyword=None):
        """Return cases in KnowledgeDoc format for the frontend."""
        if keyword:
            from app.services.knowledge_service import KnowledgeService
            ks = KnowledgeService()
            raw = ks.search_cases(keyword, page, page_size)
        else:
            raw = self.mock.get_problem_cases(page, page_size)
        transformed = []
        for item in raw.get("items", []):
            transformed.append({
                "doc_id": str(item.get("id", "")),
                "title": item.get("case_title", ""),
                "category": item.get("case_type", ""),
                "content": item.get("description", ""),
                "tags": item.get("tags", []),
                "create_time": item.get("created_at", ""),
            })
        return {
            "items": transformed,
            "total": raw["total"],
            "page": raw["page"],
            "page_size": raw["page_size"],
            "total_pages": raw["total_pages"],
        }

    def get_cases(self, page=1, page_size=20, **filters):
        return self.mock.get_problem_cases(page, page_size, **filters)

    def get_case(self, case_id: int):
        return self.mock.get_item(self.cases, case_id)

    def create_case(self, data: dict):
        return self.mock.create_item(self.cases, data)

    def update_case(self, case_id: int, data: dict):
        return self.mock.update_item(self.cases, case_id, data)

    def delete_case(self, case_id: int):
        return self.mock.delete_item(self.cases, case_id)

    def get_case_statistics(self):
        return self.mock.get_case_statistics()

    def match_cases(self, problem_description: str, top_k: int = 5):
        from app.services.ai_service import ai_service
        matches = ai_service._mock_case_matching(problem_description, self.cases, top_k)
        return matches

    def get_suggestions(self, page=1, page_size=20):
        return self.mock.get_suggestions(page, page_size)

    def get_suggestion_statistics(self):
        return self.mock.get_suggestion_statistics()

    def generate_suggestions(self, data: dict):
        return {"task_id": f"sug_gen_{hash(str(data)) % 10000}", "status": "completed"}

    def update_suggestion(self, suggestion_id: int, data: dict):
        suggestions = self.mock.get_suggestions(page=1, page_size=200)["items"]
        return self.mock.update_item(suggestions, suggestion_id, data)

    # ── Task List (RCA / root cause task list) ──────────────────────

    def get_task_list(self, page=1, page_size=15, status=None):
        """Return RCA task list matching the frontend TaskList format."""
        import random
        r = random.Random(42)

        task_names = [
            "集团上传产品实例表", "收入月账数据抽取", "用户打标任务", "账单数据清洗",
            "客户信息同步", "产品实例采集", "报表数据汇总", "指标计算任务",
            "数据质量稽核任务", "ETL批量导入", "CRM数据同步", "月账应收计算",
            "渠道数据归集", "费用明细对账", "账期数据归档", "经营分析报表",
            "数据备份任务", "数据迁移任务", "数据校验任务", "调度监控任务",
            "计费话单采集", "批价处理任务", "出账文件生成", "集团数据上传",
        ]
        modules = ["数据采集", "数据清洗", "数据加工", "数据稽核", "报表生成", "数据同步", "数据归档"]
        owners = ["张三", "李四", "王五", "赵六", "陈七", "周八"]
        statuses = ["running", "completed", "failed", "waiting", "pending", "delayed"]

        # Ensure some tasks are delayed/failed so the "根因诊断" button appears
        forced_statuses = [
            None, None, None, None, "delayed", "failed",
            None, None, None, None, "failed", None,
            None, None, None, None, None, "delayed",
            None, None, None, None, None, None,
        ]

        tasks = []
        from datetime import datetime, timedelta
        now = datetime.now()
        for i, name in enumerate(task_names):
            # Determine status — forced failures/delays so 根因诊断 buttons show
            fs = forced_statuses[i] if i < len(forced_statuses) else None
            if fs:
                st = fs
            else:
                st = r.choice(statuses)

            start = now - timedelta(hours=r.randint(1, 72), minutes=r.randint(0, 59))
            end = start + timedelta(hours=r.randint(1, 8), minutes=r.randint(0, 59)) if r.random() > 0.3 else None
            dur_minutes = r.randint(5, 180)
            summary = f"{dur_minutes}分钟"

            code = f"RCA_{now.strftime('%Y%m')}_{i+1:03d}"
            tid = f"TASK_{i+1:04d}"

            tasks.append({
                "task_id": tid,
                "task_code": code,
                "task_name": name,
                "status": st,
                "module": r.choice(modules),
                "owner": r.choice(owners),
                "priority": r.choice(["P0", "P1", "P2"]),
                "start_time": start.isoformat() if st != "pending" else "",
                "end_time": end.isoformat() if end and st in ("completed", "failed") else "",
                "duration": summary if st in ("completed", "failed") else "",
            })

        # Apply filter
        if status:
            tasks = [t for t in tasks if t["status"] == status]

        total = len(tasks)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": tasks[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
