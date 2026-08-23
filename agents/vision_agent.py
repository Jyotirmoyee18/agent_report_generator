"""
Document Vision Agent

Responsibility: analyze chart/report images and extract structured data +
descriptive findings from them. Backed by Azure AI Document Intelligence
when credentials are configured; otherwise falls back to a lightweight
local heuristic (image metadata + filename-based description) so the graph
still runs end-to-end offline.

Swapping in real Azure Document Intelligence:
    pip install azure-ai-documentintelligence
    set AZURE_DOC_INTEL_ENDPOINT and AZURE_DOC_INTEL_KEY
    -> _analyze_with_azure() below becomes the active path automatically.
"""
from __future__ import annotations
import os
from PIL import Image

import config
from state import ReportState
from tools.llm_client import complete


def _analyze_with_azure(image_path: str) -> dict:
    """Real Azure AI Document Intelligence call (prebuilt-layout model)."""
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    client = DocumentIntelligenceClient(
        endpoint=config.AZURE_DOC_INTEL_ENDPOINT,
        credential=AzureKeyCredential(config.AZURE_DOC_INTEL_KEY),
    )
    with open(image_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", body=f)
    result = poller.result()

    text_lines = []
    for page in result.pages:
        for line in page.lines:
            text_lines.append(line.content)

    return {
        "source": "azure_document_intelligence",
        "raw_text_lines": text_lines,
        "page_count": len(result.pages),
    }


def _analyze_with_mock(image_path: str) -> dict:
    """Offline fallback: basic image inspection + filename-based heuristic."""
    with Image.open(image_path) as img:
        width, height = img.size
        mode = img.mode

    filename = os.path.basename(image_path)
    return {
        "source": "mock_local_analysis",
        "filename": filename,
        "dimensions": f"{width}x{height}",
        "color_mode": mode,
        "raw_text_lines": [
            "[mock extraction] Revenue by Region and Quarter",
            "[mock extraction] Series: North America, EMEA, APAC",
            "[mock extraction] Axis: Q1-Q4, Revenue (USD)",
        ],
    }


def run(state: ReportState) -> dict:
    image_paths = state.get("chart_image_paths", [])
    if not image_paths:
        return {
            "vision_findings": [],
            "extracted_chart_data": [],
            "completed_agents": state.get("completed_agents", []) + ["document_vision_agent"],
        }

    extracted = []
    for path in image_paths:
        if config.USE_REAL_AZURE_VISION:
            extracted.append(_analyze_with_azure(path))
        else:
            extracted.append(_analyze_with_mock(path))

    prompt = (
        "The following data was extracted from chart images in a business report:\n"
        f"{extracted}\n\n"
        "Write 1-2 short bullet points describing what these charts show, in "
        "plain business language."
    )
    findings_text = complete(
        system="You describe extracted chart/document content for a business report.",
        prompt=prompt,
    )
    findings = [line.strip("- ").strip() for line in findings_text.splitlines() if line.strip()]

    return {
        "vision_findings": findings,
        "extracted_chart_data": extracted,
        "completed_agents": state.get("completed_agents", []) + ["document_vision_agent"],
    }
