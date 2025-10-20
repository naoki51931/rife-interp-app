import os
import subprocess
from pathlib import Path

FFMPEG = "ffmpeg"


def ensure_dir(p: str | Path):
    Path(p).mkdir(parents=True, exist_ok=True)


def encode_video_from_frames(frames_dir: Path, out_path: Path, fps: int = 30) -> None:
    ensure_dir(out_path.parent)
    cmd = [
        FFMPEG, "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "%06d.png"),
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


def extract_frames(input_video: Path, out_dir: Path) -> int:
    ensure_dir(out_dir)
    cmd = [FFMPEG, "-y", "-i", str(input_video), str(out_dir / "%06d.png")]
    subprocess.run(cmd, check=True)
    return len(list(out_dir.glob("*.png")))