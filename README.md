# Multi-Agent Business Report Generator

A LangGraph multi-agent system that takes structured data + chart images and
produces a fully generated PPTX and/or Word report — KPIs, findings, and
synthesized inferences, auto-populated into the output template.

## Architecture

```
START -> supervisor -> data_analysis_agent   -> back to supervisor
                     -> document_vision_agent -> back to supervisor
                     -> generation_agent      -> back to supervisor
                     -> END
```

The **supervisor** is a real routing node, not a fixed pipeline: it inspects
shared state after every step (which inputs exist, which agents have already
run) and decides what runs next. Skip the chart images and the vision agent
never fires. Skip the CSV and the data agent never fires.

- **`data_analysis_agent`** — deterministic KPI computation with pandas
  (never left to the LLM to "calculate"), then asks the LLM to narrate the
  numbers into plain-language findings. Same deterministic-lookup +
  LLM-reasoning split as an ERP reconciliation pipeline.
- **`document_vision_agent`** — pluggable vision backend. Uses Azure AI
  Document Intelligence when credentials are set; otherwise falls back to a
  local heuristic so the graph still runs offline.
- **`generation_agent`** — synthesizes cross-agent inferences, then renders
  `outputs/report.pptx` (python-pptx) and `outputs/report.docx`
  (python-docx). This is the only agent that touches the output document.

# How to run it:
# terminal 1
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000

# terminal 2
cd frontend && npm install && npm run dev


## Project layout

```
agent_report_generator/
├── main.py                    # entry point, runs the graph end to end
├── orchestrator.py            # LangGraph StateGraph + supervisor routing
├── state.py                   # shared state schema (TypedDict)
├── config.py                  # env-driven mock/live switching
├── agents/
│   ├── data_analysis_agent.py
│   ├── vision_agent.py
│   └── generation_agent.py
├── tools/
│   ├── llm_client.py          # Anthropic call + offline mock
│   ├── pptx_builder.py
│   └── docx_builder.py
├── sample_data/
│   ├── sales_data.csv
│   └── revenue_chart.png
└── outputs/                    # report.pptx / report.docx land here
```
