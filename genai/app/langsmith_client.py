"""LangSmith API client – fetches traces, metrics, and analytics from the LangSmith API."""

import httpx
from datetime import datetime, timedelta
from app.config import LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

LANGSMITH_API = "https://api.smith.langchain.com/api/v1"
HEADERS = {"x-api-key": LANGCHAIN_API_KEY}

PUBLIC_TRACE_BASE = "https://smith.langchain.com/public"


def _get(path: str, params: dict | None = None) -> dict | list:
    """Synchronous GET against the LangSmith API."""
    with httpx.Client(timeout=15) as client:
        resp = client.get(f"{LANGSMITH_API}{path}", headers=HEADERS, params=params or {})
        resp.raise_for_status()
        return resp.json()


def _post(path: str, payload: dict) -> dict | list:
    """Synchronous POST against the LangSmith API."""
    with httpx.Client(timeout=15) as client:
        resp = client.post(f"{LANGSMITH_API}{path}", headers=HEADERS, json=payload)
        resp.raise_for_status()
        return resp.json()


# ------------------------------------------------------------------
# Project / session helpers
# ------------------------------------------------------------------

def get_project_id() -> str | None:
    """Resolve the configured project name to its LangSmith session ID."""
    sessions = _get("/sessions")
    for s in sessions:
        if s.get("name") == LANGCHAIN_PROJECT:
            return s["id"]
    return None


# ------------------------------------------------------------------
# Fetch traces (runs)
# ------------------------------------------------------------------

def fetch_traces(limit: int = 50, hours_back: int = 24) -> list[dict]:
    """Return recent root-level runs from the configured project."""
    project_id = get_project_id()
    if not project_id:
        return []

    start_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat() + "Z"

    payload = {
        "session": [project_id],
        "filter": f'gte(start_time, "{start_time}")',
        "is_root": True,
        "limit": limit,
        "select": [
            "id",
            "name",
            "run_type",
            "status",
            "start_time",
            "end_time",
            "total_tokens",
            "prompt_tokens",
            "completion_tokens",
            "inputs",
            "outputs",
            "error",
            "latency",
            "feedback_stats",
            "extra",
        ],
    }
    try:
        runs = _post("/runs/query", payload)
        return runs.get("runs", runs) if isinstance(runs, dict) else runs
    except Exception:
        return []


def fetch_trace_detail(run_id: str) -> dict:
    """Fetch full detail for a single run including child steps."""
    run = _get(f"/runs/{run_id}")

    # Fetch child runs (LLM calls, retrievers, etc.)
    children_payload = {
        "filter": f'eq(parent_run_id, "{run_id}")',
        "limit": 50,
        "select": [
            "id", "name", "run_type", "status",
            "start_time", "end_time",
            "total_tokens", "prompt_tokens", "completion_tokens",
            "inputs", "outputs", "error", "extra",
        ],
    }
    try:
        children_resp = _post("/runs/query", children_payload)
        children = children_resp.get("runs", children_resp) if isinstance(children_resp, dict) else children_resp
    except Exception:
        children = []

    run["children"] = children
    return run


# ------------------------------------------------------------------
# Aggregated analytics
# ------------------------------------------------------------------

def compute_analytics(hours_back: int = 168) -> dict:
    """Compute summary analytics across all recent traces."""
    traces = fetch_traces(limit=200, hours_back=hours_back)

    if not traces:
        return {
            "total_traces": 0,
            "period_hours": hours_back,
            "message": "No traces found. Make some API calls first.",
        }

    total = len(traces)
    successes = sum(1 for t in traces if t.get("status") == "success")
    errors = sum(1 for t in traces if t.get("status") == "error")

    # Latency
    latencies = []
    for t in traces:
        start = t.get("start_time")
        end = t.get("end_time")
        if start and end:
            try:
                s = datetime.fromisoformat(start.replace("Z", "+00:00"))
                e = datetime.fromisoformat(end.replace("Z", "+00:00"))
                latencies.append((e - s).total_seconds())
            except Exception:
                pass

    # Tokens
    total_tokens_list = [t.get("total_tokens", 0) or 0 for t in traces]
    prompt_tokens_list = [t.get("prompt_tokens", 0) or 0 for t in traces]
    completion_tokens_list = [t.get("completion_tokens", 0) or 0 for t in traces]

    # Per-name breakdown
    name_stats: dict[str, dict] = {}
    for t in traces:
        name = t.get("name", "unknown")
        if name not in name_stats:
            name_stats[name] = {"count": 0, "latencies": [], "tokens": [], "errors": 0}
        name_stats[name]["count"] += 1
        if t.get("status") == "error":
            name_stats[name]["errors"] += 1
        tok = t.get("total_tokens", 0) or 0
        name_stats[name]["tokens"].append(tok)
        start = t.get("start_time")
        end = t.get("end_time")
        if start and end:
            try:
                s = datetime.fromisoformat(start.replace("Z", "+00:00"))
                e = datetime.fromisoformat(end.replace("Z", "+00:00"))
                name_stats[name]["latencies"].append((e - s).total_seconds())
            except Exception:
                pass

    endpoint_breakdown = {}
    for name, stats in name_stats.items():
        lats = stats["latencies"]
        toks = stats["tokens"]
        endpoint_breakdown[name] = {
            "count": stats["count"],
            "errors": stats["errors"],
            "avg_latency_s": round(sum(lats) / len(lats), 2) if lats else None,
            "min_latency_s": round(min(lats), 2) if lats else None,
            "max_latency_s": round(max(lats), 2) if lats else None,
            "avg_tokens": round(sum(toks) / len(toks)) if toks else 0,
            "total_tokens": sum(toks),
        }

    # Timeline data (for charts)
    timeline = []
    for t in traces:
        start = t.get("start_time")
        end = t.get("end_time")
        latency = None
        if start and end:
            try:
                s = datetime.fromisoformat(start.replace("Z", "+00:00"))
                e = datetime.fromisoformat(end.replace("Z", "+00:00"))
                latency = round((e - s).total_seconds(), 2)
            except Exception:
                pass
        timeline.append({
            "id": t.get("id"),
            "name": t.get("name", "unknown"),
            "status": t.get("status"),
            "start_time": start,
            "latency_s": latency,
            "total_tokens": t.get("total_tokens", 0) or 0,
            "prompt_tokens": t.get("prompt_tokens", 0) or 0,
            "completion_tokens": t.get("completion_tokens", 0) or 0,
        })

    return {
        "period_hours": hours_back,
        "total_traces": total,
        "successful": successes,
        "errors": errors,
        "success_rate": round(successes / total * 100, 1) if total else 0,
        "latency": {
            "avg_s": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "min_s": round(min(latencies), 2) if latencies else None,
            "max_s": round(max(latencies), 2) if latencies else None,
            "p50_s": round(sorted(latencies)[len(latencies) // 2], 2) if latencies else None,
            "p95_s": round(sorted(latencies)[int(len(latencies) * 0.95)], 2) if latencies else None,
        },
        "tokens": {
            "total": sum(total_tokens_list),
            "total_prompt": sum(prompt_tokens_list),
            "total_completion": sum(completion_tokens_list),
            "avg_per_call": round(sum(total_tokens_list) / total) if total else 0,
        },
        "endpoint_breakdown": endpoint_breakdown,
        "timeline": sorted(timeline, key=lambda x: x["start_time"] or "", reverse=True),
    }
