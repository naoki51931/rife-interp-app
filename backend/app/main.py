from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from pathlib import Path
import shutil

from settings import settings
from rife_worker import RIFEWorker

app = FastAPI(title="RIFE Interpolation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

worker = RIFEWorker()

JOBS = {}
STORAGE = Path(settings.storage)
STORAGE.mkdir(parents=True, exist_ok=True)


class JobStatus(BaseModel):
    id: str
    status: str
    kind: str
    output_url: Optional[str] = None
    frames_url: Optional[str] = None   # 🆕 中間フレーム用URL
    error: Optional[str] = None


def save_upload(upload: UploadFile, dst: Path) -> Path:
    with dst.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dst


@app.post("/api/interpolate/video", response_model=JobStatus)
async def interpolate_video(
    file: UploadFile = File(...),
    exp: int = Form(2),
    fps: Optional[int] = Form(None),
    scale: int = Form(1)
):
    job_id = uuid4().hex
    in_path = STORAGE / f"{job_id}_in.mp4"
    out_path = STORAGE / f"{job_id}_out.mp4"
    save_upload(file, in_path)

    JOBS[job_id] = JobStatus(id=job_id, status="running", kind="video")

    try:
        worker.interpolate_video(in_path, out_path, exp=exp, fps=fps, scale=scale)
        JOBS[job_id].status = "done"
        JOBS[job_id].output_url = f"/api/download/{job_id}"
    except Exception as e:
        JOBS[job_id].status = "error"
        JOBS[job_id].error = str(e)
    finally:
        pass

    return JOBS[job_id]


@app.post("/api/interpolate/frames", response_model=JobStatus)
async def interpolate_frames(
    frame_a: UploadFile = File(...),
    frame_b: UploadFile = File(...),
    num_mid: int = Form(6),
    fps: int = Form(30)
):
    job_id = uuid4().hex
    a_path = STORAGE / f"{job_id}_a.png"
    b_path = STORAGE / f"{job_id}_b.png"
    out_path = STORAGE / f"{job_id}_seq.mp4"

    save_upload(frame_a, a_path)
    save_upload(frame_b, b_path)

    JOBS[job_id] = JobStatus(id=job_id, status="running", kind="frames")

    try:
        worker.interpolate_two_frames(a_path, b_path, out_path, num_mid=num_mid, fps=fps)

        JOBS[job_id].status = "done"

        # 🎬 MP4ダウンロード用
        JOBS[job_id].output_url = f"/api/download/{job_id}"

        # 🖼️ PNG中間フレーム用
        frames_folder = Path(f"/data/{job_id}_seq_frames/output")
        if frames_folder.exists():
            JOBS[job_id].frames_url = f"/data/{job_id}_seq_frames/output/"
        else:
            JOBS[job_id].frames_url = None

    except Exception as e:
        JOBS[job_id].status = "error"
        JOBS[job_id].error = str(e)

    return JOBS[job_id]


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"detail": "job not found"})
    return job


@app.get("/api/download/{job_id}")
async def download(job_id: str):
    out = STORAGE / f"{job_id}_out.mp4"
    if not out.exists():
        out = STORAGE / f"{job_id}_seq.mp4"
    if not out.exists():
        return JSONResponse(status_code=404, content={"detail": "file not found"})
    return FileResponse(str(out), media_type="video/mp4", filename=out.name)


@app.get("/api/download_frames/{job_id}")
def download_frames(job_id: str):
    folder = Path(f"/data/{job_id}_seq_frames/output")
    zip_path = folder.parent / f"{job_id}_frames.zip"
    shutil.make_archive(zip_path.with_suffix(""), 'zip', folder)
    return FileResponse(zip_path, filename=f"{job_id}_frames.zip")

