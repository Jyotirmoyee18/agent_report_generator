import config
from orchestrator import build_graph
from state import ReportState


def main():
    graph = build_graph()

    initial_state: ReportState = {
        "request": "Generate a quarterly business report from regional sales data and the revenue chart.",
        "data_path": "sample_data/sales_data.csv",
        "chart_image_paths": ["sample_data/revenue_chart.png"],
        "output_template": "both",
        "completed_agents": [],
        "errors": [],
    }

    print(f"[mode] LLM: {'live (anthropic)' if config.USE_REAL_LLM else 'mock (offline)'}")
    print(f"[mode] Vision: {'live (azure)' if config.USE_REAL_AZURE_VISION else 'mock (offline)'}")
    print("[run] Starting graph...\n")

    final_state = graph.invoke(initial_state, config={"recursion_limit": 25})

    print("=== KPIs ===")
    for k, v in final_state.get("kpis", {}).items():
        print(f"  {k}: {v}")

    print("\n=== Data Findings ===")
    for f in final_state.get("data_findings", []):
        print(f"  - {f}")

    print("\n=== Vision Findings ===")
    for f in final_state.get("vision_findings", []):
        print(f"  - {f}")

    print("\n=== Inferences ===")
    for f in final_state.get("inferences", []):
        print(f"  - {f}")

    print("\n=== Output Files ===")
    for f in final_state.get("output_files", []):
        print(f"  - {f}")

    if final_state.get("errors"):
        print("\n=== Errors ===")
        for e in final_state["errors"]:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
