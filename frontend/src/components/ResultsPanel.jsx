function KpiGrid({ kpis }) {
  if (!kpis || Object.keys(kpis).length === 0) return null;
  const entries = Object.entries(kpis).filter(
    ([, v]) => typeof v !== "object"
  );
  return (
    <div className="kpi-grid">
      {entries.map(([label, value]) => (
        <div className="kpi-card" key={label}>
          <span className="kpi-card__value">{String(value)}</span>
          <span className="kpi-card__label">{label.replaceAll("_", " ")}</span>
        </div>
      ))}
    </div>
  );
}

function FindingsList({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="findings-block">
      <h3 className="findings-block__title">{title}</h3>
      <ul className="findings-block__list">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ResultsPanel({ result }) {
  if (!result) return null;
  const { kpis, data_findings, vision_findings, inferences } = result;

  return (
    <section className="results-panel" aria-label="Report results">
      <KpiGrid kpis={kpis} />
      <FindingsList title="Data findings" items={data_findings} />
      <FindingsList title="Chart & document findings" items={vision_findings} />
      <FindingsList title="Inferences & recommendations" items={inferences} />
    </section>
  );
}
