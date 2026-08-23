
from __future__ import annotations
import pandas as pd

from state import ReportState
from tools.llm_client import complete


def _compute_kpis(df: pd.DataFrame) -> dict:
    by_region = df.groupby("region").agg(
        total_revenue=("revenue", "sum"),
        total_units=("units_sold", "sum"),
        total_new_customers=("new_customers", "sum"),
        total_churned=("churned_customers", "sum"),
    )
    by_region["net_customer_growth"] = (
        by_region["total_new_customers"] - by_region["total_churned"]
    )

    by_quarter = df.groupby("quarter")["revenue"].sum()
    q1, q4 = by_quarter.get("Q1"), by_quarter.get("Q4")
    qoq_growth_pct = round(((q4 - q1) / q1) * 100, 1) if q1 else None

    return {
        "total_revenue": int(df["revenue"].sum()),
        "total_units_sold": int(df["units_sold"].sum()),
        "revenue_by_region": by_region["total_revenue"].to_dict(),
        "net_customer_growth_by_region": by_region["net_customer_growth"].to_dict(),
        "q1_to_q4_revenue_growth_pct": qoq_growth_pct,
        "top_region_by_revenue": by_region["total_revenue"].idxmax(),
        "top_region_by_net_growth": by_region["net_customer_growth"].idxmax(),
    }


def run(state: ReportState) -> dict:
    data_path = state.get("data_path")
    if not data_path:
        return {"errors": state.get("errors", []) + ["data_analysis_agent: no data_path in state"]}

    df = pd.read_csv(data_path)
    kpis = _compute_kpis(df)

    prompt = (
        "Here are KPIs computed from a company's regional sales data:\n"
        f"{kpis}\n\n"
        "Summarize the 3 most important findings for a business audience, "
        "as a short bullet list. Be specific and reference numbers."
    )
    findings_text = complete(
        system="You summarize business KPI data into concise, factual findings.",
        prompt=prompt,
    )
    findings = [line.strip("- ").strip() for line in findings_text.splitlines() if line.strip()]

    return {
        "kpis": kpis,
        "data_findings": findings,
        "completed_agents": state.get("completed_agents", []) + ["data_analysis_agent"],
    }
