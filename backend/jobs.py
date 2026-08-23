from __future__ import annotations
import os
import threading
import traceback
from typing import Any, Optional

from orchestrator import build_graph

JOBS_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "jobs_data")

_jobs: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


def create_job(job_id: str) -> dict:
    job = {
        "status": "queued",         # queued | running | complete | failed
        "current_agent": None,
        "completed_agents": [],
        "kpis": {},
        "data_findings": [],
        "vision_findings": [],
        "inferences": [],
        "output_files": [],
        "error": None,
    }
    with _lock:
        _jobs[job_id] = job
    return job


def get_job(job_id: str) -> Optional[dict]:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def _update(job_id: str, **fields):
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(fields)


def job_dir(job_id: str) -> str:
    return os.path.join(JOBS_ROOT, job_id)


def run_job(job_id: str, initial_state: dict):
    """
    Runs the LangGraph pipeline for one job, streaming node-by-node updates
    into the job record so the frontend's polling picks up progress as each
    agent finishes — not just a single jump from "running" to "complete".
    """
    _update(job_id, status="running")
    try:
        graph = build_graph()
        for step in graph.stream(initial_state, config={"recursion_limit": 25}, stream_mode="updates"):
            for node_name, output in step.items():
                if node_name == "supervisor":
                    next_agent = output.get("next_agent")
                    if next_agent and next_agent != "END":
                        _update(job_id, current_agent=next_agent)
                    continue

                fields = {}
                if "completed_agents" in output:
                    fields["completed_agents"] = output["completed_agents"]
                if "kpis" in output:
                    fields["kpis"] = output["kpis"]
                if "data_findings" in output:
                    fields["data_findings"] = output["data_findings"]
                if "vision_findings" in output:
                    fields["vision_findings"] = output["vision_findings"]
                if "inferences" in output:
                    fields["inferences"] = output["inferences"]
                if "output_files" in output:
                    fields["output_files"] = [os.path.basename(p) for p in output["output_files"]]
                if fields:
                    _update(job_id, **fields)

        _update(job_id, status="complete", current_agent=None)
    except Exception as exc:  # noqa: BLE001 - report any failure to the client
        _update(
            job_id,
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
        traceback.print_exc()
