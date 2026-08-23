
from __future__ import annotations
import os

import config
from state import ReportState
from tools.llm_client import complete
from tools.pptx_builder import build_pptx
from tools.docx_builder import build_docx


def _synthesize_inferences(state: ReportState) -> list[str]:
    data_findings = state.get("data_findings", [])
    vision_findings = state.get("vision_findings", [])

    if not data_findings and not vision_findings:
        return []

    prompt = (
        "Data findings:\n" + "\n".join(f"- {f}" for f in data_findings) + "\n\n"
        "Chart/document findings:\n" + "\n".join(f"- {f}" for f in vision_findings) + "\n\n"
        "Synthesize 2-3 cross-cutting business inferences or recommendations "
        "that combine both sets of findings. Return as a short bullet list."
    )
    text = complete(
        system="You synthesize multi-source business analysis into actionable inferences.",
        prompt=prompt,
    )
    return [line.strip("- ").strip() for line in text.splitlines() if line.strip()]


def run(state: ReportState) -> dict:
    inferences = _synthesize_inferences(state)
    merged_state = {**state, "inferences": inferences}

    # Per-job callers (e.g. the FastAPI backend) pass an isolated output_dir
    # in state so concurrent requests never write to the same report.pptx;
    # the CLI (main.py) doesn't set it, so it falls back to config.OUTPUT_DIR.
    output_dir = state.get("output_dir") or config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    output_files = []

    fmt = state.get("output_template", "both")
    if fmt in ("pptx", "both"):
        path = build_pptx(merged_state, os.path.join(output_dir, "report.pptx"))
        output_files.append(path)
    if fmt in ("docx", "both"):
        path = build_docx(merged_state, os.path.join(output_dir, "report.docx"))
        output_files.append(path)

    return {
        "inferences": inferences,
        "output_files": output_files,
        "completed_agents": state.get("completed_agents", []) + ["generation_agent"],
    }
