from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any


class ReportState(TypedDict, total=False):
    # ---- inputs ----
    request: str                     # natural-language user request
    data_path: Optional[str]         # path to structured data (csv)
    chart_image_paths: List[str]     # paths to chart/image files to analyze
    output_template: str             # "pptx" | "docx" | "both"
    output_dir: Optional[str]        # per-job output directory (set by API callers)

    # ---- routing ----
    plan: List[str]                  # ordered list of agent names the supervisor picked
    next_agent: Optional[str]        # what the supervisor decided to run next
    completed_agents: List[str]      # agents already executed, for routing decisions

    # ---- agent outputs ----
    kpis: Dict[str, Any]             # structured KPI output from data_analysis_agent
    data_findings: List[str]         # natural-language findings from data_analysis_agent
    vision_findings: List[str]       # natural-language findings from document_vision_agent
    extracted_chart_data: List[Dict[str, Any]]  # structured data pulled from images

    # ---- final generation ----
    inferences: List[str]            # synthesized cross-agent inferences
    output_files: List[str]          # paths to generated pptx/docx

    # ---- bookkeeping ----
    errors: List[str]
