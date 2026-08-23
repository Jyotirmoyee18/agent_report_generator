import { useCallback, useEffect, useRef, useState } from "react";
import UploadForm from "./components/UploadForm.jsx";
import ProgressStatus from "./components/ProgressStatus.jsx";
import ResultsPanel from "./components/ResultsPanel.jsx";
import DownloadButtons from "./components/DownloadButtons.jsx";
import { generateReport, getJobStatus, ApiError } from "./api/reportApi.js";

const POLL_INTERVAL_MS = 1500;

export default function App() {
  const [jobId, setJobId] = useState(null);
  const [jobState, setJobState] = useState(null); // full status response
  const [phase, setPhase] = useState("idle"); // idle | submitting | running | complete | failed
  const [errorMessage, setErrorMessage] = useState("");
  const pollRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => () => stopPolling(), [stopPolling]);

  const pollJob = useCallback(
    (id) => {
      pollRef.current = setInterval(async () => {
        try {
          const status = await getJobStatus(id);
          setJobState(status);
          if (status.status === "complete") {
            setPhase("complete");
            stopPolling();
          } else if (status.status === "failed") {
            setPhase("failed");
            setErrorMessage(status.error || "The pipeline reported an error.");
            stopPolling();
          }
        } catch (err) {
          setPhase("failed");
          setErrorMessage(
            err instanceof ApiError
              ? err.message
              : "Lost connection to the server while checking progress."
          );
          stopPolling();
        }
      }, POLL_INTERVAL_MS);
    },
    [stopPolling]
  );

  const handleSubmit = async ({ dataFile, chartFiles, outputFormat }) => {
    setPhase("submitting");
    setErrorMessage("");
    setJobState(null);
    try {
      const { job_id } = await generateReport({ dataFile, chartFiles, outputFormat });
      setJobId(job_id);
      setPhase("running");
      pollJob(job_id);
    } catch (err) {
      setPhase("failed");
      setErrorMessage(
        err instanceof ApiError
          ? err.message
          : "Could not reach the server. Check that the backend is running."
      );
    }
  };

  const handleReset = () => {
    stopPolling();
    setJobId(null);
    setJobState(null);
    setPhase("idle");
    setErrorMessage("");
  };

  const isBusy = phase === "submitting" || phase === "running";

  return (
    <div className="page">
      <header className="page__header">
        <h1 className="page__title">Business Report Generator</h1>
      
      </header>

      <main className="page__main">
        {phase === "idle" || phase === "submitting" || phase === "failed" ? (
          <UploadForm onSubmit={handleSubmit} disabled={isBusy} />
        ) : null}

        {errorMessage && (
          <p className="page__error" role="alert">
            {errorMessage}
          </p>
        )}

        {(phase === "running" || phase === "complete" || phase === "failed") && jobId && (
          <ProgressStatus
            status={jobState?.status || "running"}
            currentAgent={jobState?.current_agent}
            completedAgents={jobState?.completed_agents || []}
          />
        )}

        {phase === "complete" && jobState && (
          <>
            <DownloadButtons jobId={jobId} files={jobState.output_files} />
            <ResultsPanel result={jobState} />
            <button className="secondary-button" onClick={handleReset}>
              Start a new report
            </button>
          </>
        )}

        {phase === "failed" && (
          <button className="secondary-button" onClick={handleReset}>
            Try again
          </button>
        )}
      </main>
    </div>
  );
}
