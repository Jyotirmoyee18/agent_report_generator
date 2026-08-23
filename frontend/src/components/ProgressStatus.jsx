const STAGES = [
  { key: "data_analysis_agent", label: "Data Analysis", note: "Computing KPIs" },
  { key: "document_vision_agent", label: "Document Vision", note: "Reading charts" },
  { key: "generation_agent", label: "Generation", note: "Building report" },
];

function stageState(stageKey, currentAgent, completedAgents, status) {
  if (completedAgents.includes(stageKey)) return "done";
  if (currentAgent === stageKey) return "active";
  if (status === "failed") return "idle";
  return "idle";
}

export default function ProgressStatus({ status, currentAgent, completedAgents }) {
  return (
    <div className="pipeline" role="status" aria-live="polite">
      <p className="pipeline__eyebrow">SUPERVISOR ROUTING</p>
      <div className="pipeline__track">
        {STAGES.map((stage, i) => {
          const state = stageState(stage.key, currentAgent, completedAgents, status);
          return (
            <div className="pipeline__stage" key={stage.key}>
              <div className={`pipeline__node pipeline__node--${state}`}>
                <span className="pipeline__node-index">{i + 1}</span>
              </div>
              <div className="pipeline__stage-text">
                <span className="pipeline__stage-label">{stage.label}</span>
                <span className="pipeline__stage-note">
                  {state === "active" ? stage.note : state === "done" ? "Complete" : "Waiting"}
                </span>
              </div>
              {i < STAGES.length - 1 && (
                <div
                  className={`pipeline__connector ${
                    state === "done" ? "pipeline__connector--filled" : ""
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
      {status === "failed" && (
        <p className="pipeline__error">Something went wrong — see details below.</p>
      )}
    </div>
  );
}
