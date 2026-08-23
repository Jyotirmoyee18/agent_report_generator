import { getDownloadUrl } from "../api/reportApi.js";

const LABELS = {
  pptx: "Download PowerPoint",
  docx: "Download Word doc",
};

function extensionOf(filename) {
  return filename.split(".").pop().toLowerCase();
}

export default function DownloadButtons({ jobId, files }) {
  if (!files || files.length === 0) return null;

  return (
    <div className="download-row">
      {files.map((filename) => {
        const ext = extensionOf(filename);
        return (
          <a
            key={filename}
            className="download-button"
            href={getDownloadUrl(jobId, filename)}
            download={filename}
          >
            {LABELS[ext] || `Download ${filename}`}
          </a>
        );
      })}
    </div>
  );
}
