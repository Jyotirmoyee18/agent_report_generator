const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  return res.json();
}

/**
 * Kicks off report generation. Returns { job_id }.
 * dataFile: File (CSV) — optional if chartFiles provided
 * chartFiles: File[] — optional if dataFile provided
 * outputFormat: "pptx" | "docx" | "both"
 */
export async function generateReport({ dataFile, chartFiles, outputFormat }) {
  const form = new FormData();
  if (dataFile) form.append("data_file", dataFile);
  (chartFiles || []).forEach((file) => form.append("chart_files", file));
  form.append("output_format", outputFormat);

  const res = await fetch(`${BASE_URL}/generate-report`, {
    method: "POST",
    body: form,
  });
  return handleResponse(res);
}

/**
 * Polls job status. Returns:
 * { status: "queued"|"running"|"complete"|"failed",
 *   current_agent, completed_agents, kpis, data_findings,
 *   vision_findings, inferences, output_files, error }
 */
export async function getJobStatus(jobId) {
  const res = await fetch(`${BASE_URL}/jobs/${jobId}`);
  return handleResponse(res);
}

/** Returns a same-origin download URL for a completed job's output file. */
export function getDownloadUrl(jobId, filename) {
  return `${BASE_URL}/download/${jobId}/${filename}`;
}

export { ApiError };
