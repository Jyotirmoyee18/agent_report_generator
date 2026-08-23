import { useState, useRef, useCallback } from "react";

const FORMATS = [
  { value: "pptx", label: "PowerPoint" },
  { value: "docx", label: "Word" },
  { value: "both", label: "Both" },
];

export default function UploadForm({ onSubmit, disabled }) {
  const [dataFile, setDataFile] = useState(null);
  const [chartFiles, setChartFiles] = useState([]);
  const [outputFormat, setOutputFormat] = useState("both");
  const [isDragging, setIsDragging] = useState(false);
  const [formError, setFormError] = useState("");
  const dataInputRef = useRef(null);
  const chartInputRef = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    const csv = files.find((f) => f.name.toLowerCase().endsWith(".csv"));
    const images = files.filter((f) => f.type.startsWith("image/"));
    if (csv) setDataFile(csv);
    if (images.length) setChartFiles((prev) => [...prev, ...images]);
  }, []);

  const removeChartFile = (index) => {
    setChartFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!dataFile && chartFiles.length === 0) {
      setFormError("Add a data file, at least one chart image, or both.");
      return;
    }
    setFormError("");
    onSubmit({ dataFile, chartFiles, outputFormat });
  };

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <div
        className={`dropzone ${isDragging ? "dropzone--active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <p className="dropzone__label">Drop files here, or choose them below</p>

        <div className="dropzone__row">
          <button
            type="button"
            className="file-chip-button"
            onClick={() => dataInputRef.current?.click()}
            disabled={disabled}
          >
            {dataFile ? "Replace data file" : "Choose data file (.csv)"}
          </button>
          <input
            ref={dataInputRef}
            type="file"
            accept=".csv"
            hidden
            onChange={(e) => setDataFile(e.target.files[0] || null)}
          />
          {dataFile && (
            <span className="file-chip">
              {dataFile.name}
              <button
                type="button"
                className="file-chip__remove"
                aria-label={`Remove ${dataFile.name}`}
                onClick={() => setDataFile(null)}
              >
                ×
              </button>
            </span>
          )}
        </div>

        <div className="dropzone__row">
          <button
            type="button"
            className="file-chip-button"
            onClick={() => chartInputRef.current?.click()}
            disabled={disabled}
          >
            Add chart images
          </button>
          <input
            ref={chartInputRef}
            type="file"
            accept="image/*"
            multiple
            hidden
            onChange={(e) =>
              setChartFiles((prev) => [...prev, ...Array.from(e.target.files)])
            }
          />
          {chartFiles.map((file, i) => (
            <span className="file-chip" key={`${file.name}-${i}`}>
              {file.name}
              <button
                type="button"
                className="file-chip__remove"
                aria-label={`Remove ${file.name}`}
                onClick={() => removeChartFile(i)}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <fieldset className="format-select">
        <legend>Output format</legend>
        <div className="format-select__options">
          {FORMATS.map((f) => (
            <label
              key={f.value}
              className={`format-option ${outputFormat === f.value ? "format-option--selected" : ""}`}
            >
              <input
                type="radio"
                name="outputFormat"
                value={f.value}
                checked={outputFormat === f.value}
                onChange={() => setOutputFormat(f.value)}
              />
              {f.label}
            </label>
          ))}
        </div>
      </fieldset>

      {formError && (
        <p className="form-error" role="alert">
          {formError}
        </p>
      )}

      <button type="submit" className="primary-button" disabled={disabled}>
        {disabled ? "Generating…" : "Generate report"}
      </button>
    </form>
  );
}
