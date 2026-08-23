from __future__ import annotations
import os
import shutil
import threading
import uuid
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend import jobs

router = APIRouter()

ALLOWED_FORMATS = {"pptx", "docx", "both"}
MAX_UPLOAD_MB = 15


def _save_upload(upload: UploadFile, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    safe_name = os.path.basename(upload.filename)
    dest_path = os.path.join(dest_dir, safe_name)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest_path


@router.post("/generate-report", status_code=202)
async def generate_report(
    data_file: Optional[UploadFile] = File(None),
    chart_files: List[UploadFile] = File(default=[]),
    output_format: str = Form("both"),
):
    if output_format not in ALLOWED_FORMATS:
        raise HTTPException(400, f"output_format must be one of {sorted(ALLOWED_FORMATS)}")
    if not data_file and not chart_files:
        raise HTTPException(400, "Provide a data_file, chart_files, or both.")

    job_id = uuid.uuid4().hex[:12]
    job_root = jobs.job_dir(job_id)
    uploads_dir = os.path.join(job_root, "uploads")
    output_dir = os.path.join(job_root, "outputs")

    data_path = None
    if data_file is not None:
        if not data_file.filename.lower().endswith(".csv"):
            raise HTTPException(400, "data_file must be a .csv file")
        data_path = _save_upload(data_file, uploads_dir)

    chart_paths = []
    for chart in chart_files:
        if not (chart.content_type or "").startswith("image/"):
            raise HTTPException(400, f"{chart.filename} is not an image file")
        chart_paths.append(_save_upload(chart, uploads_dir))

    jobs.create_job(job_id)

    initial_state = {
        "request": "Generate a business report from the uploaded data and charts.",
        "data_path": data_path,
        "chart_image_paths": chart_paths,
        "output_template": output_format,
        "output_dir": output_dir,
        "completed_agents": [],
        "errors": [],
    }

    thread = threading.Thread(target=jobs.run_job, args=(job_id, initial_state), daemon=True)
    thread.start()

    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "Unknown job_id")
    return job


@router.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "Unknown job_id")

    safe_name = os.path.basename(filename)  # block path traversal
    if safe_name not in job.get("output_files", []):
        raise HTTPException(404, "File not found for this job")

    file_path = os.path.join(jobs.job_dir(job_id), "outputs", safe_name)
    if not os.path.isfile(file_path):
        raise HTTPException(404, "File not found on disk")

    media_types = {
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    ext = safe_name.rsplit(".", 1)[-1]
    return FileResponse(
        file_path,
        media_type=media_types.get(ext, "application/octet-stream"),
        filename=safe_name,
    )
